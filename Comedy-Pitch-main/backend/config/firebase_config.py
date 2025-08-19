import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from typing import Dict, Any

# Global Firebase app instance
_firebase_app = None

def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        # Create service account credentials from environment variables
        service_account_info = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        }
        
        # Validate required fields
        required_fields = ["project_id", "private_key", "client_email"]
        missing_fields = [field for field in required_fields if not service_account_info.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required Firebase configuration: {', '.join(missing_fields)}")
        
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account_info)
        _firebase_app = firebase_admin.initialize_app(cred, {
            'projectId': service_account_info["project_id"]
        })
        
        print("✅ Firebase Admin SDK initialized successfully")
        return _firebase_app
        
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        print("Please check your environment variables in .env file")
        raise

def get_firebase_web_config() -> Dict[str, Any]:
    """Get Firebase web configuration for client-side use"""
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID")
    }

def verify_firebase_token(token: str) -> Dict[str, Any]:
    """Verify Firebase ID token and return decoded token"""
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")

def get_user_by_uid(uid: str) -> Dict[str, Any]:
    """Get user information by UID"""
    try:
        user_record = auth.get_user(uid)
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "emailVerified": user_record.email_verified,
            "disabled": user_record.disabled,
            "metadata": {
                "creationTime": user_record.user_metadata.creation_timestamp,
                "lastSignInTime": user_record.user_metadata.last_sign_in_timestamp,
            }
        }
    except Exception as e:
        raise ValueError(f"User not found: {str(e)}")

def list_all_users(max_results: int = 1000) -> Dict[str, Any]:
    """List all users with pagination"""
    try:
        users = []
        page = auth.list_users(max_results=max_results)
        
        for user in page.users:
            users.append({
                "uid": user.uid,
                "email": user.email,
                "emailVerified": user.email_verified,
                "disabled": user.disabled,
                "metadata": {
                    "creationTime": user.user_metadata.creation_timestamp,
                    "lastSignInTime": user.user_metadata.last_sign_in_timestamp,
                }
            })
        
        return {
            "users": users,
            "count": len(users)
        }
    except Exception as e:
        raise ValueError(f"Failed to list users: {str(e)}")

def create_custom_token(uid: str) -> str:
    """Create a custom token for a user"""
    try:
        custom_token = auth.create_custom_token(uid)
        return custom_token.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to create custom token: {str(e)}") 