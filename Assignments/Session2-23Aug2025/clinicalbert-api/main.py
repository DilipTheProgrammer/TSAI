"""
ClinicalBERT FastAPI Application with FHIR Integration
Healthcare AI service for clinical note processing and prediction
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Optional

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.models.clinical_bert import ClinicalBERTModel
from app.core.security import verify_token
from app.dependencies import set_clinical_bert_model, get_clinical_bert_model

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="ClinicalBERT API with FHIR",
    description="FastAPI service for clinical note processing with FHIR integration",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token and get current user"""
    if settings.ENVIRONMENT == "development":
        return {"user_id": "dev_user", "scopes": ["read", "write"]}
    
    return await verify_token(credentials.credentials)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        model = get_clinical_bert_model()
        model_loaded = model is not None
    except:
        model_loaded = False
    
    return {
        "status": "healthy",
        "service": "ClinicalBERT API",
        "version": "1.0.0",
        "model_loaded": model_loaded
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ClinicalBERT API with FHIR Integration",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
