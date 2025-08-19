import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from storage.base import StorageBackend, UploadMetadata, PresignedUrlResponse
from storage.factory import get_storage_backend, get_storage

class TestStorageBase:
    """Test storage base classes and interfaces"""
    
    def test_upload_metadata_creation(self):
        """Test UploadMetadata dataclass"""
        metadata = UploadMetadata(
            filename="test.mp4",
            content_type="video/mp4",
            content_length=1024
        )
        
        assert metadata.filename == "test.mp4"
        assert metadata.content_type == "video/mp4"
        assert metadata.content_length == 1024
        assert metadata.additional_metadata is None
        
    def test_presigned_url_response_creation(self):
        """Test PresignedUrlResponse dataclass"""
        response = PresignedUrlResponse(
            upload_url="http://example.com/upload",
            storage_key="test/video.mp4",
            expires_in=3600,
            fields={"key": "test/video.mp4"}
        )
        
        assert response.upload_url == "http://example.com/upload"
        assert response.storage_key == "test/video.mp4"
        assert response.expires_in == 3600
        assert response.fields["key"] == "test/video.mp4"

class TestStorageFactory:
    """Test storage factory functionality"""
    
    @patch('storage.factory.MinIOStorage')
    def test_get_minio_storage(self, mock_minio_class):
        """Test getting MinIO storage backend"""
        mock_instance = Mock()
        mock_minio_class.return_value = mock_instance
        
        with patch.dict(os.environ, {
            "STORAGE_BACKEND": "minio",
            "MINIO_ENDPOINT": "localhost:9000",
            "MINIO_ACCESS_KEY": "testkey",
            "MINIO_SECRET_KEY": "testsecret"
        }):
            storage = get_storage_backend()
            assert storage == mock_instance
            mock_minio_class.assert_called_once()
            
    @patch('storage.factory.S3Storage')
    def test_get_s3_storage(self, mock_s3_class):
        """Test getting S3 storage backend"""
        mock_instance = Mock()
        mock_s3_class.return_value = mock_instance
        
        with patch.dict(os.environ, {
            "STORAGE_BACKEND": "s3",
            "AWS_S3_BUCKET": "test-bucket",
            "AWS_REGION": "us-east-1"
        }):
            storage = get_storage_backend()
            assert storage == mock_instance
            mock_s3_class.assert_called_once()
            
    def test_invalid_storage_backend(self):
        """Test invalid storage backend raises error"""
        with patch.dict(os.environ, {"STORAGE_BACKEND": "invalid"}):
            with pytest.raises(ValueError, match="Unknown storage backend"):
                get_storage_backend()
                
    def test_storage_singleton(self):
        """Test storage singleton pattern"""
        with patch('storage.factory._storage_backend', None):
            with patch('storage.factory.get_storage_backend') as mock_get:
                mock_storage = Mock()
                mock_get.return_value = mock_storage
                
                # First call should create new instance
                storage1 = get_storage()
                assert storage1 == mock_storage
                mock_get.assert_called_once()
                
                # Second call should return same instance
                storage2 = get_storage()
                assert storage2 == mock_storage
                # Should not call get_storage_backend again
                mock_get.assert_called_once()

class TestMinIOStorageMocking:
    """Test MinIO storage with mocked dependencies"""
    
    @patch('storage.minio_storage.Minio')
    def test_minio_initialization(self, mock_minio_class):
        """Test MinIO storage initialization"""
        mock_client = Mock()
        mock_minio_class.return_value = mock_client
        mock_client.bucket_exists.return_value = False
        
        from storage.minio_storage import MinIOStorage
        
        storage = MinIOStorage(
            endpoint="localhost:9000",
            access_key="testkey",
            secret_key="testsecret",
            bucket_name="test-bucket"
        )
        
        assert storage.endpoint == "localhost:9000"
        assert storage.access_key == "testkey"
        assert storage.secret_key == "testsecret"
        assert storage.bucket_name == "test-bucket"
        mock_client.make_bucket.assert_called_once_with("test-bucket")
        
    @patch('storage.minio_storage.Minio')
    def test_minio_presigned_url(self, mock_minio_class):
        """Test MinIO presigned URL generation"""
        mock_client = Mock()
        mock_minio_class.return_value = mock_client
        mock_client.bucket_exists.return_value = True
        mock_client.presigned_put_object.return_value = "http://minio/upload"
        
        from storage.minio_storage import MinIOStorage
        
        storage = MinIOStorage(
            endpoint="localhost:9000",
            access_key="testkey",
            secret_key="testsecret"
        )
        
        metadata = UploadMetadata(
            filename="test.mp4",
            content_type="video/mp4"
        )
        
        response = storage.generate_presigned_url("test/video.mp4", metadata=metadata)
        
        assert response.upload_url == "http://minio/upload"
        assert response.storage_key == "test/video.mp4"
        assert response.expires_in == 3600

class TestS3StorageMocking:
    """Test S3 storage with mocked dependencies"""
    
    @patch('storage.s3_storage.boto3')
    def test_s3_initialization(self, mock_boto3):
        """Test S3 storage initialization"""
        mock_session = Mock()
        mock_s3_client = Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_s3_client
        mock_s3_client.head_bucket.return_value = {}
        
        from storage.s3_storage import S3Storage
        
        storage = S3Storage(
            bucket_name="test-bucket",
            region="us-east-1",
            access_key="testkey",
            secret_key="testsecret"
        )
        
        assert storage.bucket_name == "test-bucket"
        assert storage.region == "us-east-1"
        mock_boto3.Session.assert_called_once()
        
    @patch('storage.s3_storage.boto3')
    def test_s3_presigned_url(self, mock_boto3):
        """Test S3 presigned URL generation"""
        mock_session = Mock()
        mock_s3_client = Mock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_s3_client
        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.generate_presigned_post.return_value = {
            'url': 'http://s3/upload',
            'fields': {'key': 'test/video.mp4'}
        }
        
        from storage.s3_storage import S3Storage
        
        storage = S3Storage(
            bucket_name="test-bucket",
            region="us-east-1"
        )
        
        metadata = UploadMetadata(
            filename="test.mp4",
            content_type="video/mp4"
        )
        
        response = storage.generate_presigned_url("test/video.mp4", metadata=metadata)
        
        assert response.upload_url == "http://s3/upload"
        assert response.storage_key == "test/video.mp4"
        assert response.expires_in == 3600
        assert response.fields == {'key': 'test/video.mp4'} 