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

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global model instance
clinical_bert_model: Optional[ClinicalBERTModel] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for model loading"""
    global clinical_bert_model
    
    logger.info("Starting ClinicalBERT API service...")
    
    # Load ClinicalBERT model on startup
    try:
        clinical_bert_model = ClinicalBERTModel()
        await clinical_bert_model.load_model()
        logger.info("ClinicalBERT model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ClinicalBERT model: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down ClinicalBERT API service...")
    if clinical_bert_model:
        clinical_bert_model.cleanup()

# Create FastAPI application
app = FastAPI(
    title="ClinicalBERT API with FHIR",
    description="FastAPI service for clinical note processing with FHIR integration",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
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

def get_clinical_bert_model() -> ClinicalBERTModel:
    """Dependency to get ClinicalBERT model instance"""
    if clinical_bert_model is None:
        raise HTTPException(status_code=503, detail="ClinicalBERT model not loaded")
    return clinical_bert_model

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ClinicalBERT API",
        "version": "1.0.0",
        "model_loaded": clinical_bert_model is not None
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
