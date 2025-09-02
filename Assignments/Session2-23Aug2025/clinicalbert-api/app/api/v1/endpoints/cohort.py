"""Cohort identification endpoints for patient group analysis"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import logging
import re

from app.models.clinical_bert import ClinicalBERTModel
from app.services.model_service import ModelService
from app.services.fhir_adapter import FHIRAdapter
from app.core.security import get_current_user
from main import get_clinical_bert_model

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/cohort_identification")
async def identify_patient_cohort(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Identify patient groups based on clinical criteria
    
    **Input:** Clinical criteria plus patient notes or FHIR search params
    **Output:** List or Bundle of matching patient IDs/resources
    """
    try:
        logger.info(f"Cohort identification request from user: {current_user.get('user_id')}")
        
        # Extract criteria
        criteria = request.get("criteria", {})
        if not criteria:
            raise ValueError("No cohort criteria provided")
        
        # Extract patient data source
        patient_notes = request.get("patient_notes", [])
        fhir_search_params = request.get("fhir_search_params", {})
        return_fhir = request.get("return_fhir", True)
        
        # Mock patient database for demonstration
        mock_patients = [
            {
                "patient_id": "P001",
                "age": 65,
                "gender": "male",
                "conditions": ["diabetes mellitus type 2", "hypertension", "coronary artery disease"],
                "medications": ["metformin", "lisinopril", "atorvastatin"],
                "clinical_note": "65-year-old male with well-controlled diabetes and hypertension. Recent cardiac catheterization showed stable CAD.",
                "lab_values": {"hba1c": 7.2, "ldl": 95, "bp_systolic": 135}
            },
            {
                "patient_id": "P002",
                "age": 72,
                "gender": "female", 
                "conditions": ["heart failure", "atrial fibrillation", "diabetes mellitus type 2"],
                "medications": ["metoprolol", "warfarin", "furosemide", "metformin"],
                "clinical_note": "72-year-old female with heart failure with reduced ejection fraction and diabetes.",
                "lab_values": {"hba1c": 8.1, "bnp": 450, "creatinine": 1.3}
            },
            {
                "patient_id": "P003",
                "age": 58,
                "gender": "male",
                "conditions": ["COPD", "diabetes mellitus type 2", "hypertension"],
                "medications": ["albuterol", "metformin", "amlodipine"],
                "clinical_note": "58-year-old male with moderate COPD and diabetes. Recent exacerbation required hospitalization.",
                "lab_values": {"hba1c": 7.8, "fev1": 55, "bp_systolic": 142}
            },
            {
                "patient_id": "P004",
                "age": 45,
                "gender": "female",
                "conditions": ["asthma", "allergic rhinitis"],
                "medications": ["fluticasone", "albuterol", "loratadine"],
                "clinical_note": "45-year-old female with well-controlled asthma and seasonal allergies.",
                "lab_values": {"ige": 250, "eosinophils": 8}
            },
            {
                "patient_id": "P005",
                "age": 80,
                "gender": "male",
                "conditions": ["dementia", "hypertension", "diabetes mellitus type 2"],
                "medications": ["donepezil", "metformin", "lisinopril"],
                "clinical_note": "80-year-old male with moderate dementia and multiple comorbidities.",
                "lab_values": {"hba1c": 8.5, "mmse": 18, "bp_systolic": 128}
            }
        ]
        
        # Apply cohort criteria
        matching_patients = []
        
        for patient in mock_patients:
            matches_criteria = True
            
            # Age criteria
            if "age_min" in criteria and patient["age"] < criteria["age_min"]:
                matches_criteria = False
            if "age_max" in criteria and patient["age"] > criteria["age_max"]:
                matches_criteria = False
            
            # Gender criteria
            if "gender" in criteria and patient["gender"] != criteria["gender"].lower():
                matches_criteria = False
            
            # Condition criteria
            if "conditions" in criteria:
                required_conditions = criteria["conditions"]
                if isinstance(required_conditions, str):
                    required_conditions = [required_conditions]
                
                patient_conditions_text = " ".join(patient["conditions"]).lower()
                for condition in required_conditions:
                    if condition.lower() not in patient_conditions_text:
                        matches_criteria = False
                        break
            
            # Medication criteria
            if "medications" in criteria:
                required_medications = criteria["medications"]
                if isinstance(required_medications, str):
                    required_medications = [required_medications]
                
                patient_medications_text = " ".join(patient["medications"]).lower()
                for medication in required_medications:
                    if medication.lower() not in patient_medications_text:
                        matches_criteria = False
                        break
            
            # Lab value criteria
            if "lab_criteria" in criteria:
                lab_criteria = criteria["lab_criteria"]
                for lab_name, lab_condition in lab_criteria.items():
                    if lab_name in patient["lab_values"]:
                        patient_value = patient["lab_values"][lab_name]
                        
                        # Parse condition (e.g., ">7.0", "<=100", ">=50")
                        if not self._evaluate_lab_condition(patient_value, lab_condition):
                            matches_criteria = False
                            break
            
            # Text-based criteria using NLP
            if "text_criteria" in criteria and matches_criteria:
                text_criteria = criteria["text_criteria"]
                model_service = ModelService(model)
                
                # Use similarity search to match text criteria
                similarity_results = await model_service.similarity_search(
                    query_text=text_criteria,
                    candidate_texts=[patient["clinical_note"]],
                    top_k=1,
                    threshold=0.6
                )
                
                if not similarity_results:
                    matches_criteria = False
            
            if matches_criteria:
                matching_patients.append(patient)
        
        # Format response
        cohort_results = {
            "cohort_criteria": criteria,
            "total_patients_screened": len(mock_patients),
            "matching_patients": len(matching_patients),
            "patients": []
        }
        
        for patient in matching_patients:
            patient_result = {
                "patient_id": patient["patient_id"],
                "patient_reference": f"Patient/{patient['patient_id']}",
                "age": patient["age"],
                "gender": patient["gender"],
                "conditions": patient["conditions"],
                "medications": patient["medications"],
                "clinical_summary": patient["clinical_note"]
            }
            cohort_results["patients"].append(patient_result)
        
        # Create FHIR Bundle if requested
        if return_fhir and matching_patients:
            fhir_adapter = FHIRAdapter()
            
            # Create patient resources
            patient_resources = []
            for patient in matching_patients:
                patient_resource = {
                    "resourceType": "Patient",
                    "id": patient["patient_id"],
                    "gender": patient["gender"],
                    "birthDate": f"{2024 - patient['age']}-01-01"  # Approximate birth year
                }
                patient_resources.append(patient_resource)
            
            fhir_bundle = fhir_adapter.create_bundle_resource(
                resources=patient_resources,
                bundle_type="searchset"
            )
            
            cohort_results["fhir_bundle"] = fhir_bundle
        
        logger.info(f"Cohort identification completed: {len(matching_patients)} patients matched")
        return cohort_results
        
    except ValueError as e:
        logger.error(f"Validation error in cohort identification: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in cohort identification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during cohort identification"
        )

    def _evaluate_lab_condition(self, value: float, condition: str) -> bool:
        """Evaluate lab value against condition string"""
        try:
            # Parse condition like ">7.0", "<=100", ">=50"
            if condition.startswith(">="):
                threshold = float(condition[2:])
                return value >= threshold
            elif condition.startswith("<="):
                threshold = float(condition[2:])
                return value <= threshold
            elif condition.startswith(">"):
                threshold = float(condition[1:])
                return value > threshold
            elif condition.startswith("<"):
                threshold = float(condition[1:])
                return value < threshold
            elif condition.startswith("="):
                threshold = float(condition[1:])
                return abs(value - threshold) < 0.01
            else:
                # Try direct comparison
                threshold = float(condition)
                return abs(value - threshold) < 0.01
        except (ValueError, IndexError):
            return False

@router.post("/analyze_cohort")
async def analyze_patient_cohort(
    request: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    model: ClinicalBERTModel = Depends(get_clinical_bert_model)
):
    """
    Analyze characteristics of an identified patient cohort
    
    **Input:** List of patient IDs or clinical data
    **Output:** Cohort analysis with statistics and insights
    """
    try:
        logger.info(f"Cohort analysis request from user: {current_user.get('user_id')}")
        
        patient_ids = request.get("patient_ids", [])
        patient_data = request.get("patient_data", [])
        
        if not patient_ids and not patient_data:
            raise ValueError("No patient data provided for analysis")
        
        # Mock analysis for demonstration
        if patient_ids:
            # In production, would fetch patient data from database
            analysis_results = {
                "cohort_size": len(patient_ids),
                "patient_ids": patient_ids,
                "demographics": {
                    "age_distribution": {
                        "mean": 62.5,
                        "median": 65.0,
                        "std": 12.3,
                        "min": 45,
                        "max": 80
                    },
                    "gender_distribution": {
                        "male": 0.6,
                        "female": 0.4
                    }
                },
                "common_conditions": [
                    {"condition": "diabetes mellitus", "frequency": 0.8},
                    {"condition": "hypertension", "frequency": 0.7},
                    {"condition": "coronary artery disease", "frequency": 0.3}
                ],
                "common_medications": [
                    {"medication": "metformin", "frequency": 0.8},
                    {"medication": "lisinopril", "frequency": 0.5},
                    {"medication": "atorvastatin", "frequency": 0.3}
                ],
                "risk_factors": {
                    "high_readmission_risk": 0.25,
                    "polypharmacy": 0.4,
                    "multiple_comorbidities": 0.6
                }
            }
        else:
            # Analyze provided patient data
            analysis_results = self._analyze_patient_data(patient_data)
        
        logger.info(f"Cohort analysis completed for {analysis_results['cohort_size']} patients")
        return analysis_results
        
    except ValueError as e:
        logger.error(f"Validation error in cohort analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in cohort analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during cohort analysis"
        )

    def _analyze_patient_data(self, patient_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze provided patient data"""
        if not patient_data:
            return {"cohort_size": 0}
        
        # Calculate demographics
        ages = [p.get("age", 0) for p in patient_data if "age" in p]
        genders = [p.get("gender", "").lower() for p in patient_data if "gender" in p]
        
        # Calculate condition frequencies
        all_conditions = []
        for patient in patient_data:
            conditions = patient.get("conditions", [])
            all_conditions.extend(conditions)
        
        condition_counts = {}
        for condition in all_conditions:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        
        common_conditions = [
            {"condition": condition, "frequency": count / len(patient_data)}
            for condition, count in sorted(condition_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return {
            "cohort_size": len(patient_data),
            "demographics": {
                "age_distribution": {
                    "mean": sum(ages) / len(ages) if ages else 0,
                    "min": min(ages) if ages else 0,
                    "max": max(ages) if ages else 0
                },
                "gender_distribution": {
                    "male": genders.count("male") / len(genders) if genders else 0,
                    "female": genders.count("female") / len(genders) if genders else 0
                }
            },
            "common_conditions": common_conditions,
            "total_unique_conditions": len(condition_counts)
        }
