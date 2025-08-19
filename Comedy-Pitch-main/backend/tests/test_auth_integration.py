import pytest
from unittest.mock import patch
import firebase_admin
from firebase_admin import auth as firebase_auth

class TestFirebaseAuthIntegration:
    """Test Firebase authentication integration with new endpoints"""
    
    def test_firebase_token_verification(self, client):
        """Test Firebase token verification works"""
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.return_value = {
                "uid": "test-firebase-uid",
                "email": "firebase@example.com",
                "name": "Firebase User",
                "email_verified": True
            }
            
            headers = {"Authorization": "Bearer valid-firebase-token"}
            response = client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 200
            mock_verify.assert_called_once_with("valid-firebase-token")
            
    def test_invalid_firebase_token(self, client):
        """Test handling of invalid Firebase tokens"""
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.side_effect = firebase_auth.InvalidIdTokenError("Invalid token")
            
            headers = {"Authorization": "Bearer invalid-token"}
            response = client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 401
            assert "Invalid authentication token" in response.json()["detail"]
            
    def test_expired_firebase_token(self, client):
        """Test handling of expired Firebase tokens"""
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.side_effect = firebase_auth.ExpiredIdTokenError("Token expired")
            
            headers = {"Authorization": "Bearer expired-token"}
            response = client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 401
            assert "Invalid authentication token" in response.json()["detail"]
            
    def test_missing_authorization_header(self, client):
        """Test endpoints without authorization header"""
        response = client.get("/api/users/me")
        assert response.status_code == 401
        assert "Authorization header is required" in response.json()["detail"]
        
    def test_malformed_authorization_header(self, client):
        """Test malformed authorization header"""
        test_cases = [
            {"Authorization": "InvalidFormat"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Basic token"},  # Wrong type
        ]
        
        for headers in test_cases:
            response = client.get("/api/users/me", headers=headers)
            assert response.status_code == 401

class TestAuthWithExistingFirebaseRoutes:
    """Test that existing Firebase auth routes still work correctly"""
    
    def test_existing_register_route_still_works(self, client):
        """Test existing Firebase register route is preserved"""
        with patch('config.firebase_config.create_user') as mock_create:
            mock_create.return_value = {
                "uid": "new-user-uid",
                "email": "newuser@example.com"
            }
            
            user_data = {
                "email": "newuser@example.com",
                "password": "testpassword123",
                "displayName": "New User"
            }
            
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == 201
            
    def test_existing_login_route_still_works(self, client):
        """Test existing Firebase login route is preserved"""
        with patch('config.firebase_config.sign_in_user') as mock_signin:
            mock_signin.return_value = {
                "idToken": "test-id-token",
                "refreshToken": "test-refresh-token",
                "localId": "test-user-id"
            }
            
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = client.post("/auth/login", json=login_data)
            assert response.status_code == 200
            
    def test_existing_verify_token_route_still_works(self, client):
        """Test existing token verification route is preserved"""
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.return_value = {
                "uid": "verified-user-uid",
                "email": "verified@example.com"
            }
            
            response = client.post("/auth/verify-token", json={"token": "test-token"})
            assert response.status_code == 200

class TestUserCreationOnFirstAccess:
    """Test automatic user creation on first API access"""
    
    def test_user_created_on_first_profile_access(self, client, db_session):
        """Test that user is created in database on first profile access"""
        from models.models import User
        
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.return_value = {
                "uid": "first-time-user-uid",
                "email": "firsttime@example.com",
                "name": "First Time User",
                "email_verified": True
            }
            
            headers = {"Authorization": "Bearer new-user-token"}
            response = client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            
            # User should be created with Firebase data
            assert data["firebase_uid"] == "first-time-user-uid"
            assert data["email"] == "firsttime@example.com"
            assert data["display_name"] == "First Time User"
            
            # Verify user exists in database
            user = db_session.query(User).filter(
                User.firebase_uid == "first-time-user-uid"
            ).first()
            assert user is not None
            assert user.email == "firsttime@example.com"
            
    def test_existing_user_not_duplicated(self, client, test_user, mock_firebase_token, auth_headers):
        """Test that existing users are not duplicated on subsequent access"""
        # First access - should return existing user
        response1 = client.get("/api/users/me", headers=auth_headers)
        assert response1.status_code == 200
        user_id_1 = response1.json()["id"]
        
        # Second access - should return same user
        response2 = client.get("/api/users/me", headers=auth_headers)
        assert response2.status_code == 200
        user_id_2 = response2.json()["id"]
        
        assert user_id_1 == user_id_2  # Same user ID

class TestAuthScopeAndPermissions:
    """Test authentication scope and permissions across endpoints"""
    
    def test_user_can_only_access_own_videos(self, client, db_session):
        """Test users can only access their own videos for private operations"""
        from models.models import User, Video
        
        # Create two users
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            # User 1
            mock_verify.return_value = {
                "uid": "user1-uid",
                "email": "user1@example.com",
                "name": "User One"
            }
            
            headers1 = {"Authorization": "Bearer user1-token"}
            response = client.get("/api/users/me", headers=headers1)
            user1_id = response.json()["id"]
            
            # Create video for user 1
            video_data = {
                "storage_key": "user1/video.mp4",
                "title": "User 1 Video",
                "file_type": "video"
            }
            
            with patch('storage.factory.get_storage') as mock_storage_factory:
                mock_storage = mock_storage_factory.return_value
                mock_storage.file_exists.return_value = True
                
                response = client.post("/api/videos/", json=video_data, headers=headers1)
                assert response.status_code == 200
                video_id = response.json()["id"]
            
            # User 2 tries to access user 1's video analytics
            mock_verify.return_value = {
                "uid": "user2-uid",
                "email": "user2@example.com",
                "name": "User Two"
            }
            
            headers2 = {"Authorization": "Bearer user2-token"}
            response = client.get(f"/api/videos/{video_id}/analytics", headers=headers2)
            assert response.status_code == 403  # Access denied
            
    def test_public_video_access_permissions(self, client, db_session):
        """Test public video access permissions work correctly"""
        from models.models import User, Video
        
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            # Create user and public video
            mock_verify.return_value = {
                "uid": "public-video-owner",
                "email": "publicowner@example.com",
                "name": "Public Owner"
            }
            
            headers1 = {"Authorization": "Bearer owner-token"}
            client.get("/api/users/me", headers=headers1)  # Create user
            
            # Create public video
            video_data = {
                "storage_key": "public/video.mp4",
                "title": "Public Video",
                "file_type": "video",
                "is_public": True
            }
            
            with patch('storage.factory.get_storage') as mock_storage_factory:
                mock_storage = mock_storage_factory.return_value
                mock_storage.file_exists.return_value = True
                
                response = client.post("/api/videos/", json=video_data, headers=headers1)
                video_id = response.json()["id"]
            
            # Different user should be able to view public video
            mock_verify.return_value = {
                "uid": "other-user-uid",
                "email": "other@example.com",
                "name": "Other User"
            }
            
            headers2 = {"Authorization": "Bearer other-token"}
            response = client.get(f"/api/videos/{video_id}", headers=headers2)
            assert response.status_code == 200
            
            # But should NOT be able to access analytics
            response = client.get(f"/api/videos/{video_id}/analytics", headers=headers2)
            assert response.status_code == 403

class TestMLAuthSecurity:
    """Test ML endpoints security (should not require authentication)"""
    
    def test_ml_endpoints_no_auth_required(self, client, test_video):
        """Test ML endpoints don't require authentication (internal APIs)"""
        # Processing status update
        status_data = {
            "video_id": test_video.id,
            "status": "processing"
        }
        response = client.post("/api/ml/processing-status", json=status_data)
        assert response.status_code == 200
        
        # ML results submission
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.0.0",
            "transcript": [],
            "overall_funniness_score": 0.5
        }
        response = client.post("/api/ml/score-results", json=ml_data)
        assert response.status_code == 200
        
        # Status retrieval
        response = client.get(f"/api/ml/video/{test_video.id}/status")
        assert response.status_code == 200
        
        # Health check
        response = client.get("/api/ml/health")
        assert response.status_code == 200

class TestAuthErrorHandling:
    """Test comprehensive auth error handling"""
    
    def test_firebase_service_unavailable(self, client):
        """Test handling when Firebase service is unavailable"""
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.side_effect = Exception("Firebase service unavailable")
            
            headers = {"Authorization": "Bearer valid-token"}
            response = client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 401
            
    def test_auth_with_database_error(self, client):
        """Test auth handling when database operations fail"""
        with patch('config.firebase_config.verify_firebase_token') as mock_verify:
            mock_verify.return_value = {
                "uid": "db-error-user",
                "email": "dberror@example.com",
                "name": "DB Error User"
            }
            
            with patch('config.database.get_db') as mock_get_db:
                mock_get_db.side_effect = Exception("Database connection failed")
                
                headers = {"Authorization": "Bearer token"}
                response = client.get("/api/users/me", headers=headers)
                
                # Should handle gracefully
                assert response.status_code in [500, 503]  # Server error

class TestAuthPerformance:
    """Test auth performance and caching"""
    
    def test_token_verification_called_once_per_request(self, client, mock_firebase_token, auth_headers):
        """Test that token verification is called once per request"""
        # Make request
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify mock was called exactly once
        mock_firebase_token.assert_called_once()
        
    def test_multiple_endpoints_same_request_token_reuse(self, client, mock_firebase_token, auth_headers):
        """Test that within a single request, user info is reused"""
        # This tests the dependency injection caching
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        # Should only call Firebase once per request
        assert mock_firebase_token.call_count == 1 