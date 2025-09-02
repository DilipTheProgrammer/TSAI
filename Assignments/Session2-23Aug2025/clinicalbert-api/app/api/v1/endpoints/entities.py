"""Entity extraction endpoints for clinical NLP"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import logging

from app.models.clinical_bert import ClinicalBERTModel
from app.services.model_service import ModelService
from app.services.fhir_adapter import FHIRAdapter
from app.schemas.fhir_schemas import (
    PredictionRequest, EntityExtractionResponse, TextInput, FHIRInput
)
from app.core.security import get_current_user
from main import get_clinical_bert_model

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/extract_entities", response_model=EntityExtractionResponse)
async def extract_clinical_entities(
    request: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Extract clinical entities (diagnoses, treatments, findings) from text
    
    **Input:** Clinical narrative or FHIR DocumentReference
    **Output:** Entities as JSON or FHIR Condition, MedicationStatement resources
    """
    try:
        logger.info(f"Entity extraction request from user: {current_user.get('user_id')}")
        
        # Initialize model service
        model_service = ModelService(model)
        
        # Extract entities
        result = await model_service.extract_entities(
            input_data=request.input,
            return_fhir=request.return_fhir
        )
        
        logger.info(f"Entity extraction completed: {len(result.entities)} entities found")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in entity extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in entity extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during entity extraction"
        )

@router.post("/extract_sections")
async def extract_clinical_sections(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Extract structured sections from clinical notes
    
    **Input:** Clinical note text
    **Output:** Structured sections (Chief Complaint, HPI, Assessment, etc.)
    """
    try:
        logger.info(f"Section extraction request from user: {current_user.get('user_id')}")
        
        text = request.get("text", "")
        if not text.strip():
            raise ValueError("No text provided for section extraction")
        
        # Extract sections using text preprocessor
        from app.utils.text_preprocessing import TextPreprocessor
        preprocessor = TextPreprocessor()
        
        sections = preprocessor.extract_sections(text)
        
        # Create FHIR DocumentReference if requested
        fhir_response = None
        if request.get("return_fhir", False):
            fhir_adapter = FHIRAdapter()
            
            # Create DocumentReference with sections as content
            document_ref = {
                "resourceType": "DocumentReference",
                "status": "current",
                "type": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "34109-9",
                        "display": "Note"
                    }]
                },
                "content": []
            }
            
            for section_name, section_text in sections.items():
                if section_text.strip():
                    document_ref["content"].append({
                        "attachment": {
                            "contentType": "text/plain",
                            "title": section_name.replace("_", " ").title(),
                            "data": section_text
                        }
                    })
            
            fhir_response = document_ref
        
        result = {
            "sections": sections,
            "section_count": len(sections),
            "total_sections_found": len([s for s in sections.values() if s.strip()])
        }
        
        if fhir_response:
            result["fhir_resource"] = fhir_response
        
        logger.info(f"Section extraction completed: {len(sections)} sections")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in section extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in section extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during section extraction"
        )

@router.post("/batch_extract")
async def batch_extract_entities(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Batch entity extraction for multiple clinical texts
    
    **Input:** Array of clinical texts
    **Output:** Array of entity extraction results
    """
    try:
        logger.info(f"Batch entity extraction request from user: {current_user.get('user_id')}")
        
        texts = request.get("texts", [])
        if not texts:
            raise ValueError("No texts provided for batch extraction")
        
        if len(texts) > 50:  # Limit batch size for entity extraction
            raise ValueError("Batch size cannot exceed 50 texts")
        
        model_service = ModelService(model)
        
        # Process batch
        results = await model_service.batch_process(
            texts=texts,
            operation="entity_extraction"
        )
        
        # Aggregate statistics
        total_entities = sum(len(result.get("entities", [])) for result in results)
        entity_types = set()
        for result in results:
            for entity in result.get("entities", []):
                entity_types.add(entity.get("label", "UNKNOWN"))
        
        logger.info(f"Batch entity extraction completed: {total_entities} total entities")
        return {
            "results": results,
            "total_processed": len(results),
            "total_entities": total_entities,
            "unique_entity_types": list(entity_types),
            "batch_size": len(texts)
        }
        
    except ValueError as e:
        logger.error(f"Validation error in batch entity extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in batch entity extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch entity extraction"
        )
