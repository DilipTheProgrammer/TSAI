"""Prediction endpoints for readmission risk and risk trajectory"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Union
import logging
from datetime import datetime

from app.models.clinical_bert import ClinicalBERTModel
from app.services.model_service import ModelService
from app.services.fhir_adapter import FHIRAdapter
from app.schemas.fhir_schemas import (
    PredictionRequest, PredictionResponse, TextInput, FHIRInput,
    Bundle, Observation
)
from app.core.security import get_current_user
from main import get_clinical_bert_model

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/predict_readmission", response_model=PredictionResponse)
async def predict_readmission(
    request: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Predict 30-day readmission risk from clinical text or FHIR DocumentReference
    
    **Input:** Raw text `{ "text": "..." }` or FHIR DocumentReference JSON
    **Process:** Extract note text, predict risk, return FHIR Observation
    **Output:** FHIR Observation with readmission risk score
    """
    try:
        logger.info(f"Readmission prediction request from user: {current_user.get('user_id')}")
        
        # Initialize model service
        model_service = ModelService(model)
        
        # Process prediction
        result = await model_service.predict_readmission(
            input_data=request.input,
            return_fhir=request.return_fhir
        )
        
        logger.info(f"Readmission prediction completed: risk={result.prediction}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in readmission prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in readmission prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during prediction"
        )

@router.post("/risk_trajectory")
async def calculate_risk_trajectory(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Calculate dynamic readmission risk trajectory during hospital stay
    
    **Input:** Array of notes or FHIR Bundle with temporal clinical data
    **Output:** FHIR Bundle of Observation resources representing risk scores over time
    """
    try:
        logger.info(f"Risk trajectory request from user: {current_user.get('user_id')}")
        
        model_service = ModelService(model)
        fhir_adapter = FHIRAdapter()
        
        # Extract input data
        if "bundle" in request:
            # FHIR Bundle input
            bundle_data = request["bundle"]
            if bundle_data.get("resourceType") != "Bundle":
                raise ValueError("Invalid FHIR Bundle format")
            
            texts = []
            timestamps = []
            
            for entry in bundle_data.get("entry", []):
                if "resource" in entry:
                    text, metadata = fhir_adapter.extract_text_from_fhir(entry["resource"])
                    if text.strip():
                        texts.append(text)
                        # Extract timestamp if available
                        resource = entry["resource"]
                        timestamp = None
                        if "effectiveDateTime" in resource:
                            timestamp = datetime.fromisoformat(resource["effectiveDateTime"].replace("Z", "+00:00"))
                        elif "issued" in resource:
                            timestamp = datetime.fromisoformat(resource["issued"].replace("Z", "+00:00"))
                        timestamps.append(timestamp)
            
        elif "texts" in request:
            # Array of texts
            texts = request["texts"]
            timestamps = request.get("timestamps")
            if timestamps:
                timestamps = [datetime.fromisoformat(ts) if isinstance(ts, str) else ts for ts in timestamps]
        else:
            raise ValueError("Request must contain 'bundle' or 'texts' field")
        
        if not texts:
            raise ValueError("No clinical text found in input")
        
        # Calculate trajectory
        trajectory_result = await model_service.get_risk_trajectory(texts, timestamps)
        
        # Create FHIR Bundle response if requested
        if request.get("return_fhir", True):
            observations = []
            for point in trajectory_result["trajectory"]:
                observation = fhir_adapter.create_observation_resource(
                    prediction_value=point["risk_score"],
                    observation_type="readmission-risk"
                )
                
                # Add timestamp if available
                if "timestamp" in point:
                    observation["effectiveDateTime"] = point["timestamp"]
                
                # Add trajectory metadata
                observation["component"] = [
                    {
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "LA6115-6",
                                "display": "Trajectory index"
                            }]
                        },
                        "valueInteger": point["index"]
                    },
                    {
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": "LA6116-4", 
                                "display": "Risk category"
                            }]
                        },
                        "valueString": point["risk_category"]
                    }
                ]
                
                observations.append(observation)
            
            fhir_bundle = fhir_adapter.create_bundle_resource(
                resources=observations,
                bundle_type="collection"
            )
            
            trajectory_result["fhir_bundle"] = fhir_bundle
        
        logger.info(f"Risk trajectory completed: {len(trajectory_result['trajectory'])} points")
        return trajectory_result
        
    except ValueError as e:
        logger.error(f"Validation error in risk trajectory: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in risk trajectory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during trajectory calculation"
        )

@router.post("/batch_predict")
async def batch_predict_readmission(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Batch prediction for multiple clinical texts
    
    **Input:** Array of clinical texts
    **Output:** Array of prediction results
    """
    try:
        logger.info(f"Batch prediction request from user: {current_user.get('user_id')}")
        
        texts = request.get("texts", [])
        if not texts:
            raise ValueError("No texts provided for batch prediction")
        
        if len(texts) > 100:  # Limit batch size
            raise ValueError("Batch size cannot exceed 100 texts")
        
        model_service = ModelService(model)
        
        # Process batch
        results = await model_service.batch_process(
            texts=texts,
            operation="readmission_prediction"
        )
        
        logger.info(f"Batch prediction completed: {len(results)} predictions")
        return {
            "results": results,
            "total_processed": len(results),
            "batch_size": len(texts)
        }
        
    except ValueError as e:
        logger.error(f"Validation error in batch prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in batch prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch prediction"
        )
