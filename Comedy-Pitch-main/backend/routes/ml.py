from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from config.database import get_db
from models.models import Video, AnalyticsData

# Configure logging
logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for ML processing results
class TranscriptSegment(BaseModel):
    text: str = Field(..., description="Transcript text for this segment")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds") 
    funniness_score: Optional[float] = Field(None, description="Funniness score for this segment (0.0-1.0)")

class LaughterEvent(BaseModel):
    timestamp: float = Field(..., description="Timestamp of laughter in seconds")
    duration: float = Field(..., description="Duration of laughter in seconds")
    intensity: Optional[float] = Field(None, description="Intensity of laughter (0.0-1.0)")

class MLScoreRequest(BaseModel):
    video_id: int = Field(..., description="Video ID being processed")
    processing_version: str = Field(..., description="ML model version used")
    transcript: List[TranscriptSegment] = Field(..., description="Full transcript with timestamps")
    overall_funniness_score: float = Field(..., ge=0.0, le=1.0, description="Overall funniness score")
    laughter_timestamps: Optional[List[LaughterEvent]] = Field(None, description="Detected laughter events")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in analysis")
    processing_duration: Optional[float] = Field(None, description="Processing time in seconds")
    word_count: Optional[int] = Field(None, description="Total word count")
    speaking_rate: Optional[float] = Field(None, description="Words per minute")

class MLScoreResponse(BaseModel):
    message: str
    video_id: int
    analytics_id: int

class VideoProcessingStatusUpdate(BaseModel):
    video_id: int
    status: str = Field(..., description="Processing status: pending, processing, completed, failed")
    error_message: Optional[str] = None

# Routes
@router.post("/score-results", response_model=MLScoreResponse)
async def submit_ml_results(
    ml_data: MLScoreRequest,
    db: Session = Depends(get_db)
):
    """Accept ML processing results and store in database"""
    try:
        # Verify video exists
        video = db.query(Video).filter(Video.id == ml_data.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Convert transcript segments to JSON format
        transcript_json = [
            {
                "text": segment.text,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "funniness_score": segment.funniness_score
            }
            for segment in ml_data.transcript
        ]
        
        # Convert laughter events to JSON format
        laughter_json = None
        if ml_data.laughter_timestamps:
            laughter_json = [
                {
                    "timestamp": event.timestamp,
                    "duration": event.duration,
                    "intensity": event.intensity
                }
                for event in ml_data.laughter_timestamps
            ]
        
        # Create full transcript text
        full_transcript = " ".join([segment.text for segment in ml_data.transcript])
        
        # Check if analytics record already exists
        existing_analytics = db.query(AnalyticsData).filter(
            AnalyticsData.video_id == ml_data.video_id
        ).first()
        
        if existing_analytics:
            # Update existing record
            existing_analytics.transcript = transcript_json
            existing_analytics.full_transcript_text = full_transcript
            existing_analytics.overall_funniness_score = ml_data.overall_funniness_score
            existing_analytics.laughter_timestamps = laughter_json
            existing_analytics.processing_version = ml_data.processing_version
            existing_analytics.confidence_score = ml_data.confidence_score
            existing_analytics.processing_duration = ml_data.processing_duration
            existing_analytics.word_count = ml_data.word_count
            existing_analytics.speaking_rate = ml_data.speaking_rate
            analytics = existing_analytics
        else:
            # Create new analytics record
            analytics = AnalyticsData(
                video_id=ml_data.video_id,
                transcript=transcript_json,
                full_transcript_text=full_transcript,
                overall_funniness_score=ml_data.overall_funniness_score,
                laughter_timestamps=laughter_json,
                processing_version=ml_data.processing_version,
                confidence_score=ml_data.confidence_score,
                processing_duration=ml_data.processing_duration,
                word_count=ml_data.word_count,
                speaking_rate=ml_data.speaking_rate
            )
            db.add(analytics)
        
        # Update video processing status
        video.is_processed = True
        video.processing_status = "completed"
        
        db.commit()
        db.refresh(analytics)
        
        return MLScoreResponse(
            message="ML results processed successfully",
            video_id=ml_data.video_id,
            analytics_id=analytics.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing ML results: {e}")
        raise HTTPException(status_code=500, detail="Failed to process ML results")

@router.post("/processing-status")
async def update_processing_status(
    status_update: VideoProcessingStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update video processing status"""
    try:
        video = db.query(Video).filter(Video.id == status_update.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        video.processing_status = status_update.status
        
        if status_update.status == "processing":
            video.is_processed = False
        elif status_update.status == "completed":
            video.is_processed = True
        elif status_update.status == "failed":
            video.is_processed = False
            # Could store error message in a separate field if needed
        
        db.commit()
        
        return {
            "message": "Processing status updated successfully",
            "video_id": status_update.video_id,
            "status": status_update.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update processing status")

@router.get("/video/{video_id}/status")
async def get_processing_status(
    video_id: int,
    db: Session = Depends(get_db)
):
    """Get current processing status of a video"""
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        analytics = db.query(AnalyticsData).filter(AnalyticsData.video_id == video_id).first()
        
        return {
            "video_id": video_id,
            "processing_status": video.processing_status,
            "is_processed": video.is_processed,
            "has_analytics": analytics is not None,
            "processing_version": analytics.processing_version if analytics else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing status")

# Health check endpoint
@router.get("/health")
async def ml_health():
    """Health check for ML routes"""
    return {
        "status": "healthy",
        "service": "ml_processing",
        "routes": [
            "/score-results",
            "/processing-status", 
            "/video/{video_id}/status",
            "/health"
        ]
    } 