from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import subprocess
import asyncio
from datetime import datetime
import uuid

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import get_db, create_tables
from shared.models import TestFlowsTable, TestCaseResults, MRTable
from shared.utils import setup_logging, generate_request_id, verify_api_key, create_error_response, create_success_response
from shared.config import settings
from shared.gcs_client import gcs_client
from services.test_execution_service import TestExecutionService

# Setup
app = FastAPI(title="MS-TestCase", description="Test Case Execution Service", version="1.0.0")
logger = setup_logging("MS-TestCase")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
test_execution_service = TestExecutionService()

# Models
class ExecuteTestRequest(BaseModel):
    TestFlowId: str
    mrID: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = 300  # 5 minutes default

class TestExecutionStatus(BaseModel):
    executionId: str
    status: str
    progress: Optional[Dict[str, Any]] = None

@app.on_startup
async def startup_event():
    """Initialize database and services on startup"""
    create_tables()
    await test_execution_service.initialize()
    logger.info("MS-TestCase service started successfully")

@app.post("/testcase/execute")
async def execute_test(
    request: ExecuteTestRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Execute a test flow"""
    request_id = generate_request_id()
    execution_id = str(uuid.uuid4())
    
    logger.info(f"[{request_id}] Executing test flow: {request.TestFlowId}")
    
    try:
        # Get test flow details
        test_flow = db.query(TestFlowsTable).filter(
            TestFlowsTable.TestFlowId == request.TestFlowId
        ).first()
        
        if not test_flow:
            raise HTTPException(status_code=404, detail="Test flow not found")
        
        # Create test execution record
        test_result = TestCaseResults(
            TestFlowId=request.TestFlowId,
            mrID=request.mrID,
            executionId=execution_id,
            status="running",
            startTime=datetime.utcnow()
        )
        
        db.add(test_result)
        db.commit()
        
        # Update test flow status
        test_flow.status = "running"
        test_flow.lastRun = datetime.utcnow()
        db.commit()
        
        # Execute test in background
        background_tasks.add_task(
            execute_test_background,
            execution_id,
            test_flow,
            request.parameters or {},
            request.timeout,
            request_id
        )
        
        return create_success_response({
            "executionId": execution_id,
            "status": "running",
            "testFlowId": request.TestFlowId,
            "estimatedDuration": "2-5 minutes"
        }, "Test execution started successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error starting test execution: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to start test execution",
            {"error": str(e), "requestId": request_id}
        ))

async def execute_test_background(
    execution_id: str,
    test_flow: TestFlowsTable,
    parameters: Dict[str, Any],
    timeout: int,
    request_id: str
):
    """Background task to execute test"""
    db = next(get_db())
    
    try:
        logger.info(f"[{request_id}] Starting background test execution: {execution_id}")
        
        # Get test execution record
        test_result = db.query(TestCaseResults).filter(
            TestCaseResults.executionId == execution_id
        ).first()
        
        if not test_result:
            logger.error(f"[{request_id}] Test execution record not found: {execution_id}")
            return
        
        # Execute the test
        execution_result = await test_execution_service.execute_test(
            test_flow, parameters, timeout, request_id
        )
        
        # Update test result
        test_result.status = execution_result['status']
        test_result.endTime = datetime.utcnow()
        test_result.duration = (test_result.endTime - test_result.startTime).total_seconds()
        test_result.errorMessage = execution_result.get('error_message')
        test_result.logOutput = execution_result.get('log_output', '')
        
        # Upload logs to GCS
        if test_result.logOutput:
            gcs_log_path = await gcs_client.upload_logs(
                test_result.logOutput,
                test_flow.TestFlowId,
                execution_id
            )
            test_result.gcsLogPath = gcs_log_path
        
        # Update test flow
        test_flow.status = execution_result['status']
        test_flow.duration = f"{int(test_result.duration // 60)}m {int(test_result.duration % 60)}s"
        
        if execution_result['status'] == 'passed':
            test_flow.passedSteps = execution_result.get('passed_steps', test_flow.steps)
            test_flow.failedSteps = 0
        else:
            test_flow.passedSteps = execution_result.get('passed_steps', 0)
            test_flow.failedSteps = execution_result.get('failed_steps', 1)
        
        db.commit()
        
        logger.info(f"[{request_id}] Test execution completed: {execution_id} - {execution_result['status']}")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error in background test execution: {str(e)}")
        
        # Update test result with error
        test_result = db.query(TestCaseResults).filter(
            TestCaseResults.executionId == execution_id
        ).first()
        
        if test_result:
            test_result.status = "failed"
            test_result.endTime = datetime.utcnow()
            test_result.errorMessage = str(e)
            test_result.duration = (test_result.endTime - test_result.startTime).total_seconds()
            
            # Update test flow
            test_flow.status = "failed"
            test_flow.failedSteps = test_flow.steps
            test_flow.passedSteps = 0
            
            db.commit()
    
    finally:
        db.close()

@app.get("/testcase/status/{execution_id}")
async def get_execution_status(
    execution_id: str,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Get test execution status"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Getting execution status: {execution_id}")
    
    try:
        test_result = db.query(TestCaseResults).filter(
            TestCaseResults.executionId == execution_id
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Calculate progress
        progress = {}
        if test_result.status == "running":
            elapsed = (datetime.utcnow() - test_result.startTime).total_seconds()
            progress = {
                "elapsed_seconds": int(elapsed),
                "estimated_remaining": max(0, 180 - int(elapsed))  # Estimate 3 minutes
            }
        
        return create_success_response({
            "executionId": execution_id,
            "status": test_result.status,
            "startTime": test_result.startTime.isoformat() if test_result.startTime else None,
            "endTime": test_result.endTime.isoformat() if test_result.endTime else None,
            "duration": test_result.duration,
            "errorMessage": test_result.errorMessage,
            "gcsLogPath": test_result.gcsLogPath,
            "progress": progress
        }, "Execution status retrieved successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error getting execution status: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to get execution status",
            {"error": str(e), "requestId": request_id}
        ))

@app.get("/testcase/logs/{execution_id}")
async def get_execution_logs(
    execution_id: str,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Get test execution logs"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Getting execution logs: {execution_id}")
    
    try:
        test_result = db.query(TestCaseResults).filter(
            TestCaseResults.executionId == execution_id
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        logs = test_result.logOutput or "No logs available"
        
        return create_success_response({
            "executionId": execution_id,
            "logs": logs,
            "gcsLogPath": test_result.gcsLogPath
        }, "Execution logs retrieved successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error getting execution logs: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to get execution logs",
            {"error": str(e), "requestId": request_id}
        ))

@app.post("/testcase/stop/{execution_id}")
async def stop_execution(
    execution_id: str,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Stop a running test execution"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Stopping execution: {execution_id}")
    
    try:
        test_result = db.query(TestCaseResults).filter(
            TestCaseResults.executionId == execution_id
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        if test_result.status != "running":
            raise HTTPException(status_code=400, detail="Execution is not running")
        
        # Stop the execution
        await test_execution_service.stop_execution(execution_id)
        
        # Update status
        test_result.status = "stopped"
        test_result.endTime = datetime.utcnow()
        test_result.duration = (test_result.endTime - test_result.startTime).total_seconds()
        
        # Update test flow
        test_flow = db.query(TestFlowsTable).filter(
            TestFlowsTable.TestFlowId == test_result.TestFlowId
        ).first()
        
        if test_flow:
            test_flow.status = "stopped"
        
        db.commit()
        
        return create_success_response({
            "executionId": execution_id,
            "status": "stopped"
        }, "Execution stopped successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error stopping execution: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to stop execution",
            {"error": str(e), "requestId": request_id}
        ))

@app.get("/testcase/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MS-TestCase", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)