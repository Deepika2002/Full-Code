import os
from typing import Optional

class Settings:
    # Database - Cloud SQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:password@localhost:3306/impact_analyzer"
    )
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "impact-analyzer-project")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Google Cloud Storage
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "impact-analyzer-storage")
    GCS_VECTOR_BUCKET: str = os.getenv("GCS_VECTOR_BUCKET", "impact-analyzer-vectors")
    GCS_LOGS_BUCKET: str = os.getenv("GCS_LOGS_BUCKET", "impact-analyzer-logs")
    
    # Vector Database - Cloud SQL for PostgreSQL or Vertex AI Vector Search
    VECTOR_DB_URL: str = os.getenv("VECTOR_DB_URL", "postgresql://user:pass@localhost:5432/vectors")
    VERTEX_AI_ENDPOINT: str = os.getenv("VERTEX_AI_ENDPOINT", "")
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    IMPACT_ANALYZER_API_KEY: str = os.getenv("IMPACT_ANALYZER_API_KEY", "dev-key-123")
    
    # Vertex AI Configuration
    VERTEX_AI_PROJECT: str = os.getenv("VERTEX_AI_PROJECT", GOOGLE_CLOUD_PROJECT)
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    VERTEX_AI_MODEL: str = os.getenv("VERTEX_AI_MODEL", "textembedding-gecko@003")
    
    # Services - Cloud Run URLs
    MS_INDEX_URL: str = os.getenv("MS_INDEX_URL", "http://localhost:8001")
    MS_MR_URL: str = os.getenv("MS_MR_URL", "http://localhost:8002")
    MS_COMMON_URL: str = os.getenv("MS_COMMON_URL", "http://localhost:8003")
    MS_AI_URL: str = os.getenv("MS_AI_URL", "http://localhost:8004")
    MS_TESTCASE_URL: str = os.getenv("MS_TESTCASE_URL", "http://localhost:8005")
    
    # Git Configuration
    TEMP_REPO_PATH: str = os.getenv("TEMP_REPO_PATH", "/tmp/repos")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Demo Project Configuration
    DEMO_PROJECT_ID: str = "angular-springboot-ecommerce"
    DEMO_REPO_URL: str = "https://github.com/sinnedpenguin/angular-springboot-ecommerce.git"
    
    # Cloud Scheduler
    DAILY_REFRESH_SCHEDULE: str = os.getenv("DAILY_REFRESH_SCHEDULE", "0 2 * * *")  # 2 AM daily

settings = Settings()