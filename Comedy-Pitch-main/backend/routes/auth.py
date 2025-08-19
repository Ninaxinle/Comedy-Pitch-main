from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from config.firebase_config import (
    get_firebase_web_config,
    verify_firebase_token,
    get_user_by_uid,
    list_all_users,
    create_custom_token
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class TokenVerificationResponse(BaseModel):
    message: str
    user: Dict[str, Any]

class CustomTokenRequest(BaseModel):
    uid: str

class CustomTokenResponse(BaseModel):
    customToken: str

class UserProfileResponse(BaseModel):
    uid: str
    email: Optional[str]
    emailVerified: bool
    disabled: bool
    metadata: Dict[str, Any]

class UsersListResponse(BaseModel):
    users: list
    count: int

# Dependency to verify Firebase token
async def verify_token_dependency(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Dependency to verify Firebase ID token from Authorization header"""
    logger.info(f"Auth header received: {authorization[:20] + '...' if authorization and len(authorization) > 20 else authorization}")
    
    if not authorization:
        logger.warning("No authorization header provided")
        raise HTTPException(status_code=401, detail="No token provided")
    
    if not authorization.startswith("Bearer "):
        logger.warning(f"Invalid authorization header format: {authorization[:50]}...")
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split("Bearer ")[1]
    logger.info(f"Token extracted (first 20 chars): {token[:20]}...")
    
    try:
        decoded_token = verify_firebase_token(token)
        logger.info(f"Token verified successfully for user: {decoded_token.get('email', 'unknown')}")
        return decoded_token
    except ValueError as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@router.get("/config")
async def get_config():
    """Get Firebase web configuration for client-side initialization"""
    try:
        config = get_firebase_web_config()
        return config
    except Exception as e:
        logger.error(f"Config retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Firebase configuration")

@router.post("/verify-token", response_model=TokenVerificationResponse)
async def verify_token(user: Dict[str, Any] = Depends(verify_token_dependency)):
    """Verify Firebase ID token"""
    return TokenVerificationResponse(
        message="Token is valid",
        user={
            "uid": user.get("uid"),
            "email": user.get("email"),
            "email_verified": user.get("email_verified", False)
        }
    )

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(user: Dict[str, Any] = Depends(verify_token_dependency)):
    """Get detailed user profile information"""
    try:
        user_info = get_user_by_uid(user["uid"])
        return UserProfileResponse(**user_info)
    except ValueError as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.get("/users", response_model=UsersListResponse)
async def get_users(user: Dict[str, Any] = Depends(verify_token_dependency)):
    """List all users (requires authentication)"""
    try:
        users_data = list_all_users()
        return UsersListResponse(**users_data)
    except ValueError as e:
        logger.error(f"Users list error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list users")

@router.post("/custom-token", response_model=CustomTokenResponse)
async def create_custom_token_endpoint(request: CustomTokenRequest):
    """Create a custom token for a user (testing purposes)"""
    try:
        custom_token = create_custom_token(request.uid)
        return CustomTokenResponse(customToken=custom_token)
    except ValueError as e:
        logger.error(f"Custom token creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create custom token")

# Health check for auth routes
@router.get("/health")
async def auth_health():
    """Health check for authentication routes"""
    return {
        "status": "healthy",
        "service": "authentication",
        "routes": [
            "/config",
            "/verify-token",
            "/profile", 
            "/users",
            "/custom-token",
            "/health"
        ]
    } 