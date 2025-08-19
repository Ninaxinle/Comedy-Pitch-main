import pytest
import os
import uuid
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

# CRITICAL: Mock Firebase BEFORE importing the app
# This prevents Firebase initialization during app import
firebase_mock_patcher = None
auth_mock_patcher = None

def setup_firebase_mocks():
    """Set up Firebase mocks before app import"""
    global firebase_mock_patcher, auth_mock_patcher
    
    # Mock firebase_admin.initialize_app to prevent actual Firebase initialization
    firebase_mock_patcher = patch('firebase_admin.initialize_app')
    firebase_mock_patcher.start()
    
    # Mock firebase_admin.auth.verify_id_token for authentication
    auth_mock_patcher = patch('firebase_admin.auth.verify_id_token')
    mock_verify = auth_mock_patcher.start()
    
    # Default mock return value for token verification
    mock_verify.return_value = {
        "uid": "test-uid-123",
        "email": "test@example.com",
        "name": "Test User",
        "email_verified": True
    }
    
    return mock_verify

# Setup Firebase mocks before any imports
setup_firebase_mocks()

# Now import the app (after Firebase is mocked)
from main import app
from config.database import get_db, Base
from models.models import User, Video, Like, AnalyticsData

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine with unique name per session"""
    db_name = f"test_comedy_{uuid.uuid4().hex[:8]}.db"
    database_url = f"sqlite:///./{db_name}"
    
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup: Close engine and remove test database
    engine.dispose()
    try:
        os.remove(db_name)
    except:
        pass

@pytest.fixture
def db_session(engine):
    """Create a fresh database session for each test with proper isolation"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    # Use nested transaction for proper test isolation
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    yield session
    
    # Rollback the transaction to ensure test isolation
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create test client with overridden database dependency"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency override
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    """Create a test user for use in tests"""
    user = User(
        firebase_uid="test-uid-123",
        email="test@example.com",
        display_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_video(db_session, test_user):
    """Create a test video for use in tests"""
    video = Video(
        user_id=test_user.id,
        firebase_uid=test_user.firebase_uid,
        title="Test Comedy Video",
        file_type="video",
        storage_key="test/video.mp4",
        is_public=True
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video

@pytest.fixture
def mock_firebase_token():
    """Mock Firebase token verification with configurable return values"""
    with patch('config.firebase_config.verify_firebase_token') as mock_verify:
        mock_verify.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "Test User",
            "email_verified": True
        }
        yield mock_verify

@pytest.fixture
def auth_headers():
    """Standard authentication headers for API calls"""
    return {"Authorization": "Bearer mock-token"}

@pytest.fixture
def mock_storage():
    """Mock storage backend for file operations"""
    with patch('storage.factory.get_storage') as mock_storage_factory:
        mock_storage = MagicMock()
        mock_storage.generate_presigned_upload_url.return_value = "https://mock-upload-url.com"
        mock_storage.generate_presigned_url.return_value = "https://mock-download-url.com"
        mock_storage.file_exists.return_value = True
        mock_storage.delete_file.return_value = True
        mock_storage_factory.return_value = mock_storage
        yield mock_storage

@pytest.fixture
def test_video_data():
    """Sample video data for testing"""
    return {
        "storage_key": "test/sample_video.mp4",
        "title": "Sample Test Video",
        "description": "A test video for unit testing",
        "file_type": "video",
        "duration": 120.5,
        "is_public": True
    }

@pytest.fixture
def test_analytics_data():
    """Sample analytics data for testing"""
    return {
        "funniness_score": 8.5,
        "confidence_score": 0.92,
        "transcript": "This is a test transcript for comedy analysis",
        "processing_status": "completed",
        "laugh_timestamps": [15.2, 32.8, 45.1, 78.9],
        "key_moments": [
            {"timestamp": 15.2, "type": "punchline", "confidence": 0.85},
            {"timestamp": 45.1, "type": "callback", "confidence": 0.78}
        ],
        "humor_analysis": {
            "style": "observational",
            "themes": ["daily life", "relationships"],
            "sentiment": "positive"
        }
    }

def pytest_configure(config):
    """Configure pytest to handle our custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )

def pytest_unconfigure():
    """Clean up mocks when pytest exits"""
    global firebase_mock_patcher, auth_mock_patcher
    
    if firebase_mock_patcher:
        firebase_mock_patcher.stop()
    if auth_mock_patcher:
        auth_mock_patcher.stop() 