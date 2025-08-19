import os
from typing import Dict, Any, Optional
from minio import Minio
from minio.error import S3Error
from urllib.parse import urljoin
from datetime import timedelta

from storage.base import StorageBackend, UploadMetadata, PresignedUrlResponse

class MinIOStorage(StorageBackend):
    """MinIO storage backend for S3-compatible object storage"""
    
    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket_name: str = "comedy-peach",
        secure: bool = False
    ):
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.bucket_name = bucket_name
        self.secure = secure
        
        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def generate_presigned_url(
        self, 
        key: str, 
        expires_in: int = 300,  # 5 minutes default
        metadata: Optional[UploadMetadata] = None
    ) -> PresignedUrlResponse:
        """Generate a presigned URL for file upload"""
        try:
            # Generate presigned PUT URL
            # expires: The URL must be used to start the upload within this time window (not the total upload duration)
            url = self.client.presigned_put_object(
                self.bucket_name,
                key,
                expires=timedelta(seconds=expires_in)
            )
            
            return PresignedUrlResponse(
                upload_url=url,
                storage_key=key,
                expires_in=expires_in
            )
        except S3Error as e:
            raise Exception(f"Failed to generate presigned URL: {e}")
    
    def get_public_url(self, key: str) -> str:
        """Get public URL for a stored file"""
        # For MinIO, construct the public URL manually
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.endpoint}/{self.bucket_name}/{key}"
    
    def delete_file(self, key: str) -> bool:
        """Delete a file from MinIO storage"""
        try:
            self.client.remove_object(self.bucket_name, key)
            return True
        except S3Error:
            return False
    
    def file_exists(self, key: str) -> bool:
        """Check if a file exists in MinIO storage"""
        try:
            self.client.stat_object(self.bucket_name, key)
            return True
        except S3Error:
            return False
    
    def get_file_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a stored file"""
        try:
            stat = self.client.stat_object(self.bucket_name, key)
            return {
                "size": stat.size,
                "etag": stat.etag,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type,
                "metadata": stat.metadata
            }
        except S3Error:
            return None 