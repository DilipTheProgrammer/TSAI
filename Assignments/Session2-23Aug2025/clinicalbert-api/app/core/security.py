"""Security and authentication utilities with SMART on FHIR support"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request
import httpx
import logging
import hashlib
import secrets
import json
from urllib.parse import urlencode, parse_qs, urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SMART_SCOPES = {
    "patient/*.read": "Read access to all patient data",
    "patient/*.write": "Write access to all patient data", 
    "user/*.read": "Read access to user data",
    "user/*.write": "Write access to user data",
    "system/*.read": "System-level read access",
    "system/*.write": "System-level write access",
    "launch": "Launch context",
    "launch/patient": "Patient launch context",
    "launch/encounter": "Encounter launch context",
    "offline_access": "Offline access for refresh tokens",
    "openid": "OpenID Connect",
    "profile": "User profile access",
    "fhirUser": "FHIR user identity"
}

class SMARTAuthenticator:
    """SMART on FHIR OAuth 2.0 authenticator"""
    
    def __init__(self):
        self.client_id = settings.SMART_CLIENT_ID
        self.client_secret = settings.SMART_CLIENT_SECRET
        self.authorization_endpoint = settings.SMART_AUTHORIZATION_ENDPOINT
        self.token_endpoint = settings.SMART_TOKEN_ENDPOINT
        self.introspection_endpoint = settings.SMART_INTROSPECTION_ENDPOINT
        self.redirect_uri = settings.SMART_REDIRECT_URI
        
    async def get_authorization_url(
        self, 
        scopes: List[str], 
        state: Optional[str] = None,
        launch: Optional[str] = None
    ) -> str:
        """Generate SMART on FHIR authorization URL"""
        
        if not state:
            state = secrets.token_urlsafe(32)
            
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "aud": settings.FHIR_BASE_URL
        }
        
        if launch:
            params["launch"] = launch
            
        return f"{self.authorization_endpoint}?{urlencode(params)}"
    
    async def exchange_code_for_token(
        self, 
        authorization_code: str, 
        state: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "grant_type": "authorization_code",
                    "code": authorization_code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                response = await client.post(
                    self.token_endpoint,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Token exchange failed: {response.text}"
                    )
                
                token_data = response.json()
                
                # Validate token response
                required_fields = ["access_token", "token_type"]
                for field in required_fields:
                    if field not in token_data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Missing required field: {field}"
                        )
                
                return token_data
                
        except httpx.RequestError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
    
    async def introspect_token(self, access_token: str) -> Dict[str, Any]:
        """Introspect access token to get user info and scopes"""
        
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "token": access_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                response = await client.post(
                    self.introspection_endpoint,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token introspection failed"
                    )
                
                introspection_data = response.json()
                
                if not introspection_data.get("active", False):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token is not active"
                    )
                
                return introspection_data
                
        except httpx.RequestError as e:
            logger.error(f"HTTP error during token introspection: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[List[str]] = None
) -> str:
    """Create JWT access token with SMART on FHIR claims"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": settings.JWT_ISSUER,
        "aud": settings.FHIR_BASE_URL
    })
    
    if scopes:
        to_encode["scope"] = " ".join(scopes)
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def verify_token(token: str, required_scopes: Optional[List[str]] = None) -> Dict[str, Any]:
    """Verify JWT token and return user data with scope validation"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Validate token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        # Validate required scopes
        if required_scopes:
            token_scopes = payload.get("scope", "").split()
            if not all(scope in token_scopes for scope in required_scopes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        return {
            "user_id": user_id,
            "scopes": payload.get("scope", "").split(),
            "exp": payload.get("exp"),
            "patient_id": payload.get("patient"),
            "encounter_id": payload.get("encounter"),
            "fhir_user": payload.get("fhirUser")
        }
        
    except JWTError as e:
        logger.error(f"JWT validation error: {e}")
        raise credentials_exception

class AuditLogger:
    """Audit logger for HIPAA compliance"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger("audit")
        
    async def log_access(
        self,
        user_id: str,
        action: str,
        resource: str,
        patient_id: Optional[str] = None,
        request: Optional[Request] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log access to patient data for audit trail"""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "patient_id": patient_id,
            "success": success,
            "ip_address": request.client.host if request else None,
            "user_agent": request.headers.get("user-agent") if request else None,
            "details": details or {}
        }
        
        # Hash sensitive data
        if patient_id:
            audit_entry["patient_id_hash"] = self._hash_identifier(patient_id)
        
        self.audit_logger.info(json.dumps(audit_entry))
    
    async def log_phi_access(
        self,
        user_id: str,
        phi_type: str,
        patient_id: str,
        request: Request,
        purpose: str = "treatment"
    ):
        """Log PHI access specifically"""
        
        await self.log_access(
            user_id=user_id,
            action="phi_access",
            resource=phi_type,
            patient_id=patient_id,
            request=request,
            details={
                "phi_type": phi_type,
                "purpose": purpose,
                "minimum_necessary": True
            }
        )
    
    def _hash_identifier(self, identifier: str) -> str:
        """Hash patient identifiers for audit logs"""
        return hashlib.sha256(f"{identifier}{settings.AUDIT_SALT}".encode()).hexdigest()

class PHIAnonymizer:
    """PHI anonymization for HIPAA compliance"""
    
    def __init__(self):
        self.phi_patterns = {
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            "mrn": r'\bMRN:?\s*\d+\b',
            "account": r'\bAccount:?\s*\d+\b'
        }
    
    def anonymize_text(self, text: str, anonymization_level: str = "safe_harbor") -> str:
        """Anonymize PHI in clinical text"""
        
        if anonymization_level == "safe_harbor":
            return self._safe_harbor_anonymization(text)
        elif anonymization_level == "expert_determination":
            return self._expert_determination_anonymization(text)
        else:
            return text
    
    def _safe_harbor_anonymization(self, text: str) -> str:
        """Apply HIPAA Safe Harbor anonymization"""
        import re
        
        anonymized_text = text
        
        # Replace direct identifiers
        for phi_type, pattern in self.phi_patterns.items():
            anonymized_text = re.sub(pattern, f"[{phi_type.upper()}]", anonymized_text, flags=re.IGNORECASE)
        
        # Remove specific dates (keep year if > 89 years old)
        anonymized_text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '[DATE]', anonymized_text)
        
        # Remove ages > 89
        anonymized_text = re.sub(r'\b(9[0-9]|[1-9]\d{2,})\s*(?:year|yr|y\.o\.)', '[AGE>89]', anonymized_text, flags=re.IGNORECASE)
        
        return anonymized_text
    
    def _expert_determination_anonymization(self, text: str) -> str:
        """Apply expert determination anonymization (more permissive)"""
        # This would involve more sophisticated NLP-based anonymization
        # For now, apply basic anonymization
        return self._safe_harbor_anonymization(text)

class GDPRCompliance:
    """GDPR compliance utilities"""
    
    def __init__(self):
        self.data_retention_days = settings.DATA_RETENTION_DAYS
        
    async def log_consent(
        self,
        user_id: str,
        patient_id: str,
        consent_type: str,
        granted: bool,
        purpose: str
    ):
        """Log patient consent for data processing"""
        
        consent_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "patient_id": self._hash_patient_id(patient_id),
            "consent_type": consent_type,
            "granted": granted,
            "purpose": purpose,
            "legal_basis": "consent" if granted else "withdrawn"
        }
        
        # Store consent record (in production, this would go to a database)
        logger.info(f"GDPR Consent: {json.dumps(consent_entry)}")
    
    async def handle_data_subject_request(
        self,
        request_type: str,
        patient_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle GDPR data subject requests (access, rectification, erasure)"""
        
        if request_type == "access":
            return await self._handle_access_request(patient_id, user_id)
        elif request_type == "rectification":
            return await self._handle_rectification_request(patient_id, user_id)
        elif request_type == "erasure":
            return await self._handle_erasure_request(patient_id, user_id)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    async def _handle_access_request(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        """Handle data access request"""
        # In production, this would query all systems for patient data
        return {
            "request_type": "access",
            "patient_id": patient_id,
            "processed_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data_categories": ["clinical_notes", "predictions", "audit_logs"],
            "status": "completed"
        }
    
    async def _handle_rectification_request(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        """Handle data rectification request"""
        return {
            "request_type": "rectification",
            "patient_id": patient_id,
            "processed_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending_review"
        }
    
    async def _handle_erasure_request(self, patient_id: str, user_id: str) -> Dict[str, Any]:
        """Handle data erasure request (right to be forgotten)"""
        return {
            "request_type": "erasure",
            "patient_id": patient_id,
            "processed_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending_legal_review"
        }
    
    def _hash_patient_id(self, patient_id: str) -> str:
        """Hash patient ID for privacy"""
        return hashlib.sha256(f"{patient_id}{settings.GDPR_SALT}".encode()).hexdigest()

class RateLimiter:
    """Rate limiter for API protection"""
    
    def __init__(self):
        self.requests = {}
        self.window_size = 3600  # 1 hour
        self.max_requests = 1000  # per hour per user
    
    async def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Check if user has exceeded rate limit"""
        
        current_time = datetime.utcnow().timestamp()
        key = f"{user_id}:{endpoint}"
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < self.window_size
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[key].append(current_time)
        return True

# Global instances
audit_logger = AuditLogger()
phi_anonymizer = PHIAnonymizer()
gdpr_compliance = GDPRCompliance()
rate_limiter = RateLimiter()
smart_authenticator = SMARTAuthenticator()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)
