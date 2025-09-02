"""FHIR Adapter for converting between FHIR resources and plain text"""

from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import uuid
import json
import logging
from fhir.resources.documentreference import DocumentReference as FHIRDocumentReference
from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.condition import Condition as FHIRCondition
from fhir.resources.bundle import Bundle as FHIRBundle
from fhir.resources.codeableconcept import CodeableConcept as FHIRCodeableConcept
from fhir.resources.coding import Coding as FHIRCoding
from fhir.resources.quantity import Quantity as FHIRQuantity
from fhir.resources.reference import Reference as FHIRReference

from app.schemas.fhir_schemas import (
    DocumentReference, Observation, Condition, Bundle,
    TextInput, FHIRInput, ObservationStatus
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class FHIRAdapter:
    """Adapter for FHIR resource processing and conversion"""
    
    def __init__(self):
        self.fhir_version = settings.FHIR_VERSION
        
    def extract_text_from_fhir(self, fhir_resource: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Extract clinical text from FHIR resource
        
        Args:
            fhir_resource: FHIR resource dictionary
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        resource_type = fhir_resource.get('resourceType', '')
        metadata = {
            'resource_type': resource_type,
            'resource_id': fhir_resource.get('id'),
            'patient_id': None,
            'encounter_id': None
        }
        
        text_content = ""
        
        try:
            if resource_type == 'DocumentReference':
                text_content = self._extract_from_document_reference(fhir_resource, metadata)
            elif resource_type == 'Observation':
                text_content = self._extract_from_observation(fhir_resource, metadata)
            elif resource_type == 'Condition':
                text_content = self._extract_from_condition(fhir_resource, metadata)
            elif resource_type == 'Bundle':
                text_content = self._extract_from_bundle(fhir_resource, metadata)
            else:
                # Generic text extraction
                text_content = self._generic_text_extraction(fhir_resource, metadata)
                
        except Exception as e:
            logger.error(f"Error extracting text from FHIR resource: {e}")
            raise ValueError(f"Failed to extract text from {resource_type}: {str(e)}")
            
        return text_content.strip(), metadata
    
    def _extract_from_document_reference(self, resource: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Extract text from DocumentReference"""
        text_parts = []
        
        # Extract subject reference
        if 'subject' in resource and 'reference' in resource['subject']:
            metadata['patient_id'] = resource['subject']['reference']
            
        # Extract description
        if 'description' in resource:
            text_parts.append(resource['description'])
            
        # Extract content
        if 'content' in resource:
            for content in resource['content']:
                if 'attachment' in content:
                    attachment = content['attachment']
                    if 'data' in attachment:
                        # Base64 decoded content
                        import base64
                        try:
                            decoded = base64.b64decode(attachment['data']).decode('utf-8')
                            text_parts.append(decoded)
                        except Exception:
                            pass
                    elif 'url' in attachment:
                        # URL reference - would need to fetch
                        text_parts.append(f"[Document URL: {attachment['url']}]")
                        
        return " ".join(text_parts)
    
    def _extract_from_observation(self, resource: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Extract text from Observation"""
        text_parts = []
        
        # Extract subject reference
        if 'subject' in resource and 'reference' in resource['subject']:
            metadata['patient_id'] = resource['subject']['reference']
            
        # Extract encounter reference
        if 'encounter' in resource and 'reference' in resource['encounter']:
            metadata['encounter_id'] = resource['encounter']['reference']
            
        # Extract code display
        if 'code' in resource:
            code_text = self._extract_codeable_concept_text(resource['code'])
            if code_text:
                text_parts.append(f"Observation: {code_text}")
                
        # Extract value
        value_text = self._extract_observation_value(resource)
        if value_text:
            text_parts.append(f"Value: {value_text}")
            
        # Extract notes
        if 'note' in resource:
            for note in resource['note']:
                if 'text' in note:
                    text_parts.append(note['text'])
                    
        return " ".join(text_parts)
    
    def _extract_from_condition(self, resource: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Extract text from Condition"""
        text_parts = []
        
        # Extract subject reference
        if 'subject' in resource and 'reference' in resource['subject']:
            metadata['patient_id'] = resource['subject']['reference']
            
        # Extract encounter reference
        if 'encounter' in resource and 'reference' in resource['encounter']:
            metadata['encounter_id'] = resource['encounter']['reference']
            
        # Extract condition code
        if 'code' in resource:
            code_text = self._extract_codeable_concept_text(resource['code'])
            if code_text:
                text_parts.append(f"Condition: {code_text}")
                
        # Extract clinical status
        if 'clinicalStatus' in resource:
            status_text = self._extract_codeable_concept_text(resource['clinicalStatus'])
            if status_text:
                text_parts.append(f"Status: {status_text}")
                
        # Extract notes
        if 'note' in resource:
            for note in resource['note']:
                if 'text' in note:
                    text_parts.append(note['text'])
                    
        return " ".join(text_parts)
    
    def _extract_from_bundle(self, resource: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Extract text from Bundle"""
        text_parts = []
        
        if 'entry' in resource:
            for entry in resource['entry']:
                if 'resource' in entry:
                    entry_text, _ = self.extract_text_from_fhir(entry['resource'])
                    if entry_text:
                        text_parts.append(entry_text)
                        
        return " ".join(text_parts)
    
    def _generic_text_extraction(self, resource: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Generic text extraction for unknown resource types"""
        text_parts = []
        
        # Look for common text fields
        text_fields = ['text', 'description', 'note', 'comment', 'narrative']
        
        for field in text_fields:
            if field in resource:
                if isinstance(resource[field], str):
                    text_parts.append(resource[field])
                elif isinstance(resource[field], list):
                    for item in resource[field]:
                        if isinstance(item, str):
                            text_parts.append(item)
                        elif isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                            
        return " ".join(text_parts)
    
    def _extract_codeable_concept_text(self, codeable_concept: Dict[str, Any]) -> str:
        """Extract text from CodeableConcept"""
        if 'text' in codeable_concept:
            return codeable_concept['text']
            
        if 'coding' in codeable_concept:
            for coding in codeable_concept['coding']:
                if 'display' in coding:
                    return coding['display']
                    
        return ""
    
    def _extract_observation_value(self, observation: Dict[str, Any]) -> str:
        """Extract value from Observation"""
        value_fields = [
            'valueString', 'valueQuantity', 'valueCodeableConcept',
            'valueBoolean', 'valueInteger', 'valueDateTime'
        ]
        
        for field in value_fields:
            if field in observation:
                value = observation[field]
                if field == 'valueQuantity':
                    return f"{value.get('value', '')} {value.get('unit', '')}"
                elif field == 'valueCodeableConcept':
                    return self._extract_codeable_concept_text(value)
                else:
                    return str(value)
                    
        return ""
    
    def create_observation_resource(
        self,
        prediction_value: float,
        patient_id: Optional[str] = None,
        encounter_id: Optional[str] = None,
        observation_type: str = "readmission-risk"
    ) -> Dict[str, Any]:
        """
        Create FHIR Observation resource for prediction results
        
        Args:
            prediction_value: Prediction value (0.0 to 1.0)
            patient_id: Patient reference
            encounter_id: Encounter reference
            observation_type: Type of observation
            
        Returns:
            FHIR Observation resource dictionary
        """
        observation_id = str(uuid.uuid4())
        
        # Define observation codes based on type
        observation_codes = {
            "readmission-risk": {
                "system": "http://loinc.org",
                "code": "75323-6",
                "display": "Readmission risk score"
            },
            "mortality-risk": {
                "system": "http://loinc.org",
                "code": "75324-4",
                "display": "Mortality risk score"
            }
        }
        
        code_info = observation_codes.get(observation_type, observation_codes["readmission-risk"])
        
        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "survey",
                    "display": "Survey"
                }]
            }],
            "code": {
                "coding": [code_info],
                "text": code_info["display"]
            },
            "valueQuantity": {
                "value": round(prediction_value, 4),
                "unit": "probability",
                "system": "http://unitsofmeasure.org",
                "code": "1"
            },
            "issued": datetime.utcnow().isoformat() + "Z"
        }
        
        if patient_id:
            observation["subject"] = {"reference": patient_id}
            
        if encounter_id:
            observation["encounter"] = {"reference": encounter_id}
            
        return observation
    
    def create_condition_resource(
        self,
        condition_text: str,
        condition_code: Optional[str] = None,
        patient_id: Optional[str] = None,
        encounter_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create FHIR Condition resource for extracted entities
        
        Args:
            condition_text: Condition description
            condition_code: Medical code if available
            patient_id: Patient reference
            encounter_id: Encounter reference
            
        Returns:
            FHIR Condition resource dictionary
        """
        condition_id = str(uuid.uuid4())
        
        condition = {
            "resourceType": "Condition",
            "id": condition_id,
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active",
                    "display": "Active"
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed",
                    "display": "Confirmed"
                }]
            },
            "code": {
                "text": condition_text
            },
            "recordedDate": datetime.utcnow().isoformat() + "Z"
        }
        
        if condition_code:
            condition["code"]["coding"] = [{
                "code": condition_code,
                "display": condition_text
            }]
            
        if patient_id:
            condition["subject"] = {"reference": patient_id}
            
        if encounter_id:
            condition["encounter"] = {"reference": encounter_id}
            
        return condition
    
    def create_bundle_resource(
        self,
        resources: List[Dict[str, Any]],
        bundle_type: str = "collection"
    ) -> Dict[str, Any]:
        """
        Create FHIR Bundle resource containing multiple resources
        
        Args:
            resources: List of FHIR resources
            bundle_type: Type of bundle
            
        Returns:
            FHIR Bundle resource dictionary
        """
        bundle_id = str(uuid.uuid4())
        
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": bundle_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total": len(resources),
            "entry": []
        }
        
        for resource in resources:
            entry = {
                "fullUrl": f"urn:uuid:{resource.get('id', str(uuid.uuid4()))}",
                "resource": resource
            }
            bundle["entry"].append(entry)
            
        return bundle
    
    def validate_fhir_resource(self, resource: Dict[str, Any]) -> bool:
        """
        Validate FHIR resource structure
        
        Args:
            resource: FHIR resource dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            resource_type = resource.get('resourceType')
            if not resource_type:
                return False
                
            # Basic validation using fhir.resources
            if resource_type == 'DocumentReference':
                FHIRDocumentReference(**resource)
            elif resource_type == 'Observation':
                FHIRObservation(**resource)
            elif resource_type == 'Condition':
                FHIRCondition(**resource)
            elif resource_type == 'Bundle':
                FHIRBundle(**resource)
            else:
                # Generic validation - check for required fields
                if 'id' not in resource and 'resourceType' not in resource:
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"FHIR validation error: {e}")
            return False
