"""Authentication endpoints for SMART on FHIR"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from typing import Dict, Any, List, Optional
import logging
from urllib.parse import parse_qs, urlparse

from app.core.security import smart_authenticator, create_access_token, audit_logger
from app.core.config import settings
from app.schemas.auth_schemas import (
    AuthorizationRequest, TokenRequest, TokenResponse, 
    IntrospectionRequest, IntrospectionResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    aud: str,
    launch: Optional[str] = None,
    request: Request = None
):
    """
    SMART on FHIR authorization endpoint
    
    Initiates OAuth 2.0 authorization flow with SMART on FHIR extensions
    """
    try:
        logger.info(f"Authorization request from client: {client_id}")
        
        # Validate request parameters
        if response_type != "code":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only 'code' response type is supported"
            )
        
        if client_id != settings.SMART_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client_id"
            )
        
        # Validate scopes
        requested_scopes = scope.split()
        from app.core.security import SMART_SCOPES
        invalid_scopes = [s for s in requested_scopes if s not in SMART_SCOPES]
        if invalid_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scopes: {invalid_scopes}"
            )
        
        # Generate authorization URL
        auth_url = await smart_authenticator.get_authorization_url(
            scopes=requested_scopes,
            state=state,
            launch=launch
        )
        
        # Log authorization attempt
        await audit_logger.log_access(
            user_id="system",
            action="authorization_request",
            resource="oauth2/authorize",
            request=request,
            details={
                "client_id": client_id,
                "scopes": requested_scopes,
                "launch": launch
            }
        )
        
        # In a real implementation, this would redirect to an authorization server
        # For demo purposes, we'll return a mock authorization code
        mock_code = "mock_authorization_code_12345"
        callback_url = f"{redirect_uri}?code={mock_code}&state={state}"
        
        return RedirectResponse(url=callback_url)
        
    except Exception as e:
        logger.error(f"Authorization error: {e}")
        raise

@router.post("/token", response_model=TokenResponse)
async def token(
    grant_type: str,
    code: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    refresh_token: Optional[str] = None,
    request: Request = None
):
    """
    SMART on FHIR token endpoint
    
    Exchanges authorization code for access token
    """
    try:
        logger.info(f"Token request with grant_type: {grant_type}")
        
        if grant_type == "authorization_code":
            # Validate required parameters
            if not all([code, redirect_uri, client_id, client_secret]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing required parameters for authorization_code grant"
                )
            
            # Validate client credentials
            if client_id != settings.SMART_CLIENT_ID or client_secret != settings.SMART_CLIENT_SECRET:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid client credentials"
                )
            
            # In production, validate the authorization code
            # For demo, we'll accept the mock code
            if code != "mock_authorization_code_12345":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid authorization code"
                )
            
            # Create access token with SMART claims
            token_data = {
                "sub": "user123",
                "patient": "Patient/123",
                "encounter": "Encounter/456",
                "fhirUser": "Practitioner/789"
            }
            
            scopes = ["patient/*.read", "user/*.read", "launch/patient"]
            access_token = create_access_token(
                data=token_data,
                scopes=scopes
            )
            
            # Log successful token exchange
            await audit_logger.log_access(
                user_id=token_data["sub"],
                action="token_exchange",
                resource="oauth2/token",
                request=request,
                details={
                    "grant_type": grant_type,
                    "scopes": scopes,
                    "patient_id": token_data["patient"]
                }
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                scope=" ".join(scopes),
                patient=token_data["patient"],
                encounter=token_data["encounter"],
                fhirUser=token_data["fhirUser"]
            )
            
        elif grant_type == "refresh_token":
            # Handle refresh token flow
            if not refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing refresh_token parameter"
                )
            
            # In production, validate and exchange refresh token
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Refresh token flow not implemented"
            )
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported grant_type: {grant_type}"
            )
            
    except Exception as e:
        logger.error(f"Token exchange error: {e}")
        raise

@router.post("/introspect", response_model=IntrospectionResponse)
async def introspect(
    token: str,
    client_id: str,
    client_secret: str,
    request: Request = None
):
    """
    Token introspection endpoint (RFC 7662)
    
    Returns information about the provided token
    """
    try:
        logger.info("Token introspection request")
        
        # Validate client credentials
        if client_id != settings.SMART_CLIENT_ID or client_secret != settings.SMART_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid client credentials"
            )
        
        # Introspect token
        try:
            from app.core.security import verify_token
            token_data = await verify_token(token)
            
            # Log introspection
            await audit_logger.log_access(
                user_id=token_data["user_id"],
                action="token_introspection",
                resource="oauth2/introspect",
                request=request
            )
            
            return IntrospectionResponse(
                active=True,
                client_id=client_id,
                username=token_data["user_id"],
                scope=" ".join(token_data["scopes"]),
                exp=token_data["exp"],
                sub=token_data["user_id"],
                patient=token_data.get("patient_id"),
                fhirUser=token_data.get("fhir_user")
            )
            
        except HTTPException:
            # Token is invalid or expired
            return IntrospectionResponse(active=False)
            
    except Exception as e:
        logger.error(f"Token introspection error: {e}")
        raise

@router.get("/userinfo")
async def userinfo(
    current_user: Dict[str, Any] = Depends(lambda: {"user_id": "user123"}),
    request: Request = None
):
    """
    OpenID Connect UserInfo endpoint
    
    Returns user information for the authenticated user
    """
    try:
        logger.info(f"UserInfo request for user: {current_user['user_id']}")
        
        # Log userinfo access
        await audit_logger.log_access(
            user_id=current_user["user_id"],
            action="userinfo_access",
            resource="oauth2/userinfo",
            request=request
        )
        
        # Return user information
        return {
            "sub": current_user["user_id"],
            "name": "Dr. John Smith",
            "given_name": "John",
            "family_name": "Smith",
            "email": "john.smith@hospital.com",
            "fhirUser": "Practitioner/789",
            "profile": "https://fhir.hospital.com/Practitioner/789"
        }
        
    except Exception as e:
        logger.error(f"UserInfo error: {e}")
        raise

@router.post("/logout")
async def logout(
    token: str,
    request: Request = None
):
    """
    Logout endpoint
    
    Revokes the provided access token
    """
    try:
        logger.info("Logout request")
        
        # In production, add token to revocation list
        # For demo, just log the logout
        
        await audit_logger.log_access(
            user_id="unknown",
            action="logout",
            resource="oauth2/logout",
            request=request,
            details={"token_revoked": True}
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise
