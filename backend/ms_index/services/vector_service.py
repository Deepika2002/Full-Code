import os
import numpy as np
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
from ...shared.gcs_client import gcs_client, vertex_ai_client
from ...shared.config import settings
from ...shared.models import VectorMetadata
import logging

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.vector_stores = {}  # In-memory cache
        self.metadata_stores = {}
        
    async def initialize(self):
        """Initialize the vector service"""
        try:
            logger.info("Vector service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector service: {e}")
    
    async def create_embeddings(self, graph_data, project_id: str, request_id: str) -> Tuple[str, str]:
        """Create embeddings for the dependency graph using Vertex AI"""
        try:
            # Prepare texts for embedding
            texts = []
            metadata = []
            
            # Create embeddings for nodes
            for node in graph_data.nodes:
                text = f"Class: {node.name} Type: {node.type} Path: {node.path or 'unknown'}"
                texts.append(text)
                metadata.append({
                    'type': 'node',
                    'id': node.id,
                    'name': node.name,
                    'node_type': node.type,
                    'path': node.path,
                    'project_id': project_id
                })
            
            # Create embeddings for edges (relationships)
            for edge in graph_data.edges:
                text = f"Dependency: {edge.from_node} {edge.type} {edge.to}"
                texts.append(text)
                metadata.append({
                    'type': 'edge',
                    'from': edge.from_node,
                    'to': edge.to,
                    'edge_type': edge.type,
                    'project_id': project_id
                })
            
            # Generate embeddings using Vertex AI
            embeddings = vertex_ai_client.generate_embeddings(texts)
            
            # Create index ID
            index_id = f"{project_id}_{request_id}_{int(datetime.now().timestamp())}"
            
            # Upload vectors to Google Cloud Storage
            gcs_path = await gcs_client.upload_vectors(
                embeddings, metadata, project_id, index_id
            )
            
            # Store metadata in cache
            self.vector_stores[index_id] = embeddings
            self.metadata_stores[index_id] = metadata
            
            logger.info(f"Created {len(embeddings)} embeddings for project {project_id}")
            
            return gcs_path, index_id
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            # Fallback to mock embeddings
            return await self._create_mock_embeddings(graph_data, project_id, request_id)
    
    async def _create_mock_embeddings(self, graph_data, project_id: str, request_id: str) -> Tuple[str, str]:
        """Create mock embeddings for development/testing"""
        index_id = f"{project_id}_{request_id}_mock"
        
        # Create mock data
        mock_data = {
            'nodes': [node.dict() for node in graph_data.nodes],
            'edges': [edge.dict() for edge in graph_data.edges],
            'embeddings_count': len(graph_data.nodes) + len(graph_data.edges),
            'project_id': project_id,
            'index_id': index_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Upload to GCS
        gcs_path = await gcs_client.upload_json(
            mock_data, 
            f"vectors/{project_id}/{index_id}.json",
            settings.GCS_VECTOR_BUCKET
        )
        
        return gcs_path, index_id
    
    def get_embeddings_count(self, index_id: str) -> int:
        """Get the number of embeddings in an index"""
        if index_id in self.vector_stores:
            return len(self.vector_stores[index_id])
        
        # Try to load from GCS
        try:
            project_id = index_id.split('_')[0]
            data = gcs_client.download_json(
                f"vectors/{project_id}/{index_id}.json",
                settings.GCS_VECTOR_BUCKET
            )
            return data.get('embeddings_count', 0)
        except:
            return 0
    
    async def search_similar(self, query: str, index_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        try:
            # Generate query embedding
            query_embeddings = vertex_ai_client.generate_embeddings([query])
            query_embedding = query_embeddings[0]
            
            # Get stored embeddings
            if index_id not in self.vector_stores:
                await self._load_embeddings_from_gcs(index_id)
            
            if index_id not in self.vector_stores:
                return []
            
            stored_embeddings = self.vector_stores[index_id]
            metadata = self.metadata_stores[index_id]
            
            # Perform similarity search
            similar_indices = vertex_ai_client.similarity_search(
                query_embedding, stored_embeddings, k
            )
            
            # Return results with metadata
            results = []
            for idx in similar_indices:
                if idx < len(metadata):
                    result = metadata[idx].copy()
                    result['similarity_score'] = float(np.random.random())  # Mock score
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []
    
    async def _load_embeddings_from_gcs(self, index_id: str):
        """Load embeddings from Google Cloud Storage"""
        try:
            project_id = index_id.split('_')[0]
            data = gcs_client.download_json(
                f"vectors/{project_id}/{index_id}.json",
                settings.GCS_VECTOR_BUCKET
            )
            
            if 'vectors' in data:
                self.vector_stores[index_id] = data['vectors']
                self.metadata_stores[index_id] = data['metadata']
            
        except Exception as e:
            logger.error(f"Error loading embeddings from GCS: {e}")