import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

class TestVideoPresignedUpload:
    """Test presigned upload URL generation"""
    
    def test_get_presigned_url_success(self, client, mock_firebase_token, mock_storage, auth_headers):
        """Test successful presigned URL generation"""
        request_data = {
            "filename": "my_video.mp4",
            "content_type": "video/mp4",
            "content_length": 1024000
        }
        
        response = client.post(
            "/api/videos/uploads/presign",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "upload_url" in data
        assert "storage_key" in data
        assert "expires_in" in data
        assert data["expires_in"] == 3600
        assert "my_video.mp4" in data["storage_key"]  # Should contain original filename
        
    def test_get_presigned_url_without_auth(self, client):
        """Test presigned URL generation without authentication"""
        request_data = {
            "filename": "my_video.mp4",
            "content_type": "video/mp4"
        }
        
        response = client.post("/api/videos/uploads/presign", json=request_data)
        assert response.status_code == 401
        
    def test_get_presigned_url_invalid_data(self, client, mock_firebase_token, auth_headers):
        """Test presigned URL generation with invalid data"""
        request_data = {
            "filename": "",  # Empty filename
            "content_type": "video/mp4"
        }
        
        response = client.post(
            "/api/videos/uploads/presign",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error

class TestVideoCreation:
    """Test video creation after upload"""
    
    def test_create_video_success(self, client, mock_firebase_token, mock_storage, auth_headers, test_user):
        """Test successful video creation"""
        video_data = {
            "storage_key": "videos/1/test_video.mp4",
            "title": "My Awesome Comedy Set",
            "description": "Hilarious stand-up routine from last night",
            "file_type": "video",
            "duration": 1800.5,
            "venue_name": "Comedy Store",
            "audience_size": 150,
            "is_public": True
        }
        
        response = client.post(
            "/api/videos/",
            json=video_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "My Awesome Comedy Set"
        assert data["description"] == "Hilarious stand-up routine from last night"
        assert data["file_type"] == "video"
        assert data["duration"] == 1800.5
        assert data["is_public"] is True
        assert data["view_count"] == 0
        assert data["like_count"] == 0
        assert "storage_url" in data
        assert "user" in data
        
    def test_create_video_file_not_found(self, client, mock_firebase_token, auth_headers):
        """Test video creation when file doesn't exist in storage"""
        with patch('storage.factory.get_storage') as mock_get_storage:
            mock_storage = Mock()
            mock_storage.file_exists.return_value = False
            mock_get_storage.return_value = mock_storage
            
            video_data = {
                "storage_key": "nonexistent/video.mp4",
                "title": "Missing Video",
                "file_type": "video"
            }
            
            response = client.post(
                "/api/videos/",
                json=video_data,
                headers=auth_headers
            )
            
            assert response.status_code == 400
            assert "File not found in storage" in response.json()["detail"]
            
    def test_create_video_invalid_data(self, client, mock_firebase_token, auth_headers):
        """Test video creation with invalid data"""
        video_data = {
            "storage_key": "valid/key.mp4",
            "title": "",  # Empty title should fail validation
            "file_type": "video"
        }
        
        response = client.post(
            "/api/videos/",
            json=video_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_create_video_without_auth(self, client):
        """Test video creation without authentication"""
        video_data = {
            "storage_key": "test/video.mp4",
            "title": "Unauthorized Video",
            "file_type": "video"
        }
        
        response = client.post("/api/videos/", json=video_data)
        assert response.status_code == 401

class TestVideoListing:
    """Test video listing and pagination"""
    
    def test_list_own_videos(self, client, mock_firebase_token, auth_headers, test_user, test_video):
        """Test listing user's own videos"""
        response = client.get("/api/videos/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "videos" in data
        assert "cursor" in data
        assert "has_more" in data
        assert len(data["videos"]) >= 1
        
        # Check video data structure
        video = data["videos"][0]
        assert "id" in video
        assert "title" in video
        assert "user" in video
        
    def test_list_home_feed(self, client, mock_firebase_token, auth_headers, test_user, test_video):
        """Test listing home feed (public videos)"""
        response = client.get("/api/videos/?feed=home", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "videos" in data
        assert "cursor" in data
        assert "has_more" in data
        
    def test_list_videos_with_pagination(self, client, mock_firebase_token, auth_headers, test_user):
        """Test video listing with pagination"""
        # Create multiple videos for pagination testing
        from models.models import Video
        from tests.conftest import TestingSessionLocal
        
        db = TestingSessionLocal()
        try:
            videos = []
            for i in range(5):
                video = Video(
                    user_id=test_user.id,
                    firebase_uid=test_user.firebase_uid,
                    title=f"Test Video {i}",
                    file_type="video",
                    storage_key=f"test/video_{i}.mp4",
                    is_public=True
                )
                db.add(video)
                videos.append(video)
            db.commit()
            
            # Test pagination with limit
            response = client.get("/api/videos/?limit=3", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["videos"]) <= 3
            
            # Test with cursor if there are more videos
            if data["has_more"]:
                cursor = data["cursor"]
                response2 = client.get(f"/api/videos/?cursor={cursor}", headers=auth_headers)
                assert response2.status_code == 200
                
        finally:
            db.close()
            
    def test_list_videos_invalid_cursor(self, client, mock_firebase_token, auth_headers):
        """Test video listing with invalid cursor"""
        response = client.get("/api/videos/?cursor=invalid_cursor", headers=auth_headers)
        assert response.status_code == 400
        assert "Invalid cursor format" in response.json()["detail"]
        
    def test_list_videos_without_auth(self, client):
        """Test video listing without authentication"""
        response = client.get("/api/videos/")
        assert response.status_code == 401

class TestVideoRetrieval:
    """Test individual video retrieval"""
    
    def test_get_video_success(self, client, mock_firebase_token, auth_headers, test_video):
        """Test successful video retrieval"""
        response = client.get(f"/api/videos/{test_video.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_video.id
        assert data["title"] == test_video.title
        assert "user" in data
        assert "storage_url" in data
        
    def test_get_video_increments_view_count(self, client, mock_firebase_token, auth_headers, db_session):
        """Test that viewing a video increments view count"""
        from models.models import Video, User
        
        # Create another user and their video
        other_user = User(
            firebase_uid="other-user-uid",
            email="other@example.com",
            display_name="Other User"
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        video = Video(
            user_id=other_user.id,
            firebase_uid=other_user.firebase_uid,
            title="Other User's Video",
            file_type="video",
            storage_key="other/video.mp4",
            is_public=True,
            view_count=0
        )
        db_session.add(video)
        db_session.commit()
        db_session.refresh(video)
        
        # View the video
        response = client.get(f"/api/videos/{video.id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Check that view count increased
        db_session.refresh(video)
        assert video.view_count == 1
        
    def test_get_video_not_found(self, client, mock_firebase_token, auth_headers):
        """Test retrieving non-existent video"""
        response = client.get("/api/videos/99999", headers=auth_headers)
        assert response.status_code == 404
        
    def test_get_private_video_access_denied(self, client, mock_firebase_token, auth_headers, db_session):
        """Test accessing private video of another user"""
        from models.models import Video, User
        
        # Create another user with a private video
        other_user = User(
            firebase_uid="private-user-uid",
            email="private@example.com",
            display_name="Private User"
        )
        db_session.add(other_user)
        db_session.commit()
        
        private_video = Video(
            user_id=other_user.id,
            firebase_uid=other_user.firebase_uid,
            title="Private Video",
            file_type="video",
            storage_key="private/video.mp4",
            is_public=False
        )
        db_session.add(private_video)
        db_session.commit()
        
        response = client.get(f"/api/videos/{private_video.id}", headers=auth_headers)
        assert response.status_code == 403
        
    def test_get_video_without_auth(self, client, test_video):
        """Test video retrieval without authentication"""
        response = client.get(f"/api/videos/{test_video.id}")
        assert response.status_code == 401

class TestVideoAnalytics:
    """Test video analytics endpoints"""
    
    def test_get_video_analytics_success(self, client, mock_firebase_token, auth_headers, test_video, db_session):
        """Test successful analytics retrieval"""
        from models.models import AnalyticsData
        
        # Create analytics data
        analytics = AnalyticsData(
            video_id=test_video.id,
            transcript=[
                {
                    "text": "Welcome to my comedy show",
                    "start_time": 0.0,
                    "end_time": 3.0,
                    "funniness_score": 0.3
                },
                {
                    "text": "Here's a funny joke...",
                    "start_time": 3.0,
                    "end_time": 8.0,
                    "funniness_score": 0.9
                }
            ],
            overall_funniness_score=0.75,
            laughter_timestamps=[
                {
                    "timestamp": 7.5,
                    "duration": 2.0,
                    "intensity": 0.8
                }
            ]
        )
        db_session.add(analytics)
        test_video.processing_status = "completed"
        db_session.commit()
        
        response = client.get(f"/api/videos/{test_video.id}/analytics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["overall_funniness_score"] == 0.75
        assert data["processing_status"] == "completed"
        assert len(data["transcript"]) == 2
        assert data["transcript"][0]["text"] == "Welcome to my comedy show"
        assert data["transcript"][1]["funniness_score"] == 0.9
        assert len(data["laughter_timestamps"]) == 1
        assert data["laughter_timestamps"][0]["intensity"] == 0.8
        
    def test_get_video_analytics_no_analytics(self, client, mock_firebase_token, auth_headers, test_video):
        """Test analytics retrieval when no analytics exist"""
        response = client.get(f"/api/videos/{test_video.id}/analytics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["transcript"] is None
        assert data["overall_funniness_score"] is None
        assert data["laughter_timestamps"] is None
        assert data["processing_status"] == "pending"  # Default status
        
    def test_get_video_analytics_not_owner(self, client, mock_firebase_token, auth_headers, db_session):
        """Test analytics access denied for non-owner"""
        from models.models import Video, User
        
        # Create another user's video
        other_user = User(
            firebase_uid="analytics-other-uid",
            email="analytics@example.com",
            display_name="Other Analytics User"
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_video = Video(
            user_id=other_user.id,
            firebase_uid=other_user.firebase_uid,
            title="Other User's Video",
            file_type="video",
            storage_key="other/analytics.mp4"
        )
        db_session.add(other_video)
        db_session.commit()
        
        response = client.get(f"/api/videos/{other_video.id}/analytics", headers=auth_headers)
        assert response.status_code == 403
        
    def test_get_video_analytics_not_found(self, client, mock_firebase_token, auth_headers):
        """Test analytics retrieval for non-existent video"""
        response = client.get("/api/videos/99999/analytics", headers=auth_headers)
        assert response.status_code == 404
        
    def test_get_video_analytics_without_auth(self, client, test_video):
        """Test analytics retrieval without authentication"""
        response = client.get(f"/api/videos/{test_video.id}/analytics")
        assert response.status_code == 401

class TestVideoIntegration:
    """Test complete video workflow integration"""
    
    def test_complete_video_workflow(self, client, mock_firebase_token, mock_storage, auth_headers):
        """Test complete workflow: presigned URL -> upload -> create -> view -> analytics"""
        
        # Step 1: Get presigned upload URL
        presign_data = {
            "filename": "workflow_test.mp4",
            "content_type": "video/mp4",
            "content_length": 2048000
        }
        
        response = client.post(
            "/api/videos/uploads/presign",
            json=presign_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        presign_result = response.json()
        storage_key = presign_result["storage_key"]
        
        # Step 2: Create video metadata (simulating successful upload)
        video_data = {
            "storage_key": storage_key,
            "title": "Workflow Test Video",
            "description": "Testing the complete workflow",
            "file_type": "video",
            "duration": 300.0,
            "is_public": True
        }
        
        response = client.post(
            "/api/videos/",
            json=video_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        video_result = response.json()
        video_id = video_result["id"]
        
        # Step 3: Retrieve the video
        response = client.get(f"/api/videos/{video_id}", headers=auth_headers)
        assert response.status_code == 200
        retrieved_video = response.json()
        assert retrieved_video["title"] == "Workflow Test Video"
        
        # Step 4: Get analytics (should show no analytics yet)
        response = client.get(f"/api/videos/{video_id}/analytics", headers=auth_headers)
        assert response.status_code == 200
        analytics_result = response.json()
        assert analytics_result["processing_status"] == "pending"
        
        # Step 5: Check video appears in listing
        response = client.get("/api/videos/", headers=auth_headers)
        assert response.status_code == 200
        listing_result = response.json()
        
        video_titles = [v["title"] for v in listing_result["videos"]]
        assert "Workflow Test Video" in video_titles 