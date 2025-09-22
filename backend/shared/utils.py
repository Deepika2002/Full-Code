import logging
import uuid
from typing import Dict, Any, Optional
from fastapi import HTTPException, Header
from .config import settings

def setup_logging(service_name: str):
    """Setup structured logging for a service"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=f'%(asctime)s - {service_name} - %(levelname)s - %(message)s'
    )
    return logging.getLogger(service_name)

def generate_request_id() -> str:
    """Generate a unique request ID for tracing"""
    return str(uuid.uuid4())[:8]

def verify_api_key(x_impact_analyzer_api_key: Optional[str] = Header(None)):
    """Verify API key if configured"""
    if settings.IMPACT_ANALYZER_API_KEY and x_impact_analyzer_api_key != settings.IMPACT_ANALYZER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

def create_error_response(message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "message": message,
        "details": details or {}
    }

def create_success_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "success": True,
        "message": message,
        **data
    }