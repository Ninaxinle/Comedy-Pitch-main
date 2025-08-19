import pytest
from datetime import datetime
from models.models import User, Video, Like, AnalyticsData
import json

class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            firebase_uid="test-uid-456",
            email="newuser@example.com",
            display_name="New User",
            bio="Comedy enthusiast",
            is_comedian=False,
            location="New York"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.firebase_uid == "test-uid-456"
        assert user.email == "newuser@example.com"
        assert user.display_name == "New User"
        assert user.is_comedian is False
        assert user.is_active is True  # Default value
        assert user.created_at is not None
        
    def test_user_relationships(self, db_session, test_user):
        """Test user relationships with videos and likes"""
        # Create a video for the user
        video = Video(
            user_id=test_user.id,
            firebase_uid=test_user.firebase_uid,
            title="Test Video",
            file_type="video",
            storage_key="test/video.mp4"
        )
        db_session.add(video)
        db_session.commit()
        
        # Verify relationship
        db_session.refresh(test_user)
        assert len(test_user.videos) == 1
        assert test_user.videos[0].title == "Test Video"
        
    def test_user_repr(self, test_user):
        """Test user string representation"""
        repr_str = repr(test_user)
        assert "test-uid-123" in repr_str
        assert "test@example.com" in repr_str

class TestVideoModel:
    """Test Video model functionality"""
    
    def test_create_video(self, db_session, test_user):
        """Test creating a video"""
        video = Video(
            user_id=test_user.id,
            firebase_uid=test_user.firebase_uid,
            title="My Comedy Special",
            description="Hilarious stand-up routine",
            duration=3600.0,
            file_type="video",
            storage_key="videos/1/special.mp4",
            venue_name="Comedy Club",
            audience_size=200,
            is_public=True
        )
        
        db_session.add(video)
        db_session.commit()
        db_session.refresh(video)
        
        assert video.id is not None
        assert video.title == "My Comedy Special"
        assert video.duration == 3600.0
        assert video.file_type == "video"
        assert video.is_public is True
        assert video.view_count == 0  # Default value
        assert video.like_count == 0  # Default value
        assert video.processing_status == "pending"  # Default value
        assert video.created_at is not None
        assert video.posted_at is not None
        
    def test_video_user_relationship(self, db_session, test_user):
        """Test video-user relationship"""
        video = Video(
            user_id=test_user.id,
            firebase_uid=test_user.firebase_uid,
            title="Test Video",
            file_type="video",
            storage_key="test.mp4"
        )
        db_session.add(video)
        db_session.commit()
        db_session.refresh(video)
        
        assert video.user.id == test_user.id
        assert video.user.email == test_user.email
        
    def test_video_repr(self, test_video):
        """Test video string representation"""
        repr_str = repr(test_video)
        assert str(test_video.id) in repr_str
        assert "Test Comedy Video" in repr_str

class TestLikeModel:
    """Test Like model functionality"""
    
    def test_create_like(self, db_session, test_user, test_video):
        """Test creating a like"""
        like = Like(
            user_id=test_user.id,
            video_id=test_video.id,
            firebase_uid=test_user.firebase_uid
        )
        
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        assert like.id is not None
        assert like.user_id == test_user.id
        assert like.video_id == test_video.id
        assert like.firebase_uid == test_user.firebase_uid
        assert like.created_at is not None
        
    def test_like_relationships(self, db_session, test_user, test_video):
        """Test like relationships with user and video"""
        like = Like(
            user_id=test_user.id,
            video_id=test_video.id,
            firebase_uid=test_user.firebase_uid
        )
        db_session.add(like)
        db_session.commit()
        db_session.refresh(like)
        
        assert like.user.id == test_user.id
        assert like.video.id == test_video.id
        
    def test_like_repr(self, db_session, test_user, test_video):
        """Test like string representation"""
        like = Like(
            user_id=test_user.id,
            video_id=test_video.id,
            firebase_uid=test_user.firebase_uid
        )
        db_session.add(like)
        db_session.commit()
        
        repr_str = repr(like)
        assert str(test_user.id) in repr_str
        assert str(test_video.id) in repr_str

class TestAnalyticsDataModel:
    """Test AnalyticsData model functionality"""
    
    def test_create_analytics(self, db_session, test_video):
        """Test creating analytics data"""
        transcript_data = [
            {
                "text": "So I went to the store...",
                "start_time": 0.0,
                "end_time": 3.5,
                "funniness_score": 0.2
            },
            {
                "text": "And the cashier said...",
                "start_time": 3.5,
                "end_time": 7.0,
                "funniness_score": 0.8
            }
        ]
        
        laughter_data = [
            {
                "timestamp": 6.5,
                "duration": 2.0,
                "intensity": 0.9
            }
        ]
        
        analytics = AnalyticsData(
            video_id=test_video.id,
            transcript=transcript_data,
            full_transcript_text="So I went to the store... And the cashier said...",
            overall_funniness_score=0.75,
            laughter_timestamps=laughter_data,
            processing_version="v1.0.0",
            confidence_score=0.95,
            word_count=10,
            speaking_rate=120.0
        )
        
        db_session.add(analytics)
        db_session.commit()
        db_session.refresh(analytics)
        
        assert analytics.id is not None
        assert analytics.video_id == test_video.id
        assert analytics.overall_funniness_score == 0.75
        assert analytics.processing_version == "v1.0.0"
        assert analytics.confidence_score == 0.95
        assert analytics.word_count == 10
        assert analytics.speaking_rate == 120.0
        assert analytics.created_at is not None
        
        # Test JSON fields
        assert len(analytics.transcript) == 2
        assert analytics.transcript[0]["text"] == "So I went to the store..."
        assert analytics.transcript[0]["funniness_score"] == 0.2
        assert len(analytics.laughter_timestamps) == 1
        assert analytics.laughter_timestamps[0]["intensity"] == 0.9
        
    def test_analytics_video_relationship(self, db_session, test_video):
        """Test analytics-video relationship"""
        analytics = AnalyticsData(
            video_id=test_video.id,
            overall_funniness_score=0.6
        )
        db_session.add(analytics)
        db_session.commit()
        db_session.refresh(analytics)
        
        assert analytics.video.id == test_video.id
        assert analytics.video.title == test_video.title
        
    def test_analytics_repr(self, db_session, test_video):
        """Test analytics string representation"""
        analytics = AnalyticsData(
            video_id=test_video.id,
            overall_funniness_score=0.85
        )
        db_session.add(analytics)
        db_session.commit()
        
        repr_str = repr(analytics)
        assert str(test_video.id) in repr_str
        assert "0.85" in repr_str

class TestModelIntegration:
    """Test model integration and complex relationships"""
    
    def test_complete_workflow(self, db_session):
        """Test a complete workflow: user -> video -> like -> analytics"""
        # Create user
        user = User(
            firebase_uid="workflow-user",
            email="workflow@example.com",
            display_name="Workflow User",
            is_comedian=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create video
        video = Video(
            user_id=user.id,
            firebase_uid=user.firebase_uid,
            title="Workflow Video",
            file_type="video",
            storage_key="workflow/video.mp4",
            is_public=True
        )
        db_session.add(video)
        db_session.commit()
        db_session.refresh(video)
        
        # Create like
        like = Like(
            user_id=user.id,
            video_id=video.id,
            firebase_uid=user.firebase_uid
        )
        db_session.add(like)
        video.like_count += 1
        db_session.commit()
        
        # Create analytics
        analytics = AnalyticsData(
            video_id=video.id,
            overall_funniness_score=0.9,
            processing_version="v1.0.0"
        )
        db_session.add(analytics)
        video.is_processed = True
        video.processing_status = "completed"
        db_session.commit()
        
        # Verify all relationships
        db_session.refresh(user)
        db_session.refresh(video)
        
        assert len(user.videos) == 1
        assert len(user.likes) == 1
        assert video.like_count == 1
        assert video.is_processed is True
        assert len(video.likes) == 1
        assert len(video.analytics) == 1
        assert video.analytics[0].overall_funniness_score == 0.9
        
    def test_cascade_delete(self, db_session, test_user):
        """Test cascade delete behavior"""
        # Create video with likes and analytics
        video = Video(
            user_id=test_user.id,
            firebase_uid=test_user.firebase_uid,
            title="Delete Test Video",
            file_type="video",
            storage_key="delete/test.mp4"
        )
        db_session.add(video)
        db_session.commit()
        db_session.refresh(video)
        
        like = Like(
            user_id=test_user.id,
            video_id=video.id,
            firebase_uid=test_user.firebase_uid
        )
        db_session.add(like)
        
        analytics = AnalyticsData(
            video_id=video.id,
            overall_funniness_score=0.5
        )
        db_session.add(analytics)
        db_session.commit()
        
        video_id = video.id
        
        # Delete the video
        db_session.delete(video)
        db_session.commit()
        
        # Verify cascaded deletes
        remaining_likes = db_session.query(Like).filter(Like.video_id == video_id).all()
        remaining_analytics = db_session.query(AnalyticsData).filter(AnalyticsData.video_id == video_id).all()
        
        assert len(remaining_likes) == 0
        assert len(remaining_analytics) == 0 