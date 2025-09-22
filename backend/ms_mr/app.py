from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import requests
from datetime import datetime

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import get_db, create_tables
from shared.models import MRTable, ChangedClassNames
from shared.utils import setup_logging, generate_request_id, verify_api_key, create_error_response, create_success_response
from shared.config import settings
from services.mr_analysis_service import MRAnalysisService

# Setup
app = FastAPI(title="MS-MR", description="Merge Request Analysis Service", version="1.0.0")
logger = setup_logging("MS-MR")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
mr_analysis_service = MRAnalysisService()

# Models
class ChangedFile(BaseModel):
    path: str
    oldPath: Optional[str] = None
    newPath: Optional[str] = None
    type: str  # MODIFY, ADD, DELETE

class RepositoryInfo(BaseModel):
    repoUrl: str
    branch: str
    commitHash: str

class AnalyzeMRRequest(BaseModel):
    projectId: str
    mrId: str
    author: str
    timestamp: str
    gitDiff: str
    changedFiles: List[ChangedFile]
    repositoryInfo: RepositoryInfo

@app.on_startup
async def startup_event():
    """Initialize database and services on startup"""
    create_tables()
    logger.info("MS-MR service started successfully")

@app.post("/mr/analyze")
async def analyze_mr(
    request: AnalyzeMRRequest,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Analyze merge request for impact"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Analyzing MR: {request.mrId} for project: {request.projectId}")
    
    try:
        # Check if MR already exists
        existing_mr = db.query(MRTable).filter(MRTable.mrID == request.mrId).first()
        if existing_mr:
            logger.info(f"[{request_id}] MR {request.mrId} already analyzed, updating...")
        
        # Analyze the MR using AI service
        analysis_result = await mr_analysis_service.analyze_mr_impact(request, request_id)
        
        # Create or update MR record
        if existing_mr:
            mr_record = existing_mr
            # Clear existing changed classes
            db.query(ChangedClassNames).filter(ChangedClassNames.mrID == request.mrId).delete()
        else:
            mr_record = MRTable(mrID=request.mrId)
            db.add(mr_record)
        
        # Update MR record
        mr_record.author = request.author
        mr_record.timestamp = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        mr_record.projectId = request.projectId
        mr_record.gitDiff = request.gitDiff
        mr_record.analysisId = analysis_result['analysisId']
        mr_record.totalUnitTestCoverage = analysis_result['analysis']['codeCoverage']
        mr_record.SeverityScore = analysis_result['analysis']['severityScore']
        mr_record.TestExecutedIDs = [flow['id'] for flow in analysis_result['analysis']['testFlows']]
        mr_record.description = analysis_result['analysis']['summary']
        
        # Store changed class names
        changed_classes = []
        for affected_class in analysis_result['analysis']['affectedClasses']:
            changed_class = ChangedClassNames(
                mrID=request.mrId,
                className=affected_class['name'],
                severity=affected_class['severity'],
                reason=affected_class['reason']
            )
            changed_classes.append(changed_class.className)
            db.add(changed_class)
        
        mr_record.CommaSeparatedChangedClassNames = ','.join(changed_classes)
        
        db.commit()
        
        logger.info(f"[{request_id}] Successfully analyzed MR: {request.mrId}")
        
        return create_success_response({
            "analysisId": analysis_result['analysisId'],
            "mrSummary": {
                "mrId": request.mrId,
                "severityScore": analysis_result['analysis']['severityScore'],
                "affectedClassesCount": len(analysis_result['analysis']['affectedClasses']),
                "testFlowsCount": len(analysis_result['analysis']['testFlows']),
                "codeCoverage": analysis_result['analysis']['codeCoverage']
            },
            "details": analysis_result['analysis']
        }, "MR analyzed successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error analyzing MR: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to analyze MR",
            {"error": str(e), "requestId": request_id}
        ))

@app.get("/mr/{mr_id}/analysis")
async def get_mr_analysis(
    mr_id: str,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Get analysis results for a specific MR"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Getting analysis for MR: {mr_id}")
    
    try:
        # Get MR record
        mr_record = db.query(MRTable).filter(MRTable.mrID == mr_id).first()
        if not mr_record:
            raise HTTPException(status_code=404, detail="MR not found")
        
        # Get changed classes
        changed_classes = db.query(ChangedClassNames).filter(
            ChangedClassNames.mrID == mr_id
        ).all()
        
        analysis_data = {
            "mrId": mr_record.mrID,
            "author": mr_record.author,
            "timestamp": mr_record.timestamp.isoformat(),
            "severityScore": mr_record.SeverityScore,
            "codeCoverage": mr_record.totalUnitTestCoverage,
            "summary": mr_record.description,
            "affectedClasses": [
                {
                    "name": cc.className,
                    "severity": cc.severity,
                    "reason": cc.reason
                }
                for cc in changed_classes
            ],
            "testFlowIds": mr_record.TestExecutedIDs or []
        }
        
        return create_success_response({
            "analysis": analysis_data
        }, "Analysis retrieved successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error getting MR analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to get MR analysis",
            {"error": str(e), "requestId": request_id}
        ))

@app.get("/mr/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MS-MR"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)