import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:password@localhost:3306/impact_analyzer"
    )
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    IMPACT_ANALYZER_API_KEY: str = os.getenv("IMPACT_ANALYZER_API_KEY", "dev-key-123")
    
    # Vector Store
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Services
    MS_INDEX_URL: str = os.getenv("MS_INDEX_URL", "http://localhost:8001")
    MS_MR_URL: str = os.getenv("MS_MR_URL", "http://localhost:8002")
    MS_COMMON_URL: str = os.getenv("MS_COMMON_URL", "http://localhost:8003")
    MS_AI_URL: str = os.getenv("MS_AI_URL", "http://localhost:8004")
    
    # Git
    TEMP_REPO_PATH: str = os.getenv("TEMP_REPO_PATH", "./temp_repos")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()