from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    firebase_uid = Column(String(128), nullable=False, index=True)  # For quick Firebase user lookup
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="likes")
    video = relationship("Video", back_populates="likes")
    
    def __repr__(self):
        return f"<Like(user_id={self.user_id}, video_id={self.video_id})>" 