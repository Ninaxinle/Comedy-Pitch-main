from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
import logging

from config.database import get_db
from routes.auth import verify_token_dependency
from models.models import User, Video, Like
from routes.videos import get_or_create_user

# Configure logging
logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class LikeResponse(BaseModel):
    message: str
    liked: bool
    like_count: int



# Routes
@router.post("/{video_id}/likes", response_model=LikeResponse)
async def like_video(
    video_id: int,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Like a video"""
    try:
        # Get or create user
        user = get_or_create_user(db, firebase_user)
        
        # Check if video exists
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Check if video is accessible (public or owned by user)
        if not video.is_public and video.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if user already liked this video
        existing_like = db.query(Like).filter(
            Like.user_id == user.id,
            Like.video_id == video_id
        ).first()
        
        if existing_like:
            return LikeResponse(
                message="Video already liked",
                liked=True,
                like_count=video.like_count
            )
        
        # Create new like
        new_like = Like(
            user_id=user.id,
            video_id=video_id,
            firebase_uid=firebase_user["uid"]
        )
        
        db.add(new_like)
        
        # Update video like count
        video.like_count += 1
        
        db.commit()
        
        return LikeResponse(
            message="Video liked successfully",
            liked=True,
            like_count=video.like_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking video: {e}")
        raise HTTPException(status_code=500, detail="Failed to like video")

@router.delete("/{video_id}/likes", response_model=LikeResponse)
async def unlike_video(
    video_id: int,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Remove like from a video"""
    try:
        # Get or create user
        user = get_or_create_user(db, firebase_user)
        
        # Check if video exists
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Find existing like
        existing_like = db.query(Like).filter(
            Like.user_id == user.id,
            Like.video_id == video_id
        ).first()
        
        if not existing_like:
            return LikeResponse(
                message="Video not liked by user",
                liked=False,
                like_count=video.like_count
            )
        
        # Remove like
        db.delete(existing_like)
        
        # Update video like count
        video.like_count = max(0, video.like_count - 1)  # Ensure it doesn't go negative
        
        db.commit()
        
        return LikeResponse(
            message="Like removed successfully",
            liked=False,
            like_count=video.like_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unliking video: {e}")
        raise HTTPException(status_code=500, detail="Failed to unlike video")

 