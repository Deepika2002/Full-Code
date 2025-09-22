from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import openai
from datetime import datetime

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.utils import setup_logging, generate_request_id, verify_api_key, create_error_response, create_success_response
from shared.config import settings
from services.ai_analysis_service import AIAnalysisService

# Setup
app = FastAPI(title="MS-AI", description="AI Analysis Service", version="1.0.0")
logger = setup_logging("MS-AI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
ai_analysis_service = AIAnalysisService()

# Models
class ImpactAnalysisRequest(BaseModel):
    mrId: str
    changedClasses: List[str]
    codeContext: str
    vectorContext: Optional[Dict[str, Any]] = None

class TestCoverageRequest(BaseModel):
    day: str
    allMRs: List[Dict[str, Any]]

@app.on_startup
async def startup_event():
    """Initialize AI service on startup"""
    ai_analysis_service.initialize()
    logger.info("MS-AI service started successfully")

@app.post("/analysis/impact")
async def analyze_impact(
    request: ImpactAnalysisRequest,
    _=Depends(verify_api_key)
):
    """Analyze impact of code changes using AI"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Analyzing impact for MR: {request.mrId}")
    
    try:
        analysis_result = await ai_analysis_service.analyze_impact(
            request.mrId,
            request.changedClasses,
            request.codeContext,
            request.vectorContext,
            request_id
        )
        
        return create_success_response({
            "analysis": analysis_result
        }, "Impact analysis completed successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error analyzing impact: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to analyze impact",
            {"error": str(e), "requestId": request_id}
        ))

@app.post("/analysis/test-coverage")
async def analyze_test_coverage(
    request: TestCoverageRequest,
    _=Depends(verify_api_key)
):
    """Analyze test coverage for a day"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Analyzing test coverage for day: {request.day}")
    
    try:
        coverage_report = await ai_analysis_service.analyze_test_coverage(
            request.day,
            request.allMRs,
            request_id
        )
        
        return create_success_response({
            "coverageReport": coverage_report
        }, "Test coverage analysis completed successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error analyzing test coverage: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to analyze test coverage",
            {"error": str(e), "requestId": request_id}
        ))

@app.get("/ai/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MS-AI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)