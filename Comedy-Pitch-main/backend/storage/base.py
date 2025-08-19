from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class UploadMetadata:
    """Metadata for file uploads"""
    filename: str
    content_type: str
    content_length: Optional[int] = None
    additional_metadata: Optional[Dict[str, Any]] = None

@dataclass
class PresignedUrlResponse:
    """Response for presigned URL generation"""
    upload_url: str
    storage_key: str
    expires_in: int
    fields: Optional[Dict[str, str]] = None  # For form fields in POST uploads

class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def generate_presigned_url(
        self, 
        key: str, 
        expires_in: int = 3600,
        metadata: Optional[UploadMetadata] = None
    ) -> PresignedUrlResponse:
        """Generate a presigned URL for file upload"""
        pass
    
    @abstractmethod
    def get_public_url(self, key: str) -> str:
        """Get public URL for a stored file"""
        pass
    
    @abstractmethod
    def delete_file(self, key: str) -> bool:
        """Delete a file from storage"""
        pass
    
    @abstractmethod
    def file_exists(self, key: str) -> bool:
        """Check if a file exists in storage"""
        pass
    
    @abstractmethod
    def get_file_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a stored file"""
        pass 