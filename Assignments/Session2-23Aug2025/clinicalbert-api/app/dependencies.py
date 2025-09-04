"""
Application dependencies for FastAPI dependency injection
"""

from fastapi import HTTPException
from typing import Optional
import logging

from app.models.clinical_bert import ClinicalBERTModel

logger = logging.getLogger(__name__)

# Global model instance
clinical_bert_model: Optional[ClinicalBERTModel] = None

def set_clinical_bert_model(model: ClinicalBERTModel):
    """Set the global ClinicalBERT model instance"""
    global clinical_bert_model
    clinical_bert_model = model
    logger.info("ClinicalBERT model dependency set")

def get_clinical_bert_model() -> ClinicalBERTModel:
    """Dependency to get ClinicalBERT model instance"""
    if clinical_bert_model is None:
        raise HTTPException(status_code=503, detail="ClinicalBERT model not loaded")
    return clinical_bert_model
