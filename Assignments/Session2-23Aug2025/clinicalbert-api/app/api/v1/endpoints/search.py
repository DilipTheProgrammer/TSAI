"""Search endpoints for similarity search and information retrieval"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import logging

from app.models.clinical_bert import ClinicalBERTModel
from app.services.model_service import ModelService
from app.schemas.fhir_schemas import SearchRequest, SearchResponse
from app.core.security import get_current_user
from main import get_clinical_bert_model

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/search_cases", response_model=SearchResponse)
async def search_similar_cases(
    request: SearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Semantic search for similar patient cases using ClinicalBERT embeddings
    
    **Input:** Search query text or FHIR search params
    **Output:** List of patient IDs or FHIR Patient/Encounter references ranked by similarity
    """
    try:
        logger.info(f"Case search request from user: {current_user.get('user_id')}")
        
        # Extract query text
        if isinstance(request.query, str):
            query_text = request.query
        elif isinstance(request.query, dict):
            # Extract text from FHIR search parameters
            query_text = request.query.get("text", "")
            if not query_text:
                raise ValueError("No search text found in FHIR parameters")
        else:
            raise ValueError("Invalid query format")
        
        if not query_text.strip():
            raise ValueError("Empty search query")
        
        # For demonstration, we'll use a mock database of clinical cases
        # In production, this would connect to a real patient database
        mock_cases = [
            "Patient with diabetes mellitus type 2, hypertension, and chronic kidney disease",
            "Elderly patient admitted with acute myocardial infarction and heart failure",
            "Young adult with asthma exacerbation and pneumonia",
            "Patient with sepsis secondary to urinary tract infection",
            "Chronic obstructive pulmonary disease with acute exacerbation",
            "Patient with stroke and atrial fibrillation",
            "Diabetic patient with diabetic ketoacidosis",
            "Patient with acute appendicitis requiring surgery",
            "Elderly patient with hip fracture and dementia",
            "Patient with acute pancreatitis and alcohol use disorder"
        ]
        
        model_service = ModelService(model)
        
        # Perform similarity search
        similar_cases = await model_service.similarity_search(
            query_text=query_text,
            candidate_texts=mock_cases,
            top_k=request.limit,
            threshold=request.threshold
        )
        
        # Format results with mock patient/encounter references
        formatted_results = []
        for i, case in enumerate(similar_cases):
            result = {
                "case_id": f"case_{case['index']}",
                "patient_reference": f"Patient/{1000 + case['index']}",
                "encounter_reference": f"Encounter/{2000 + case['index']}",
                "similarity_score": case["similarity_score"],
                "case_summary": case["text"],
                "rank": i + 1
            }
            formatted_results.append(result)
        
        response = SearchResponse(
            results=formatted_results,
            total=len(formatted_results),
            processing_time=None
        )
        
        logger.info(f"Case search completed: {len(formatted_results)} similar cases found")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in case search: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in case search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during case search"
        )

@router.post("/semantic_search")
async def semantic_text_search(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    General semantic search across clinical documents
    
    **Input:** Query text and document corpus
    **Output:** Ranked documents by semantic similarity
    """
    try:
        logger.info(f"Semantic search request from user: {current_user.get('user_id')}")
        
        query_text = request.get("query", "")
        documents = request.get("documents", [])
        top_k = request.get("limit", 10)
        threshold = request.get("threshold", 0.5)
        
        if not query_text.strip():
            raise ValueError("Empty search query")
        
        if not documents:
            raise ValueError("No documents provided for search")
        
        if len(documents) > 1000:
            raise ValueError("Document corpus cannot exceed 1000 documents")
        
        model_service = ModelService(model)
        
        # Perform semantic search
        results = await model_service.similarity_search(
            query_text=query_text,
            candidate_texts=documents,
            top_k=top_k,
            threshold=threshold
        )
        
        # Add document metadata
        for i, result in enumerate(results):
            result["document_id"] = f"doc_{result['index']}"
            result["rank"] = i + 1
        
        logger.info(f"Semantic search completed: {len(results)} relevant documents")
        return {
            "query": query_text,
            "results": results,
            "total_documents": len(documents),
            "relevant_documents": len(results),
            "threshold_used": threshold
        }
        
    except ValueError as e:
        logger.error(f"Validation error in semantic search: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during semantic search"
        )

@router.post("/find_similar_patients")
async def find_similar_patients(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Find patients with similar clinical presentations
    
    **Input:** Patient clinical summary or condition list
    **Output:** Similar patients with matching conditions/presentations
    """
    try:
        logger.info(f"Similar patients search from user: {current_user.get('user_id')}")
        
        patient_summary = request.get("patient_summary", "")
        conditions = request.get("conditions", [])
        limit = request.get("limit", 10)
        
        # Combine patient summary and conditions
        search_text = patient_summary
        if conditions:
            conditions_text = " ".join(conditions)
            search_text = f"{patient_summary} {conditions_text}".strip()
        
        if not search_text:
            raise ValueError("No patient information provided")
        
        # Mock patient database for demonstration
        mock_patients = [
            {
                "patient_id": "P001",
                "summary": "65-year-old male with diabetes, hypertension, and coronary artery disease",
                "conditions": ["diabetes mellitus", "hypertension", "coronary artery disease"]
            },
            {
                "patient_id": "P002", 
                "summary": "72-year-old female with heart failure and atrial fibrillation",
                "conditions": ["heart failure", "atrial fibrillation"]
            },
            {
                "patient_id": "P003",
                "summary": "58-year-old male with COPD and diabetes",
                "conditions": ["COPD", "diabetes mellitus"]
            },
            {
                "patient_id": "P004",
                "summary": "45-year-old female with asthma and allergic rhinitis",
                "conditions": ["asthma", "allergic rhinitis"]
            },
            {
                "patient_id": "P005",
                "summary": "80-year-old male with dementia and hypertension",
                "conditions": ["dementia", "hypertension"]
            }
        ]
        
        # Extract text for similarity comparison
        patient_texts = [p["summary"] for p in mock_patients]
        
        model_service = ModelService(model)
        
        # Find similar patients
        similar_results = await model_service.similarity_search(
            query_text=search_text,
            candidate_texts=patient_texts,
            top_k=limit,
            threshold=0.3  # Lower threshold for patient matching
        )
        
        # Format results with patient metadata
        similar_patients = []
        for result in similar_results:
            patient_data = mock_patients[result["index"]]
            similar_patients.append({
                "patient_id": patient_data["patient_id"],
                "patient_reference": f"Patient/{patient_data['patient_id']}",
                "similarity_score": result["similarity_score"],
                "summary": result["text"],
                "conditions": patient_data["conditions"],
                "match_strength": "high" if result["similarity_score"] > 0.7 else "medium" if result["similarity_score"] > 0.5 else "low"
            })
        
        logger.info(f"Similar patients search completed: {len(similar_patients)} matches")
        return {
            "query_patient": {
                "summary": patient_summary,
                "conditions": conditions
            },
            "similar_patients": similar_patients,
            "total_matches": len(similar_patients)
        }
        
    except ValueError as e:
        logger.error(f"Validation error in similar patients search: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in similar patients search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during similar patients search"
        )
