"""
FastAPI dependencies and middleware for all services
Handles authentication, rate limiting, and common request processing
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import jwt
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

from .base_config import get_config, db_manager
from ..interfaces.core_types import User, GuardianPermission

# Security
security = HTTPBearer()

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.max_requests = 120  # per minute per IP
        self.window_seconds = 60
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is within rate limit"""
        now = time.time()
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if now - req_time < self.window_seconds
            ]
        else:
            self.requests[client_ip] = []
        
        # Check limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()

async def verify_rate_limit(request: Request):
    """Dependency to check rate limiting"""
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 120 requests per minute."
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Extract and validate user from JWT token"""
    config = get_config()
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            config.jwt_secret,
            algorithms=[config.jwt_algorithm]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Get user from database
        user_doc = db_manager.get_collection("users").document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        # Remove sensitive data
        if "password_hash" in user_data:
            del user_data["password_hash"]
        return User(**user_data)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_optional_user(
    request: Request
) -> Optional[User]:
    """Get user if authenticated, otherwise return None"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=auth_header.split(" ")[1]
        )
        return await get_current_user(credentials)
    except HTTPException:
        return None

async def verify_guardian_permission(
    user: User = Depends(get_current_user),
    required_permission: GuardianPermission = GuardianPermission.VIEW_ONLY
) -> User:
    """Verify user has guardian permissions"""
    # Check if user is a guardian
    guardian_doc = db_manager.get_collection("guardians").document(user.uid).get()
    if not guardian_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guardian access required"
        )
    
    guardian_data = guardian_doc.to_dict()
    user_permission = GuardianPermission(guardian_data.get("permission_level", "view_only"))
    
    # Check permission hierarchy
    permission_hierarchy = {
        GuardianPermission.VIEW_ONLY: 1,
        GuardianPermission.TASK_EDIT: 2,
        GuardianPermission.CHAT_SEND: 3
    }
    
    if permission_hierarchy[user_permission] < permission_hierarchy[required_permission]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {required_permission.value}"
        )
    
    return user

def create_jwt_token(user_id: str, additional_claims: Dict[str, Any] = None) -> str:
    """Create JWT token for user"""
    config = get_config()
    
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=config.jwt_expiration_hours)
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    return jwt.encode(payload, config.jwt_secret, algorithm=config.jwt_algorithm)

def setup_middleware(app):
    """Setup common middleware for FastAPI apps"""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted hosts (configure for production)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure properly for production
    )
    
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Add security headers to all responses"""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests for monitoring"""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log to structured format for Cloud Logging
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "client_ip": request.client.host
        }
        
        print(json.dumps(log_data))  # Replace with proper logging
        return response