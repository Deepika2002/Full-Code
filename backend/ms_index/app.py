from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import git
import shutil
import json
from datetime import datetime, timedelta
import asyncio

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import get_db, create_tables, init_sample_data
from shared.models import DependencyGraph, VectorMetadata, DailyMetricsTable, TestFlowsTable
from shared.utils import setup_logging, generate_request_id, verify_api_key, create_error_response, create_success_response
from shared.config import settings
from shared.gcs_client import gcs_client, vertex_ai_client
from services.indexing_service import IndexingService
from services.vector_service import VectorService

# Setup
app = FastAPI(title="MS-Index", description="Dependency Graph Indexing Service", version="1.0.0")
logger = setup_logging("MS-Index")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
indexing_service = IndexingService()
vector_service = VectorService()

# Models
class DependencyNode(BaseModel):
    id: str
    name: str
    type: Optional[str] = "module"
    path: Optional[str] = None

class DependencyEdge(BaseModel):
    from_node: str
    to: str
    type: str = "depends-on"

class DependencyGraphData(BaseModel):
    nodes: List[DependencyNode]
    edges: List[DependencyEdge]

class IngestGraphRequest(BaseModel):
    projectId: str
    repoUrl: str
    commitHash: str
    timestamp: str
    author: Optional[str] = None
    dependencyGraph: DependencyGraphData

@app.on_startup
async def startup_event():
    """Initialize database and services on startup"""
    create_tables()
    init_sample_data()
    await vector_service.initialize()
    logger.info("MS-Index service started successfully")

@app.post("/index/ingest-graph")
async def ingest_graph(
    request: IngestGraphRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Ingest dependency graph and create embeddings"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Ingesting graph for project: {request.projectId}")
    
    try:
        # Process in background for better performance
        background_tasks.add_task(
            process_dependency_graph,
            request,
            request_id
        )
        
        return create_success_response({
            "requestId": request_id,
            "status": "processing",
            "message": "Dependency graph ingestion started"
        }, "Graph ingestion initiated successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error initiating graph ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to initiate graph ingestion",
            {"error": str(e), "requestId": request_id}
        ))

async def process_dependency_graph(request: IngestGraphRequest, request_id: str):
    """Background task to process dependency graph"""
    db = next(get_db())
    
    try:
        logger.info(f"[{request_id}] Starting background processing for project: {request.projectId}")
        
        # Clone repository
        repo_path = await indexing_service.clone_repository(request.repoUrl, request.commitHash)
        
        # Parse code and build enhanced dependency graph
        enhanced_graph = await indexing_service.parse_code_structure(repo_path, request.dependencyGraph)
        
        # Generate embeddings using Vertex AI
        vector_store_path, index_id = await vector_service.create_embeddings(
            enhanced_graph, request.projectId, request_id
        )
        
        # Store in database
        dependency_graph = DependencyGraph(
            projectId=request.projectId,
            repoUrl=request.repoUrl,
            commitHash=request.commitHash,
            timestamp=datetime.fromisoformat(request.timestamp.replace('Z', '+00:00')),
            author=request.author,
            graphData=enhanced_graph.dict(),
            vectorStorePath=vector_store_path,
            indexId=index_id,
            gcsVectorPath=vector_store_path
        )
        
        db.add(dependency_graph)
        db.commit()
        
        # Update daily metrics
        await update_daily_metrics(db, request.projectId)
        
        # Cleanup temporary repo
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        
        logger.info(f"[{request_id}] Successfully processed graph for project: {request.projectId}")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error processing dependency graph: {str(e)}")
    finally:
        db.close()

async def update_daily_metrics(db, project_id: str):
    """Update daily metrics after processing"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get or create daily metrics
        daily_metrics = db.query(DailyMetricsTable).filter(
            DailyMetricsTable.dayId == today
        ).first()
        
        if not daily_metrics:
            daily_metrics = DailyMetricsTable(dayId=today)
            db.add(daily_metrics)
        
        # Count total test cases for the project
        total_test_cases = db.query(TestFlowsTable).filter(
            TestFlowsTable.projectId == project_id
        ).count()
        
        daily_metrics.TotNoOfTestCases = total_test_cases
        daily_metrics.updatedAt = datetime.utcnow()
        
        db.commit()
        logger.info(f"Updated daily metrics for {today}")
        
    except Exception as e:
        logger.error(f"Error updating daily metrics: {e}")

@app.post("/index/rebuild-embeddings")
async def rebuild_embeddings(
    project_id: str,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Rebuild embeddings for a project"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Rebuilding embeddings for project: {project_id}")
    
    try:
        # Get existing graph data
        graph_record = db.query(DependencyGraph).filter(
            DependencyGraph.projectId == project_id
        ).order_by(DependencyGraph.timestamp.desc()).first()
        
        if not graph_record:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Process in background
        background_tasks.add_task(
            rebuild_embeddings_task,
            graph_record,
            request_id
        )
        
        return create_success_response({
            "requestId": request_id,
            "status": "processing",
            "projectId": project_id
        }, "Embeddings rebuild initiated successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error initiating embeddings rebuild: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to initiate embeddings rebuild",
            {"error": str(e), "requestId": request_id}
        ))

async def rebuild_embeddings_task(graph_record: DependencyGraph, request_id: str):
    """Background task to rebuild embeddings"""
    db = next(get_db())
    
    try:
        # Rebuild embeddings
        enhanced_graph = DependencyGraphData(**graph_record.graphData)
        vector_store_path, index_id = await vector_service.create_embeddings(
            enhanced_graph, graph_record.projectId, request_id
        )
        
        # Update database
        graph_record.vectorStorePath = vector_store_path
        graph_record.indexId = index_id
        graph_record.gcsVectorPath = vector_store_path
        graph_record.updatedAt = datetime.utcnow()
        db.commit()
        
        logger.info(f"[{request_id}] Successfully rebuilt embeddings for project: {graph_record.projectId}")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error rebuilding embeddings: {str(e)}")
    finally:
        db.close()

@app.post("/index/daily-refresh")
async def daily_refresh(
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Daily refresh of dependency graphs and metrics"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Starting daily refresh")
    
    try:
        # Get all projects that need refresh
        projects = db.query(DependencyGraph).distinct(DependencyGraph.projectId).all()
        
        for project in projects:
            background_tasks.add_task(
                refresh_project_data,
                project.projectId,
                request_id
            )
        
        return create_success_response({
            "requestId": request_id,
            "projectsCount": len(projects),
            "status": "processing"
        }, "Daily refresh initiated successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error initiating daily refresh: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to initiate daily refresh",
            {"error": str(e), "requestId": request_id}
        ))

async def refresh_project_data(project_id: str, request_id: str):
    """Refresh data for a specific project"""
    db = next(get_db())
    
    try:
        logger.info(f"[{request_id}] Refreshing data for project: {project_id}")
        
        # Get latest graph for project
        latest_graph = db.query(DependencyGraph).filter(
            DependencyGraph.projectId == project_id
        ).order_by(DependencyGraph.timestamp.desc()).first()
        
        if latest_graph:
            # Clone and re-analyze repository
            repo_path = await indexing_service.clone_repository(
                latest_graph.repoUrl, 
                "main"  # Use main branch for daily refresh
            )
            
            # Update metrics
            await update_daily_metrics(db, project_id)
            
            # Cleanup
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
        
        logger.info(f"[{request_id}] Successfully refreshed project: {project_id}")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error refreshing project {project_id}: {str(e)}")
    finally:
        db.close()

@app.get("/index/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MS-Index", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)