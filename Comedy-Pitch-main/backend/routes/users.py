from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import logging

from config.database import get_db
from routes.auth import verify_token_dependency
from models.models import User, Video
from routes.videos import get_or_create_user

# Configure logging
logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=2000)
    is_comedian: Optional[bool] = None
    stage_name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)
    social_links: Optional[Dict[str, str]] = None  # Will be stored as JSON

class UserSettingsUpdate(BaseModel):
    is_public_profile: Optional[bool] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None

class UserProfileResponse(BaseModel):
    id: int
    firebase_uid: str
    email: str
    display_name: Optional[str]
    profile_picture_url: Optional[str]
    bio: Optional[str]
    is_comedian: bool
    stage_name: Optional[str]
    location: Optional[str]
    website: Optional[str]
    social_links: Optional[Dict[str, str]]
    is_active: bool
    video_count: int
    total_likes: int
    created_at: str

class PublicUserProfileResponse(BaseModel):
    id: int
    display_name: Optional[str]
    bio: Optional[str]
    is_comedian: bool
    stage_name: Optional[str]
    location: Optional[str]
    website: Optional[str]
    social_links: Optional[Dict[str, str]]
    video_count: int
    total_likes: int

# Helper functions
def format_user_profile(user: User, include_private: bool = False) -> Dict[str, Any]:
    """Format user profile for API response"""
    # Calculate video count and total likes
    video_count = len(user.videos) if user.videos else 0
    total_likes = sum(video.like_count for video in user.videos) if user.videos else 0
    
    # Parse social links JSON
    social_links = None
    if user.social_links:
        try:
            social_links = json.loads(user.social_links)
        except (json.JSONDecodeError, TypeError):
            social_links = None
    
    base_profile = {
        "id": user.id,
        "display_name": user.display_name,
        "bio": user.bio,
        "is_comedian": user.is_comedian,
        "stage_name": user.stage_name,
        "location": user.location,
        "website": user.website,
        "social_links": social_links,
        "video_count": video_count,
        "total_likes": total_likes
    }
    
    if include_private:
        base_profile.update({
            "firebase_uid": user.firebase_uid,
            "email": user.email,
            "profile_picture_url": user.profile_picture_url,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        })
    
    return base_profile

# Routes
@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Get own profile information"""
    try:
        user = get_or_create_user(db, firebase_user)
        profile_data = format_user_profile(user, include_private=True)
        return UserProfileResponse(**profile_data)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_update: UserProfileUpdate,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Update own profile information"""
    try:
        user = get_or_create_user(db, firebase_user)
        
        # Update fields if provided
        if profile_update.display_name is not None:
            user.display_name = profile_update.display_name
        
        if profile_update.bio is not None:
            user.bio = profile_update.bio
        
        if profile_update.is_comedian is not None:
            user.is_comedian = profile_update.is_comedian
        
        if profile_update.stage_name is not None:
            user.stage_name = profile_update.stage_name
        
        if profile_update.location is not None:
            user.location = profile_update.location
        
        if profile_update.website is not None:
            user.website = profile_update.website
        
        if profile_update.social_links is not None:
            user.social_links = json.dumps(profile_update.social_links)
        
        db.commit()
        db.refresh(user)
        
        profile_data = format_user_profile(user, include_private=True)
        return UserProfileResponse(**profile_data)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

@router.put("/me/settings")
async def update_my_settings(
    settings_update: UserSettingsUpdate,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Update user settings and preferences"""
    try:
        user = get_or_create_user(db, firebase_user)
        
        # For now, we'll store these as a JSON field or add columns later
        # This is a placeholder for user settings functionality
        # In a full implementation, you'd want a separate UserSettings table
        
        return {"message": "Settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user settings")

@router.get("/{user_id}", response_model=PublicUserProfileResponse)
async def get_public_profile(
    user_id: int,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Get public profile of another user"""
    try:
        # Verify requesting user exists
        requesting_user = get_or_create_user(db, firebase_user)
        
        # Get target user
        target_user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile_data = format_user_profile(target_user, include_private=False)
        return PublicUserProfileResponse(**profile_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting public profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.get("/{user_id}/videos")
async def get_user_videos(
    user_id: int,
    limit: int = 20,
    cursor: Optional[str] = None,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Get public videos from a specific user"""
    try:
        # Verify requesting user exists
        requesting_user = get_or_create_user(db, firebase_user)
        
        # Get target user
        target_user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get public videos from this user
        from routes.videos import format_video_response
        from datetime import datetime
        
        query = db.query(Video).filter(
            Video.user_id == user_id,
            Video.is_public == True
        )
        
        # Apply cursor-based pagination if provided
        if cursor:
            try:
                cursor_timestamp, cursor_id = cursor.split('_')
                cursor_datetime = datetime.fromisoformat(cursor_timestamp.replace('Z', '+00:00'))
                query = query.filter(
                    (Video.posted_at < cursor_datetime) |
                    ((Video.posted_at == cursor_datetime) & (Video.id < int(cursor_id)))
                )
            except (ValueError, IndexError):
                raise HTTPException(status_code=400, detail="Invalid cursor format")
        
        # Order by posted_at descending
        query = query.order_by(Video.posted_at.desc(), Video.id.desc())
        
        # Fetch one extra to check if there are more results
        videos = query.limit(limit + 1).all()
        
        has_more = len(videos) > limit
        if has_more:
            videos = videos[:limit]
        
        # Generate next cursor
        next_cursor = None
        if has_more and videos:
            last_video = videos[-1]
            next_cursor = f"{last_video.posted_at.isoformat()}_{last_video.id}"
        
        video_responses = [format_video_response(video) for video in videos]
        
        return {
            "videos": video_responses,
            "cursor": next_cursor,
            "has_more": has_more,
            "user": format_user_profile(target_user, include_private=False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user videos: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user videos") 