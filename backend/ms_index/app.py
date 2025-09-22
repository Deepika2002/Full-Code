from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import git
import shutil
import json
from datetime import datetime

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import get_db, create_tables, init_sample_data
from shared.models import DependencyGraph, VectorMetadata
from shared.utils import setup_logging, generate_request_id, verify_api_key, create_error_response, create_success_response
from shared.config import settings
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

class DependencyEdge(BaseModel):
    from_node: str = None
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
    vector_service.initialize()
    logger.info("MS-Index service started successfully")

@app.post("/index/ingest-graph")
async def ingest_graph(
    request: IngestGraphRequest,
    db=Depends(get_db),
    _=Depends(verify_api_key)
):
    """Ingest dependency graph and create embeddings"""
    request_id = generate_request_id()
    logger.info(f"[{request_id}] Ingesting graph for project: {request.projectId}")
    
    try:
        # Clone repository
        repo_path = await indexing_service.clone_repository(request.repoUrl, request.commitHash)
        
        # Parse code and build enhanced dependency graph
        enhanced_graph = await indexing_service.parse_code_structure(repo_path, request.dependencyGraph)
        
        # Generate embeddings
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
            indexId=index_id
        )
        
        db.add(dependency_graph)
        db.commit()
        
        # Cleanup temporary repo
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        
        logger.info(f"[{request_id}] Successfully processed graph for project: {request.projectId}")
        
        return create_success_response({
            "indexId": index_id,
            "vectorStorePath": vector_store_path,
            "metadata": {
                "projectId": request.projectId,
                "nodesCount": len(enhanced_graph.nodes),
                "edgesCount": len(enhanced_graph.edges),
                "embeddingsCount": vector_service.get_embeddings_count(index_id)
            }
        }, "Dependency graph ingested successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error ingesting graph: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to ingest dependency graph",
            {"error": str(e), "requestId": request_id}
        ))

@app.post("/index/rebuild-embeddings")
async def rebuild_embeddings(
    project_id: str,
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
        
        # Rebuild embeddings
        enhanced_graph = DependencyGraphData(**graph_record.graphData)
        vector_store_path, index_id = await vector_service.create_embeddings(
            enhanced_graph, project_id, request_id
        )
        
        # Update database
        graph_record.vectorStorePath = vector_store_path
        graph_record.indexId = index_id
        db.commit()
        
        logger.info(f"[{request_id}] Successfully rebuilt embeddings for project: {project_id}")
        
        return create_success_response({
            "indexId": index_id,
            "vectorStorePath": vector_store_path,
            "embeddingsCount": vector_service.get_embeddings_count(index_id)
        }, "Embeddings rebuilt successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error rebuilding embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=create_error_response(
            "Failed to rebuild embeddings",
            {"error": str(e), "requestId": request_id}
        ))

@app.get("/index/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MS-Index"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)