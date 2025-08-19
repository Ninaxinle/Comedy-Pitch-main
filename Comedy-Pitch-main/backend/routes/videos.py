from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from config.database import get_db
from config.firebase_config import verify_firebase_token
from routes.auth import verify_token_dependency
from models.models import User, Video, AnalyticsData
from storage.factory import get_storage
from storage.base import UploadMetadata

# Configure logging
logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for requests/responses
class PresignedUploadRequest(BaseModel):
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type of the file")
    content_length: Optional[int] = Field(None, description="File size in bytes")

class PresignedUploadResponse(BaseModel):
    upload_url: str
    storage_key: str
    expires_in: int
    fields: Optional[Dict[str, str]] = None

class VideoCreateRequest(BaseModel):
    storage_key: str = Field(..., description="Storage key from presigned upload")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    file_type: str = Field(..., description="'video' or 'audio'")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    venue_name: Optional[str] = Field(None, max_length=255)
    performance_date: Optional[datetime] = None
    set_duration: Optional[float] = Field(None, description="Total set duration in seconds")
    audience_size: Optional[int] = Field(None, ge=0)
    is_public: bool = Field(True, description="Whether the video is publicly visible")

class VideoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration: Optional[float]
    file_type: str
    storage_url: Optional[str]
    thumbnail_url: Optional[str]
    is_public: bool
    view_count: int
    like_count: int
    comment_count: int
    venue_name: Optional[str]
    performance_date: Optional[datetime]
    created_at: datetime
    posted_at: datetime
    user: Dict[str, Any]

class VideoListResponse(BaseModel):
    videos: List[VideoResponse]
    cursor: Optional[str] = None
    has_more: bool

class AnalyticsResponse(BaseModel):
    transcript: Optional[List[Dict[str, Any]]] = None
    overall_funniness_score: Optional[float] = None
    laughter_timestamps: Optional[List[Dict[str, Any]]] = None
    processing_status: str

# Helper functions
def get_or_create_user(db: Session, firebase_user: Dict[str, Any]) -> User:
    """Get or create user in database from Firebase user data"""
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    
    if not user:
        user = User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user.get("email", ""),
            display_name=firebase_user.get("name"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def generate_storage_key(filename: str, user_id: int) -> str:
    """Generate a unique storage key for the file"""
    file_extension = filename.split('.')[-1] if '.' in filename else ''
    unique_id = str(uuid.uuid4())
    return f"videos/{user_id}/{unique_id}.{file_extension}"

def format_video_response(video: Video) -> VideoResponse:
    """Format video for API response"""
    storage = get_storage()
    storage_url = storage.get_public_url(video.storage_key) if video.storage_key else None
    
    return VideoResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        duration=video.duration,
        file_type=video.file_type,
        storage_url=storage_url,
        thumbnail_url=video.thumbnail_url,
        is_public=video.is_public,
        view_count=video.view_count,
        like_count=video.like_count,
        comment_count=video.comment_count,
        venue_name=video.venue_name,
        performance_date=video.performance_date,
        created_at=video.created_at,
        posted_at=video.posted_at,
        user={
            "id": video.user.id,
            "display_name": video.user.display_name,
            "stage_name": video.user.stage_name,
            "is_comedian": video.user.is_comedian
        }
    )

# Routes
@router.post("/uploads/presign", response_model=PresignedUploadResponse)
async def get_presigned_upload_url(
    request: PresignedUploadRequest,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Get presigned URL for video/audio upload"""
    try:
        # Get or create user
        user = get_or_create_user(db, firebase_user)
        
        # Generate storage key
        storage_key = generate_storage_key(request.filename, user.id)
        
        # Get storage backend and generate presigned URL
        storage = get_storage()
        metadata = UploadMetadata(
            filename=request.filename,
            content_type=request.content_type,
            content_length=request.content_length
        )
        
        presigned_response = storage.generate_presigned_url(
            key=storage_key,
            metadata=metadata
        )
        
        return PresignedUploadResponse(
            upload_url=presigned_response.upload_url,
            storage_key=presigned_response.storage_key,
            expires_in=presigned_response.expires_in,
            fields=presigned_response.fields
        )
        
    except Exception as e:
        logger.error(f"Error generating presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")

@router.post("/", response_model=VideoResponse)
async def create_video(
    video_data: VideoCreateRequest,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Create video metadata after successful upload"""
    try:
        # Get or create user
        user = get_or_create_user(db, firebase_user)
        
        # Verify the file was uploaded by checking if it exists in storage
        storage = get_storage()
        if not storage.file_exists(video_data.storage_key):
            raise HTTPException(status_code=400, detail="File not found in storage")
        
        # Get file metadata from storage
        file_metadata = storage.get_file_metadata(video_data.storage_key)
        
        # Create video record
        video = Video(
            user_id=user.id,
            firebase_uid=firebase_user["uid"],
            title=video_data.title,
            description=video_data.description,
            duration=video_data.duration,
            file_type=video_data.file_type,
            storage_key=video_data.storage_key,
            is_public=video_data.is_public,
            venue_name=video_data.venue_name,
            performance_date=video_data.performance_date,
            set_duration=video_data.set_duration,
            audience_size=video_data.audience_size,
            mime_type=file_metadata.get("content_type") if file_metadata else None,
            file_size=file_metadata.get("size") if file_metadata else None
        )
        
        db.add(video)
        db.commit()
        db.refresh(video)
        
        return format_video_response(video)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        raise HTTPException(status_code=500, detail="Failed to create video")

@router.get("/", response_model=VideoListResponse)
async def list_videos(
    feed: Optional[str] = Query(None, description="Feed type: 'home' for personalized feed"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(20, ge=1, le=100, description="Number of videos to return"),
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """List videos with pagination"""
    try:
        user = get_or_create_user(db, firebase_user)
        
        if feed == "home":
            # Personalized feed - for now, just return public videos ordered by posted_at
            query = db.query(Video).filter(Video.is_public == True)
        else:
            # User's own videos
            query = db.query(Video).filter(Video.user_id == user.id)
        
        # Apply cursor-based pagination
        if cursor:
            try:
                # Cursor format: timestamp_id
                cursor_timestamp, cursor_id = cursor.split('_')
                cursor_datetime = datetime.fromisoformat(cursor_timestamp.replace('Z', '+00:00'))
                query = query.filter(
                    (Video.posted_at < cursor_datetime) |
                    ((Video.posted_at == cursor_datetime) & (Video.id < int(cursor_id)))
                )
            except (ValueError, IndexError):
                raise HTTPException(status_code=400, detail="Invalid cursor format")
        
        # Order by posted_at descending, then by id for consistent pagination
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
        
        return VideoListResponse(
            videos=video_responses,
            cursor=next_cursor,
            has_more=has_more
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise HTTPException(status_code=500, detail="Failed to list videos")

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Get specific video details"""
    try:
        user = get_or_create_user(db, firebase_user)
        
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Check access permissions
        if not video.is_public and video.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Increment view count if it's not the owner viewing
        if video.user_id != user.id:
            video.view_count += 1
            db.commit()
        
        return format_video_response(video)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video: {e}")
        raise HTTPException(status_code=500, detail="Failed to get video")

@router.get("/{video_id}/analytics", response_model=AnalyticsResponse)
async def get_video_analytics(
    video_id: int,
    firebase_user: Dict[str, Any] = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Get video analytics including transcript and funniness scores"""
    try:
        user = get_or_create_user(db, firebase_user)
        
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Only owner can access analytics
        if video.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        analytics = db.query(AnalyticsData).filter(AnalyticsData.video_id == video_id).first()
        
        if not analytics:
            return AnalyticsResponse(processing_status=video.processing_status)
        
        return AnalyticsResponse(
            transcript=analytics.transcript,
            overall_funniness_score=analytics.overall_funniness_score,
            laughter_timestamps=analytics.laughter_timestamps,
            processing_status=video.processing_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get video analytics") 