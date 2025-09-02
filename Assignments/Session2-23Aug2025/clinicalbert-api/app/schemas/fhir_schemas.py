"""FHIR R4 Schema definitions and Pydantic models"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class FHIRResourceType(str, Enum):
    """FHIR Resource Types"""
    PATIENT = "Patient"
    OBSERVATION = "Observation"
    CONDITION = "Condition"
    DOCUMENT_REFERENCE = "DocumentReference"
    BUNDLE = "Bundle"
    MEDICATION_STATEMENT = "MedicationStatement"
    PROCEDURE = "Procedure"
    ENCOUNTER = "Encounter"

class ObservationStatus(str, Enum):
    """FHIR Observation Status"""
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"

class BundleType(str, Enum):
    """FHIR Bundle Types"""
    DOCUMENT = "document"
    MESSAGE = "message"
    TRANSACTION = "transaction"
    TRANSACTION_RESPONSE = "transaction-response"
    BATCH = "batch"
    BATCH_RESPONSE = "batch-response"
    HISTORY = "history"
    SEARCHSET = "searchset"
    COLLECTION = "collection"

# Base FHIR Models
class Coding(BaseModel):
    """FHIR Coding"""
    system: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    userSelected: Optional[bool] = None

class CodeableConcept(BaseModel):
    """FHIR CodeableConcept"""
    coding: Optional[List[Coding]] = None
    text: Optional[str] = None

class Reference(BaseModel):
    """FHIR Reference"""
    reference: Optional[str] = None
    type: Optional[str] = None
    identifier: Optional[Dict[str, Any]] = None
    display: Optional[str] = None

class Quantity(BaseModel):
    """FHIR Quantity"""
    value: Optional[float] = None
    comparator: Optional[str] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None

class Period(BaseModel):
    """FHIR Period"""
    start: Optional[datetime] = None
    end: Optional[datetime] = None

class Attachment(BaseModel):
    """FHIR Attachment"""
    contentType: Optional[str] = None
    language: Optional[str] = None
    data: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    hash: Optional[str] = None
    title: Optional[str] = None
    creation: Optional[datetime] = None

# Resource Models
class DocumentReference(BaseModel):
    """FHIR DocumentReference Resource"""
    resourceType: str = Field(default="DocumentReference", const=True)
    id: Optional[str] = None
    status: str = Field(..., description="current | superseded | entered-in-error")
    type: Optional[CodeableConcept] = None
    category: Optional[List[CodeableConcept]] = None
    subject: Optional[Reference] = None
    date: Optional[datetime] = None
    author: Optional[List[Reference]] = None
    authenticator: Optional[Reference] = None
    custodian: Optional[Reference] = None
    description: Optional[str] = None
    content: List[Dict[str, Any]] = Field(..., description="Document content")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['current', 'superseded', 'entered-in-error']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v

class Observation(BaseModel):
    """FHIR Observation Resource"""
    resourceType: str = Field(default="Observation", const=True)
    id: Optional[str] = None
    status: ObservationStatus = Field(..., description="Observation status")
    category: Optional[List[CodeableConcept]] = None
    code: CodeableConcept = Field(..., description="Type of observation")
    subject: Optional[Reference] = None
    encounter: Optional[Reference] = None
    effectiveDateTime: Optional[datetime] = None
    effectivePeriod: Optional[Period] = None
    issued: Optional[datetime] = None
    performer: Optional[List[Reference]] = None
    valueQuantity: Optional[Quantity] = None
    valueCodeableConcept: Optional[CodeableConcept] = None
    valueString: Optional[str] = None
    valueBoolean: Optional[bool] = None
    valueInteger: Optional[int] = None
    valueRange: Optional[Dict[str, Any]] = None
    valueRatio: Optional[Dict[str, Any]] = None
    valueSampledData: Optional[Dict[str, Any]] = None
    valueTime: Optional[str] = None
    valueDateTime: Optional[datetime] = None
    valuePeriod: Optional[Period] = None
    dataAbsentReason: Optional[CodeableConcept] = None
    interpretation: Optional[List[CodeableConcept]] = None
    note: Optional[List[Dict[str, Any]]] = None
    bodySite: Optional[CodeableConcept] = None
    method: Optional[CodeableConcept] = None
    component: Optional[List[Dict[str, Any]]] = None

class Condition(BaseModel):
    """FHIR Condition Resource"""
    resourceType: str = Field(default="Condition", const=True)
    id: Optional[str] = None
    clinicalStatus: Optional[CodeableConcept] = None
    verificationStatus: Optional[CodeableConcept] = None
    category: Optional[List[CodeableConcept]] = None
    severity: Optional[CodeableConcept] = None
    code: Optional[CodeableConcept] = None
    bodySite: Optional[List[CodeableConcept]] = None
    subject: Reference = Field(..., description="Who has the condition")
    encounter: Optional[Reference] = None
    onsetDateTime: Optional[datetime] = None
    onsetAge: Optional[Quantity] = None
    onsetPeriod: Optional[Period] = None
    onsetRange: Optional[Dict[str, Any]] = None
    onsetString: Optional[str] = None
    abatementDateTime: Optional[datetime] = None
    abatementAge: Optional[Quantity] = None
    abatementPeriod: Optional[Period] = None
    abatementRange: Optional[Dict[str, Any]] = None
    abatementString: Optional[str] = None
    recordedDate: Optional[datetime] = None
    recorder: Optional[Reference] = None
    asserter: Optional[Reference] = None
    stage: Optional[List[Dict[str, Any]]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    note: Optional[List[Dict[str, Any]]] = None

class BundleEntry(BaseModel):
    """FHIR Bundle Entry"""
    fullUrl: Optional[str] = None
    resource: Optional[Dict[str, Any]] = None
    search: Optional[Dict[str, Any]] = None
    request: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None

class Bundle(BaseModel):
    """FHIR Bundle Resource"""
    resourceType: str = Field(default="Bundle", const=True)
    id: Optional[str] = None
    type: BundleType = Field(..., description="Bundle type")
    timestamp: Optional[datetime] = None
    total: Optional[int] = None
    link: Optional[List[Dict[str, Any]]] = None
    entry: Optional[List[BundleEntry]] = None

# Request/Response Models
class TextInput(BaseModel):
    """Plain text input for processing"""
    text: str = Field(..., description="Clinical text to process")
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    encounter_id: Optional[str] = Field(None, description="Encounter identifier")

class FHIRInput(BaseModel):
    """FHIR resource input"""
    resource: Dict[str, Any] = Field(..., description="FHIR resource")
    
    @validator('resource')
    def validate_fhir_resource(cls, v):
        if 'resourceType' not in v:
            raise ValueError('FHIR resource must have resourceType')
        return v

class PredictionRequest(BaseModel):
    """Request for prediction endpoints"""
    input: Union[TextInput, FHIRInput] = Field(..., description="Input data")
    return_fhir: bool = Field(True, description="Return FHIR-compliant response")

class PredictionResponse(BaseModel):
    """Response from prediction endpoints"""
    prediction: Union[Dict[str, Any], float] = Field(..., description="Prediction result")
    confidence: Optional[float] = Field(None, description="Confidence score")
    fhir_resource: Optional[Dict[str, Any]] = Field(None, description="FHIR resource")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class EntityExtractionResponse(BaseModel):
    """Response from entity extraction"""
    entities: List[Dict[str, Any]] = Field(..., description="Extracted entities")
    fhir_resources: Optional[List[Dict[str, Any]]] = Field(None, description="FHIR resources")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class SearchRequest(BaseModel):
    """Request for similarity search"""
    query: Union[str, Dict[str, Any]] = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results to return")
    threshold: float = Field(0.5, ge=0.0, le=1.0, description="Similarity threshold")

class SearchResponse(BaseModel):
    """Response from similarity search"""
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
