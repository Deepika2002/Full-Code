import os
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
import json
from ..app import DependencyGraphData

class VectorService:
    def __init__(self):
        self.model = None
        self.vector_stores = {}  # Store multiple FAISS indices
        self.metadata_stores = {}  # Store metadata for each index
        
    def initialize(self):
        """Initialize the sentence transformer model"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Vector service initialized successfully")
        except Exception as e:
            print(f"Error initializing vector service: {e}")
            # Fallback to a simple embedding service
            self.model = None
    
    async def create_embeddings(self, graph_data: DependencyGraphData, project_id: str, request_id: str) -> Tuple[str, str]:
        """Create embeddings for the dependency graph"""
        if not self.model:
            # Mock embeddings for development
            return self._create_mock_embeddings(graph_data, project_id, request_id)
        
        try:
            # Prepare texts for embedding
            texts = []
            metadata = []
            
            # Create embeddings for nodes
            for node in graph_data.nodes:
                text = f"Node: {node.name} Type: {node.type}"
                texts.append(text)
                metadata.append({
                    'type': 'node',
                    'id': node.id,
                    'name': node.name,
                    'node_type': node.type,
                    'project_id': project_id
                })
            
            # Create embeddings for edges (relationships)
            for edge in graph_data.edges:
                text = f"Relationship: {edge.from_node} {edge.type} {edge.to}"
                texts.append(text)
                metadata.append({
                    'type': 'edge',
                    'from': edge.from_node,
                    'to': edge.to,
                    'edge_type': edge.type,
                    'project_id': project_id
                })
            
            # Generate embeddings
            embeddings = self.model.encode(texts)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype('float32'))
            
            # Save index and metadata
            index_id = f"{project_id}_{request_id}"
            vector_store_path = os.path.join("./vector_store", f"{index_id}.faiss")
            metadata_path = os.path.join("./vector_store", f"{index_id}_metadata.pkl")
            
            # Ensure directory exists
            os.makedirs("./vector_store", exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(index, vector_store_path)
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            # Store in memory for quick access
            self.vector_stores[index_id] = index
            self.metadata_stores[index_id] = metadata
            
            return vector_store_path, index_id
            
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            return self._create_mock_embeddings(graph_data, project_id, request_id)
    
    def _create_mock_embeddings(self, graph_data: DependencyGraphData, project_id: str, request_id: str) -> Tuple[str, str]:
        """Create mock embeddings for development/testing"""
        index_id = f"{project_id}_{request_id}"
        vector_store_path = os.path.join("./vector_store", f"{index_id}_mock.json")
        
        # Ensure directory exists
        os.makedirs("./vector_store", exist_ok=True)
        
        # Create mock data
        mock_data = {
            'nodes': [node.dict() for node in graph_data.nodes],
            'edges': [edge.dict() for edge in graph_data.edges],
            'embeddings_count': len(graph_data.nodes) + len(graph_data.edges),
            'project_id': project_id,
            'index_id': index_id
        }
        
        # Save mock data
        with open(vector_store_path, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        return vector_store_path, index_id
    
    def get_embeddings_count(self, index_id: str) -> int:
        """Get the number of embeddings in an index"""
        if index_id in self.vector_stores:
            return self.vector_stores[index_id].ntotal
        
        # Check for mock data
        mock_path = os.path.join("./vector_store", f"{index_id}_mock.json")
        if os.path.exists(mock_path):
            with open(mock_path, 'r') as f:
                data = json.load(f)
                return data.get('embeddings_count', 0)
        
        return 0
    
    def search_similar(self, query: str, index_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        if not self.model or index_id not in self.vector_stores:
            return []
        
        try:
            # Encode query
            query_embedding = self.model.encode([query])
            
            # Search in FAISS index
            index = self.vector_stores[index_id]
            distances, indices = index.search(query_embedding.astype('float32'), k)
            
            # Get metadata for results
            metadata = self.metadata_stores[index_id]
            results = []
            
            for i, idx in enumerate(indices[0]):
                if idx < len(metadata):
                    result = metadata[idx].copy()
                    result['distance'] = float(distances[0][i])
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error searching embeddings: {e}")
            return []