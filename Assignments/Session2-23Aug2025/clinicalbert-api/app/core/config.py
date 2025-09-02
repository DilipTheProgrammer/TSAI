"""Application configuration settings"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ClinicalBERT API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # SMART on FHIR Configuration
    SMART_CLIENT_ID: Optional[str] = None
    SMART_CLIENT_SECRET: Optional[str] = None
    SMART_AUTHORIZATION_ENDPOINT: Optional[str] = None
    SMART_TOKEN_ENDPOINT: Optional[str] = None
    SMART_INTROSPECTION_ENDPOINT: Optional[str] = None
    SMART_REDIRECT_URI: Optional[str] = None
    
    # JWT Configuration
    JWT_ISSUER: str = "clinicalbert-api"
    JWT_AUDIENCE: str = "clinicalbert-users"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = []  # Empty list means no CORS allowed by default
    ALLOWED_METHODS: List[str] = ["GET", "POST"]
    ALLOWED_HEADERS: List[str] = ["Authorization", "Content-Type"]
    
    # Database
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # ClinicalBERT Model
    MODEL_NAME: str = "emilyalsentzer/Bio_ClinicalBERT"
    MODEL_CACHE_DIR: str = "./models"
    MAX_SEQUENCE_LENGTH: int = 512
    BATCH_SIZE: int = 16
    
    # FHIR
    FHIR_BASE_URL: Optional[str] = None
    FHIR_VERSION: str = "R4"
    
    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Security Configuration
    AUDIT_SALT: str = "audit-salt-change-in-production"
    GDPR_SALT: str = "gdpr-salt-change-in-production"
    DATA_RETENTION_DAYS: int = 2555  # 7 years for medical records
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    RATE_LIMIT_BURST: int = 100
    
    # PHI Anonymization
    ANONYMIZATION_LEVEL: str = "safe_harbor"  # safe_harbor or expert_determination
    
    # TLS Configuration
    TLS_CERT_FILE: Optional[str] = None
    TLS_KEY_FILE: Optional[str] = None
    FORCE_HTTPS: bool = True
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_CONCURRENT_SESSIONS: int = 5
    
    # Audit Logging
    AUDIT_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FILE: str = "audit.log"
    ENABLE_AUDIT_LOGGING: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Performance
    WORKERS: int = 1
    MAX_REQUESTS: int = 1000
    TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
