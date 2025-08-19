import os
from typing import Optional

from storage.base import StorageBackend
from storage.minio_storage import MinIOStorage
from storage.s3_storage import S3Storage

def get_storage_backend() -> StorageBackend:
    """Get storage backend based on environment configuration"""
    storage_type = os.getenv("STORAGE_BACKEND", "minio").lower()
    
    if storage_type == "minio":
        return MinIOStorage(
            endpoint=os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            bucket_name=os.getenv("MINIO_BUCKET_NAME", "comedy-peach"),
            secure=os.getenv("MINIO_SECURE", "false").lower() == "true"
        )
    
    elif storage_type == "s3":
        return S3Storage(
            bucket_name=os.getenv("AWS_S3_BUCKET"),
            region=os.getenv("AWS_REGION"),
            access_key=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    else:
        raise ValueError(f"Unknown storage backend: {storage_type}. Supported backends: minio, s3")

# Global storage instance
_storage_backend: Optional[StorageBackend] = None

def get_storage() -> StorageBackend:
    """Get the configured storage backend (singleton)"""
    global _storage_backend
    if _storage_backend is None:
        _storage_backend = get_storage_backend()
    return _storage_backend 