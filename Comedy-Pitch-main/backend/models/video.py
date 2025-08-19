from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    firebase_uid = Column(String(128), nullable=False, index=True)  # For quick Firebase user lookup
    
    # Video metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)  # Duration in seconds
    file_type = Column(String(50), nullable=False)  # 'video' or 'audio'
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Storage information
    storage_key = Column(String(500), nullable=False)  # S3/MinIO key
    storage_url = Column(String(1000), nullable=True)  # Public URL if available
    thumbnail_url = Column(String(1000), nullable=True)
    
    # Visibility and status
    is_public = Column(Boolean, default=True)
    is_processed = Column(Boolean, default=False)  # ML processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Performance metadata
    venue_name = Column(String(255), nullable=True)
    performance_date = Column(DateTime(timezone=True), nullable=True)
    set_duration = Column(Float, nullable=True)  # Total set duration
    audience_size = Column(Integer, nullable=True)
    
    # Engagement metrics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    posted_at = Column(DateTime(timezone=True), server_default=func.now())  # For feed ordering
    
    # Relationships
    user = relationship("User", back_populates="videos")
    likes = relationship("Like", back_populates="video", cascade="all, delete-orphan")
    analytics = relationship("AnalyticsData", back_populates="video", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', user_id={self.user_id})>" 