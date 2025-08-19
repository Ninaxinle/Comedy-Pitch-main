from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from config.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    is_comedian = Column(Boolean, default=False)
    stage_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    social_links = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(firebase_uid='{self.firebase_uid}', email='{self.email}')>" 