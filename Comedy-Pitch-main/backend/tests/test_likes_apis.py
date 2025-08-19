import pytest
from unittest.mock import patch

class TestLikeVideo:
    """Test video liking functionality"""
    
    def test_like_video_success(self, client, mock_firebase_token, auth_headers, test_video, db_session):
        """Test successfully liking a video"""
        # Get initial like count
        initial_like_count = test_video.like_count
        
        response = client.post(
            f"/api/videos/{test_video.id}/likes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Video liked successfully"
        assert data["liked"] is True
        assert data["like_count"] == initial_like_count + 1
        
        # Verify like was created in database
        from models.models import Like
        like = db_session.query(Like).filter(
            Like.video_id == test_video.id,
            Like.firebase_uid == "test-uid-123"
        ).first()
        assert like is not None
        
    def test_like_video_already_liked(self, client, mock_firebase_token, auth_headers, test_video, test_user, db_session):
        """Test liking a video that's already liked"""
        from models.models import Like
        
        # Create existing like
        existing_like = Like(
            user_id=test_user.id,
            video_id=test_video.id,
            firebase_uid=test_user.firebase_uid
        )
        db_session.add(existing_like)
        test_video.like_count = 1
        db_session.commit()
        
        response = client.post(
            f"/api/videos/{test_video.id}/likes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Video already liked"
        assert data["liked"] is True
        assert data["like_count"] == 1  # Should remain the same
        
    def test_like_nonexistent_video(self, client, mock_firebase_token, auth_headers):
        """Test liking a video that doesn't exist"""
        response = client.post("/api/videos/99999/likes", headers=auth_headers)
        assert response.status_code == 404
        assert "Video not found" in response.json()["detail"]
        
    def test_like_private_video_access_denied(self, client, mock_firebase_token, auth_headers, db_session):
        """Test liking a private video of another user"""
        from models.models import Video, User
        
        # Create another user with a private video
        other_user = User(
            firebase_uid="private-video-owner",
            email="private@example.com",
            display_name="Private Owner"
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
        
        response = client.post(f"/api/videos/{private_video.id}/likes", headers=auth_headers)
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]
        
    def test_like_video_without_auth(self, client, test_video):
        """Test liking a video without authentication"""
        response = client.post(f"/api/videos/{test_video.id}/likes")
        assert response.status_code == 401

class TestUnlikeVideo:
    """Test video unliking functionality"""
    
    def test_unlike_video_success(self, client, mock_firebase_token, auth_headers, test_video, test_user, db_session):
        """Test successfully unliking a video"""
        from models.models import Like
        
        # Create existing like
        existing_like = Like(
            user_id=test_user.id,
            video_id=test_video.id,
            firebase_uid=test_user.firebase_uid
        )
        db_session.add(existing_like)
        test_video.like_count = 1
        db_session.commit()
        
        response = client.delete(
            f"/api/videos/{test_video.id}/likes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Like removed successfully"
        assert data["liked"] is False
        assert data["like_count"] == 0
        
        # Verify like was removed from database
        remaining_like = db_session.query(Like).filter(
            Like.video_id == test_video.id,
            Like.firebase_uid == "test-uid-123"
        ).first()
        assert remaining_like is None
        
    def test_unlike_video_not_liked(self, client, mock_firebase_token, auth_headers, test_video):
        """Test unliking a video that wasn't liked"""
        response = client.delete(
            f"/api/videos/{test_video.id}/likes",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Video not liked by user"
        assert data["liked"] is False
        assert data["like_count"] == 0  # Should remain the same
        
    def test_unlike_nonexistent_video(self, client, mock_firebase_token, auth_headers):
        """Test unliking a video that doesn't exist"""
        response = client.delete("/api/videos/99999/likes", headers=auth_headers)
        assert response.status_code == 404
        assert "Video not found" in response.json()["detail"]
        
    def test_unlike_video_without_auth(self, client, test_video):
        """Test unliking a video without authentication"""
        response = client.delete(f"/api/videos/{test_video.id}/likes")
        assert response.status_code == 401



class TestLikeWorkflow:
    """Test complete like/unlike workflow"""
    
    def test_like_unlike_workflow(self, client, mock_firebase_token, auth_headers, test_video, db_session):
        """Test complete like -> unlike workflow using POST/DELETE for status checking"""
        
        # Step 1: Check initial status by trying to unlike (should not be liked)
        response = client.delete(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["liked"] is False
        assert response.json()["like_count"] == 0
        
        # Step 2: Like the video
        response = client.post(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["liked"] is True
        assert response.json()["like_count"] == 1
        
        # Step 3: Check status by trying to like again (should be idempotent)
        response = client.post(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["liked"] is True
        assert response.json()["like_count"] == 1  # Should not increase
        
        # Step 4: Unlike the video
        response = client.delete(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["liked"] is False
        assert response.json()["like_count"] == 0
        
        # Step 5: Check final status by trying to unlike again (should be idempotent)
        response = client.delete(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["liked"] is False
        assert response.json()["like_count"] == 0

class TestMultiUserLikes:
    """Test like functionality with multiple users"""
    
    def test_multiple_users_like_same_video(self, client, mock_firebase_token, auth_headers, test_video, db_session):
        """Test multiple users liking the same video"""
        from models.models import User, Like
        
        # Create second user
        user2 = User(
            firebase_uid="second-user-uid",
            email="second@example.com",
            display_name="Second User"
        )
        db_session.add(user2)
        db_session.commit()
        
        # First user likes video
        response = client.post(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["like_count"] == 1
        
        # Simulate second user liking (mock different Firebase user)
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.return_value = {
                "uid": "second-user-uid",
                "email": "second@example.com",
                "name": "Second User"
            }
            
            response = client.post(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["like_count"] == 2
        
        # Verify both likes exist in database
        likes = db_session.query(Like).filter(Like.video_id == test_video.id).all()
        assert len(likes) == 2
        
        like_uids = [like.firebase_uid for like in likes]
        assert "test-uid-123" in like_uids
        assert "second-user-uid" in like_uids
        
    def test_like_count_consistency(self, client, mock_firebase_token, auth_headers, test_video, test_user, db_session):
        """Test that like count remains consistent"""
        from models.models import Like
        
        # Create like directly in database
        like = Like(
            user_id=test_user.id,
            video_id=test_video.id,
            firebase_uid=test_user.firebase_uid
        )
        db_session.add(like)
        test_video.like_count = 1
        db_session.commit()
        
        # Unlike through API
        response = client.delete(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["like_count"] == 0
        
        # Verify like count in database
        db_session.refresh(test_video)
        assert test_video.like_count == 0
        
        # Like again through API
        response = client.post(f"/api/videos/{test_video.id}/likes", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["like_count"] == 1
        
        # Verify like count in database
        db_session.refresh(test_video)
        assert test_video.like_count == 1 