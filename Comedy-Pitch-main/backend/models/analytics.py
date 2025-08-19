from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class AnalyticsData(Base):
    __tablename__ = "analytics_data"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    
    # Transcript data
    transcript = Column(JSON, nullable=True)  # Array of transcript segments
    full_transcript_text = Column(Text, nullable=True)  # Complete transcript as text
    
    # ML Analytics
    overall_funniness_score = Column(Float, nullable=True)  # 0.0 - 1.0
    laughter_timestamps = Column(JSON, nullable=True)  # Array of laughter detection data
    sentiment_analysis = Column(JSON, nullable=True)  # Sentiment scores per segment
    
    # Processing metadata
    processing_version = Column(String(50), nullable=True)  # ML model version
    confidence_score = Column(Float, nullable=True)  # Overall confidence in analysis
    processing_duration = Column(Float, nullable=True)  # Time taken to process in seconds
    
    # Additional analytics
    word_count = Column(Integer, nullable=True)
    speaking_rate = Column(Float, nullable=True)  # Words per minute
    pause_analysis = Column(JSON, nullable=True)  # Pause timing data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="analytics")
    
    def __repr__(self):
        return f"<AnalyticsData(video_id={self.video_id}, funniness_score={self.overall_funniness_score})>" 