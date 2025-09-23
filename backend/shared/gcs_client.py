from google.cloud import storage
from google.cloud import aiplatform
import json
import os
from typing import List, Dict, Any, Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)

class GCSClient:
    def __init__(self):
        self.storage_client = storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)
        self.bucket = self.storage_client.bucket(settings.GCS_BUCKET_NAME)
        self.vector_bucket = self.storage_client.bucket(settings.GCS_VECTOR_BUCKET)
        self.logs_bucket = self.storage_client.bucket(settings.GCS_LOGS_BUCKET)
    
    def upload_file(self, file_path: str, destination_blob_name: str, bucket_name: str = None) -> str:
        """Upload a file to Google Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(bucket_name or settings.GCS_BUCKET_NAME)
            blob = bucket.blob(destination_blob_name)
            
            blob.upload_from_filename(file_path)
            
            logger.info(f"File {file_path} uploaded to {destination_blob_name}")
            return f"gs://{bucket.name}/{destination_blob_name}"
            
        except Exception as e:
            logger.error(f"Error uploading file to GCS: {e}")
            raise
    
    def upload_json(self, data: Dict[str, Any], destination_blob_name: str, bucket_name: str = None) -> str:
        """Upload JSON data to Google Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(bucket_name or settings.GCS_BUCKET_NAME)
            blob = bucket.blob(destination_blob_name)
            
            blob.upload_from_string(
                json.dumps(data, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"JSON data uploaded to {destination_blob_name}")
            return f"gs://{bucket.name}/{destination_blob_name}"
            
        except Exception as e:
            logger.error(f"Error uploading JSON to GCS: {e}")
            raise
    
    def download_json(self, blob_name: str, bucket_name: str = None) -> Dict[str, Any]:
        """Download JSON data from Google Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(bucket_name or settings.GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)
            
            content = blob.download_as_text()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error downloading JSON from GCS: {e}")
            raise
    
    def upload_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], 
                      project_id: str, index_id: str) -> str:
        """Upload vector embeddings to Google Cloud Storage"""
        try:
            vector_data = {
                "vectors": vectors,
                "metadata": metadata,
                "project_id": project_id,
                "index_id": index_id,
                "timestamp": str(datetime.utcnow())
            }
            
            blob_name = f"vectors/{project_id}/{index_id}.json"
            return self.upload_json(vector_data, blob_name, settings.GCS_VECTOR_BUCKET)
            
        except Exception as e:
            logger.error(f"Error uploading vectors to GCS: {e}")
            raise
    
    def upload_logs(self, log_content: str, test_flow_id: str, execution_id: str) -> str:
        """Upload test execution logs to Google Cloud Storage"""
        try:
            blob_name = f"logs/{test_flow_id}/{execution_id}.log"
            bucket = self.storage_client.bucket(settings.GCS_LOGS_BUCKET)
            blob = bucket.blob(blob_name)
            
            blob.upload_from_string(log_content, content_type='text/plain')
            
            logger.info(f"Logs uploaded to {blob_name}")
            return f"gs://{settings.GCS_LOGS_BUCKET}/{blob_name}"
            
        except Exception as e:
            logger.error(f"Error uploading logs to GCS: {e}")
            raise

class VertexAIClient:
    def __init__(self):
        aiplatform.init(
            project=settings.VERTEX_AI_PROJECT,
            location=settings.VERTEX_AI_LOCATION
        )
        self.model_name = settings.VERTEX_AI_MODEL
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Vertex AI"""
        try:
            from vertexai.language_models import TextEmbeddingModel
            
            model = TextEmbeddingModel.from_pretrained(self.model_name)
            embeddings = model.get_embeddings(texts)
            
            return [embedding.values for embedding in embeddings]
            
        except Exception as e:
            logger.error(f"Error generating embeddings with Vertex AI: {e}")
            # Fallback to mock embeddings for development
            return [[0.1] * 768 for _ in texts]  # Mock 768-dimensional embeddings
    
    def similarity_search(self, query_embedding: List[float], 
                         stored_embeddings: List[List[float]], 
                         top_k: int = 5) -> List[int]:
        """Perform similarity search on embeddings"""
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            query_array = np.array(query_embedding).reshape(1, -1)
            stored_array = np.array(stored_embeddings)
            
            similarities = cosine_similarity(query_array, stored_array)[0]
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            return top_indices.tolist()
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            return list(range(min(top_k, len(stored_embeddings))))

# Global clients
gcs_client = GCSClient()
vertex_ai_client = VertexAIClient()