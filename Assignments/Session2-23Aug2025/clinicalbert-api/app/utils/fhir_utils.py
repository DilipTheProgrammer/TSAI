"""FHIR utility functions"""

from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

def generate_fhir_id() -> str:
    """Generate a unique FHIR resource ID"""
    return str(uuid.uuid4())

def create_fhir_reference(resource_type: str, resource_id: str) -> Dict[str, str]:
    """Create a FHIR reference"""
    return {
        "reference": f"{resource_type}/{resource_id}",
        "type": resource_type
    }

def create_coding(system: str, code: str, display: str) -> Dict[str, str]:
    """Create a FHIR Coding"""
    return {
        "system": system,
        "code": code,
        "display": display
    }

def create_codeable_concept(text: str, coding: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """Create a FHIR CodeableConcept"""
    concept = {"text": text}
    if coding:
        concept["coding"] = coding
    return concept

def create_quantity(value: float, unit: str, system: str = "http://unitsofmeasure.org") -> Dict[str, Any]:
    """Create a FHIR Quantity"""
    return {
        "value": value,
        "unit": unit,
        "system": system,
        "code": unit
    }

def format_fhir_datetime(dt: datetime) -> str:
    """Format datetime for FHIR"""
    return dt.isoformat() + "Z"

def extract_patient_id_from_reference(reference: str) -> Optional[str]:
    """Extract patient ID from FHIR reference"""
    if reference and "/" in reference:
        parts = reference.split("/")
        if len(parts) >= 2 and parts[0] == "Patient":
            return parts[1]
    return None

def extract_encounter_id_from_reference(reference: str) -> Optional[str]:
    """Extract encounter ID from FHIR reference"""
    if reference and "/" in reference:
        parts = reference.split("/")
        if len(parts) >= 2 and parts[0] == "Encounter":
            return parts[1]
    return None

def merge_fhir_bundles(bundles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple FHIR bundles into one"""
    merged_entries = []
    total = 0
    
    for bundle in bundles:
        if bundle.get("resourceType") == "Bundle" and "entry" in bundle:
            merged_entries.extend(bundle["entry"])
            total += bundle.get("total", len(bundle["entry"]))
    
    return {
        "resourceType": "Bundle",
        "id": generate_fhir_id(),
        "type": "collection",
        "timestamp": format_fhir_datetime(datetime.utcnow()),
        "total": total,
        "entry": merged_entries
    }

def pretty_print_fhir(resource: Dict[str, Any]) -> str:
    """Pretty print FHIR resource as JSON"""
    return json.dumps(resource, indent=2, default=str)

# LOINC codes for common clinical observations
LOINC_CODES = {
    "readmission_risk": {
        "system": "http://loinc.org",
        "code": "75323-6",
        "display": "Readmission risk score"
    },
    "mortality_risk": {
        "system": "http://loinc.org",
        "code": "75324-4", 
        "display": "Mortality risk score"
    },
    "length_of_stay": {
        "system": "http://loinc.org",
        "code": "78033-5",
        "display": "Length of stay"
    },
    "clinical_note": {
        "system": "http://loinc.org",
        "code": "34109-9",
        "display": "Note"
    }
}

# SNOMED CT codes for common conditions
SNOMED_CODES = {
    "diabetes": {
        "system": "http://snomed.info/sct",
        "code": "73211009",
        "display": "Diabetes mellitus"
    },
    "hypertension": {
        "system": "http://snomed.info/sct", 
        "code": "38341003",
        "display": "Hypertensive disorder"
    },
    "heart_failure": {
        "system": "http://snomed.info/sct",
        "code": "84114007", 
        "display": "Heart failure"
    }
}
