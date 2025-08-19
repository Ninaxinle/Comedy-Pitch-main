import pytest
import json
from unittest.mock import patch

class TestGetUserProfile:
    """Test user profile retrieval"""
    
    def test_get_my_profile_success(self, client, mock_firebase_token, auth_headers, test_user):
        """Test successful retrieval of own profile"""
        response = client.get("/api/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["firebase_uid"] == test_user.firebase_uid
        assert data["email"] == test_user.email
        assert data["display_name"] == test_user.display_name
        assert data["is_comedian"] == test_user.is_comedian
        assert data["is_active"] == test_user.is_active
        assert "video_count" in data
        assert "total_likes" in data
        assert "created_at" in data
        
    def test_get_my_profile_without_auth(self, client):
        """Test profile retrieval without authentication"""
        response = client.get("/api/users/me")
        assert response.status_code == 401
        
    def test_get_my_profile_creates_user_if_not_exists(self, client, auth_headers):
        """Test that getting profile creates user if they don't exist in database"""
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.return_value = {
                "uid": "new-user-uid",
                "email": "newuser@example.com",
                "name": "New User"
            }
            
            response = client.get("/api/users/me", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["firebase_uid"] == "new-user-uid"
            assert data["email"] == "newuser@example.com"

class TestUpdateUserProfile:
    """Test user profile updates"""
    
    def test_update_profile_success(self, client, mock_firebase_token, auth_headers, test_user, db_session):
        """Test successful profile update"""
        update_data = {
            "display_name": "Updated Display Name",
            "bio": "Updated bio with comedy background",
            "is_comedian": True,
            "stage_name": "Comedy King",
            "location": "Los Angeles, CA",
            "website": "https://comedyking.com",
            "social_links": {
                "twitter": "@comedyking",
                "instagram": "comedyking_official"
            }
        }
        
        response = client.put(
            "/api/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["display_name"] == "Updated Display Name"
        assert data["bio"] == "Updated bio with comedy background"
        assert data["is_comedian"] is True
        assert data["stage_name"] == "Comedy King"
        assert data["location"] == "Los Angeles, CA"
        assert data["website"] == "https://comedyking.com"
        assert data["social_links"]["twitter"] == "@comedyking"
        assert data["social_links"]["instagram"] == "comedyking_official"
        
        # Verify changes in database
        db_session.refresh(test_user)
        assert test_user.display_name == "Updated Display Name"
        assert test_user.bio == "Updated bio with comedy background"
        assert test_user.is_comedian is True
        
    def test_update_profile_partial(self, client, mock_firebase_token, auth_headers, test_user):
        """Test partial profile update"""
        update_data = {
            "display_name": "Partially Updated Name"
        }
        
        response = client.put(
            "/api/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["display_name"] == "Partially Updated Name"
        # Other fields should remain unchanged
        assert data["email"] == test_user.email
        assert data["is_comedian"] == test_user.is_comedian
        
    def test_update_profile_invalid_data(self, client, mock_firebase_token, auth_headers):
        """Test profile update with invalid data"""
        update_data = {
            "display_name": "x" * 300,  # Too long
            "website": "not-a-valid-url"
        }
        
        response = client.put(
            "/api/users/me",
            json=update_data,
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code == 422
        
    def test_update_profile_without_auth(self, client):
        """Test profile update without authentication"""
        update_data = {"display_name": "Unauthorized Update"}
        
        response = client.put("/api/users/me", json=update_data)
        assert response.status_code == 401

class TestUpdateUserSettings:
    """Test user settings updates"""
    
    def test_update_settings_success(self, client, mock_firebase_token, auth_headers):
        """Test successful settings update"""
        settings_data = {
            "is_public_profile": True,
            "email_notifications": False,
            "push_notifications": True
        }
        
        response = client.put(
            "/api/users/me/settings",
            json=settings_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Settings updated successfully"
        
    def test_update_settings_without_auth(self, client):
        """Test settings update without authentication"""
        settings_data = {"email_notifications": False}
        
        response = client.put("/api/users/me/settings", json=settings_data)
        assert response.status_code == 401

class TestGetPublicProfile:
    """Test public profile retrieval"""
    
    def test_get_public_profile_success(self, client, mock_firebase_token, auth_headers, db_session):
        """Test successful public profile retrieval"""
        from models.models import User
        
        # Create another user for public profile viewing
        other_user = User(
            firebase_uid="public-profile-uid",
            email="public@example.com",
            display_name="Public User",
            bio="Public comedy bio",
            is_comedian=True,
            stage_name="Public Comedian",
            location="New York",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)
        
        response = client.get(f"/api/users/{other_user.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == other_user.id
        assert data["display_name"] == "Public User"
        assert data["bio"] == "Public comedy bio"
        assert data["is_comedian"] is True
        assert data["stage_name"] == "Public Comedian"
        assert data["location"] == "New York"
        assert "video_count" in data
        assert "total_likes" in data
        
        # Should not include private information
        assert "firebase_uid" not in data
        assert "email" not in data
        assert "is_active" not in data
        
    def test_get_public_profile_not_found(self, client, mock_firebase_token, auth_headers):
        """Test getting public profile for non-existent user"""
        response = client.get("/api/users/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
        
    def test_get_public_profile_inactive_user(self, client, mock_firebase_token, auth_headers, db_session):
        """Test getting public profile for inactive user"""
        from models.models import User
        
        # Create inactive user
        inactive_user = User(
            firebase_uid="inactive-user-uid",
            email="inactive@example.com",
            display_name="Inactive User",
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        response = client.get(f"/api/users/{inactive_user.id}", headers=auth_headers)
        assert response.status_code == 404
        
    def test_get_public_profile_without_auth(self, client, test_user):
        """Test getting public profile without authentication"""
        response = client.get(f"/api/users/{test_user.id}")
        assert response.status_code == 401

class TestGetUserVideos:
    """Test user videos retrieval"""
    
    def test_get_user_videos_success(self, client, mock_firebase_token, auth_headers, db_session):
        """Test successful user videos retrieval"""
        from models.models import User, Video
        
        # Create user with videos
        video_owner = User(
            firebase_uid="video-owner-uid",
            email="videoowner@example.com",
            display_name="Video Owner",
            is_comedian=True
        )
        db_session.add(video_owner)
        db_session.commit()
        db_session.refresh(video_owner)
        
        # Create public videos
        for i in range(3):
            video = Video(
                user_id=video_owner.id,
                firebase_uid=video_owner.firebase_uid,
                title=f"Public Video {i}",
                file_type="video",
                storage_key=f"public/video_{i}.mp4",
                is_public=True
            )
            db_session.add(video)
        
        # Create private video (should not appear)
        private_video = Video(
            user_id=video_owner.id,
            firebase_uid=video_owner.firebase_uid,
            title="Private Video",
            file_type="video",
            storage_key="private/video.mp4",
            is_public=False
        )
        db_session.add(private_video)
        db_session.commit()
        
        response = client.get(f"/api/users/{video_owner.id}/videos", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "videos" in data
        assert "cursor" in data
        assert "has_more" in data
        assert "user" in data
        
        # Should only show public videos
        assert len(data["videos"]) == 3
        video_titles = [v["title"] for v in data["videos"]]
        assert "Private Video" not in video_titles
        
        # Check user info
        assert data["user"]["id"] == video_owner.id
        assert data["user"]["display_name"] == "Video Owner"
        
    def test_get_user_videos_with_pagination(self, client, mock_firebase_token, auth_headers, db_session):
        """Test user videos with pagination"""
        from models.models import User, Video
        
        # Create user with many videos
        video_owner = User(
            firebase_uid="paginated-owner-uid",
            email="paginated@example.com",
            display_name="Paginated Owner"
        )
        db_session.add(video_owner)
        db_session.commit()
        db_session.refresh(video_owner)
        
        # Create multiple videos
        for i in range(25):
            video = Video(
                user_id=video_owner.id,
                firebase_uid=video_owner.firebase_uid,
                title=f"Video {i}",
                file_type="video",
                storage_key=f"paginated/video_{i}.mp4",
                is_public=True
            )
            db_session.add(video)
        db_session.commit()
        
        # Test pagination
        response = client.get(
            f"/api/users/{video_owner.id}/videos?limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["videos"]) == 10
        assert data["has_more"] is True
        assert data["cursor"] is not None
        
        # Test second page
        cursor = data["cursor"]
        response2 = client.get(
            f"/api/users/{video_owner.id}/videos?cursor={cursor}&limit=10",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["videos"]) == 10
        
    def test_get_user_videos_not_found(self, client, mock_firebase_token, auth_headers):
        """Test getting videos for non-existent user"""
        response = client.get("/api/users/99999/videos", headers=auth_headers)
        assert response.status_code == 404
        
    def test_get_user_videos_invalid_cursor(self, client, mock_firebase_token, auth_headers, test_user):
        """Test getting user videos with invalid cursor"""
        response = client.get(
            f"/api/users/{test_user.id}/videos?cursor=invalid_cursor",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "Invalid cursor format" in response.json()["detail"]
        
    def test_get_user_videos_without_auth(self, client, test_user):
        """Test getting user videos without authentication"""
        response = client.get(f"/api/users/{test_user.id}/videos")
        assert response.status_code == 401

class TestUserProfileIntegration:
    """Test complete user profile workflow"""
    
    def test_complete_profile_workflow(self, client, mock_firebase_token, auth_headers, db_session):
        """Test complete profile workflow: get -> update -> view public"""
        
        # Step 1: Get initial profile
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        initial_profile = response.json()
        user_id = initial_profile["id"]
        
        # Step 2: Update profile
        update_data = {
            "display_name": "Workflow Comedian",
            "bio": "Testing the complete workflow",
            "is_comedian": True,
            "stage_name": "Workflow King",
            "social_links": {
                "youtube": "workflow_comedian"
            }
        }
        
        response = client.put("/api/users/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        updated_profile = response.json()
        
        assert updated_profile["display_name"] == "Workflow Comedian"
        assert updated_profile["bio"] == "Testing the complete workflow"
        assert updated_profile["is_comedian"] is True
        assert updated_profile["social_links"]["youtube"] == "workflow_comedian"
        
        # Step 3: View public profile
        response = client.get(f"/api/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        public_profile = response.json()
        
        assert public_profile["display_name"] == "Workflow Comedian"
        assert public_profile["bio"] == "Testing the complete workflow"
        assert public_profile["is_comedian"] is True
        
        # Should not contain private info
        assert "firebase_uid" not in public_profile
        assert "email" not in public_profile
        
        # Step 4: Update settings
        settings_data = {"email_notifications": False}
        response = client.put("/api/users/me/settings", json=settings_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Step 5: Verify profile still accessible
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        final_profile = response.json()
        assert final_profile["display_name"] == "Workflow Comedian"

class TestUserProfileWithVideos:
    """Test user profile functionality with videos"""
    
    def test_profile_video_counts(self, client, mock_firebase_token, auth_headers, test_user, db_session):
        """Test that profile shows correct video counts and like totals"""
        from models.models import Video, Like
        
        # Create videos for the user
        video1 = Video(
            user_id=test_user.id,
            firebase_uid=test_user.firebase_uid,
            title="Video 1",
            file_type="video",
            storage_key="test/video1.mp4",
            like_count=5
        )
        video2 = Video(
            user_id=test_user.id,
            firebase_uid=test_user.firebase_uid,
            title="Video 2",
            file_type="video",
            storage_key="test/video2.mp4",
            like_count=3
        )
        
        db_session.add(video1)
        db_session.add(video2)
        db_session.commit()
        
        # Get profile
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["video_count"] == 2
        assert data["total_likes"] == 8  # 5 + 3
        
    def test_social_links_json_handling(self, client, mock_firebase_token, auth_headers, db_session):
        """Test proper JSON handling for social links"""
        update_data = {
            "social_links": {
                "twitter": "@comedian",
                "instagram": "comedian_official",
                "tiktok": "@funny_comedian",
                "website": "https://comedian.com"
            }
        }
        
        response = client.put("/api/users/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Verify social links are properly stored and retrieved
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        social_links = data["social_links"]
        assert social_links["twitter"] == "@comedian"
        assert social_links["instagram"] == "comedian_official"
        assert social_links["tiktok"] == "@funny_comedian"
        assert social_links["website"] == "https://comedian.com" 