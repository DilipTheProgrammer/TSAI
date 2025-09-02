"""Authentication schema definitions"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AuthorizationRequest(BaseModel):
    """OAuth 2.0 authorization request"""
    response_type: str = Field(..., description="Must be 'code'")
    client_id: str = Field(..., description="Client identifier")
    redirect_uri: str = Field(..., description="Redirect URI")
    scope: str = Field(..., description="Requested scopes")
    state: str = Field(..., description="State parameter")
    aud: str = Field(..., description="FHIR server URL")
    launch: Optional[str] = Field(None, description="Launch context")

class TokenRequest(BaseModel):
    """OAuth 2.0 token request"""
    grant_type: str = Field(..., description="Grant type")
    code: Optional[str] = Field(None, description="Authorization code")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI")
    client_id: Optional[str] = Field(None, description="Client identifier")
    client_secret: Optional[str] = Field(None, description="Client secret")
    refresh_token: Optional[str] = Field(None, description="Refresh token")

class TokenResponse(BaseModel):
    """OAuth 2.0 token response"""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    scope: str = Field(..., description="Granted scopes")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    patient: Optional[str] = Field(None, description="Patient context")
    encounter: Optional[str] = Field(None, description="Encounter context")
    fhirUser: Optional[str] = Field(None, description="FHIR user reference")

class IntrospectionRequest(BaseModel):
    """Token introspection request"""
    token: str = Field(..., description="Token to introspect")
    client_id: str = Field(..., description="Client identifier")
    client_secret: str = Field(..., description="Client secret")

class IntrospectionResponse(BaseModel):
    """Token introspection response"""
    active: bool = Field(..., description="Whether token is active")
    client_id: Optional[str] = Field(None, description="Client identifier")
    username: Optional[str] = Field(None, description="Username")
    scope: Optional[str] = Field(None, description="Token scopes")
    exp: Optional[int] = Field(None, description="Expiration timestamp")
    sub: Optional[str] = Field(None, description="Subject identifier")
    patient: Optional[str] = Field(None, description="Patient context")
    fhirUser: Optional[str] = Field(None, description="FHIR user reference")
