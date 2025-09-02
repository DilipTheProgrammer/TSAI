"""Security middleware for request processing"""

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import time
import logging
from typing import Callable
import json

from app.core.security import audit_logger, rate_limiter, phi_anonymizer
from app.core.config import settings

logger = logging.getLogger(__name__)

async def security_middleware(request: Request, call_next: Callable) -> Response:
    """Security middleware for all requests"""
    
    start_time = time.time()
    
    try:
        # Force HTTPS in production
        if settings.FORCE_HTTPS and settings.ENVIRONMENT == "production":
            if request.url.scheme != "https":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="HTTPS required"
                )
        
        # Add security headers
        response = await call_next(request)
        
        # Add security headers to response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Log request for audit
        processing_time = time.time() - start_time
        
        if settings.ENABLE_AUDIT_LOGGING:
            await audit_logger.log_access(
                user_id=getattr(request.state, "user_id", "anonymous"),
                action=request.method,
                resource=str(request.url.path),
                request=request,
                success=response.status_code < 400,
                details={
                    "status_code": response.status_code,
                    "processing_time": processing_time,
                    "content_length": response.headers.get("content-length", 0)
                }
            )
        
        return response
        
    except Exception as e:
        # Log security errors
        logger.error(f"Security middleware error: {e}")
        
        if settings.ENABLE_AUDIT_LOGGING:
            await audit_logger.log_access(
                user_id=getattr(request.state, "user_id", "anonymous"),
                action=request.method,
                resource=str(request.url.path),
                request=request,
                success=False,
                details={"error": str(e)}
            )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Security error"}
        )

async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware"""
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/docs", "/redoc"]:
        return await call_next(request)
    
    # Get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", request.client.host)
    endpoint = request.url.path
    
    # Check rate limit
    if not await rate_limiter.check_rate_limit(user_id, endpoint):
        logger.warning(f"Rate limit exceeded for user {user_id} on endpoint {endpoint}")
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded",
                "retry_after": 3600
            },
            headers={"Retry-After": "3600"}
        )
    
    return await call_next(request)

async def phi_protection_middleware(request: Request, call_next: Callable) -> Response:
    """PHI protection middleware"""
    
    # Process request
    response = await call_next(request)
    
    # Check if response contains PHI and anonymize if needed
    if (
        response.status_code == 200 and 
        "application/json" in response.headers.get("content-type", "") and
        settings.ANONYMIZATION_LEVEL != "none"
    ):
        # This is a simplified example - in production, you'd need more sophisticated PHI detection
        try:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Parse JSON and check for PHI
            if body:
                content = json.loads(body.decode())
                
                # Anonymize text fields that might contain PHI
                anonymized_content = _anonymize_response_content(content)
                
                # Create new response with anonymized content
                return JSONResponse(
                    content=anonymized_content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        
        except Exception as e:
            logger.error(f"PHI protection error: {e}")
            # Return original response if anonymization fails
            pass
    
    return response

def _anonymize_response_content(content: dict) -> dict:
    """Anonymize PHI in response content"""
    
    if isinstance(content, dict):
        anonymized = {}
        for key, value in content.items():
            if isinstance(value, str) and _contains_potential_phi(key):
                anonymized[key] = phi_anonymizer.anonymize_text(value)
            elif isinstance(value, (dict, list)):
                anonymized[key] = _anonymize_response_content(value)
            else:
                anonymized[key] = value
        return anonymized
    
    elif isinstance(content, list):
        return [_anonymize_response_content(item) for item in content]
    
    else:
        return content

def _contains_potential_phi(field_name: str) -> bool:
    """Check if field name suggests it might contain PHI"""
    phi_indicators = [
        "text", "note", "narrative", "description", "comment",
        "name", "address", "phone", "email", "ssn", "mrn"
    ]
    
    field_lower = field_name.lower()
    return any(indicator in field_lower for indicator in phi_indicators)
