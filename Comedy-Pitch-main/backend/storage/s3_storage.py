import os
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from storage.base import StorageBackend, UploadMetadata, PresignedUrlResponse

class S3Storage(StorageBackend):
    """AWS S3 storage backend for production"""
    
    def __init__(
        self,
        bucket_name: str = None,
        region: str = None,
        access_key: str = None,
        secret_key: str = None
    ):
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET", "comedy-peach-prod")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize S3 client
        session = boto3.Session(
            aws_access_key_id=access_key or os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=secret_key or os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region
        )
        
        self.s3_client = session.client('s3')
        
        # Verify credentials and bucket access
        self._verify_access()
    
    def _verify_access(self):
        """Verify AWS credentials and bucket access"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise Exception(f"S3 bucket '{self.bucket_name}' not found")
            elif error_code == '403':
                raise Exception(f"Access denied to S3 bucket '{self.bucket_name}'")
            else:
                raise Exception(f"S3 error: {e}")
        except NoCredentialsError:
            raise Exception("AWS credentials not found")
    
    def generate_presigned_url(
        self, 
        key: str, 
        expires_in: int = 3600,
        metadata: Optional[UploadMetadata] = None
    ) -> PresignedUrlResponse:
        """Generate a presigned URL for file upload"""
        try:
            conditions = []
            fields = {}
            
            if metadata:
                if metadata.content_type:
                    conditions.append(["starts-with", "$Content-Type", metadata.content_type])
                    fields["Content-Type"] = metadata.content_type
                
                if metadata.content_length:
                    conditions.append(["content-length-range", 1, metadata.content_length])
            
            # Generate presigned POST URL for better browser compatibility
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expires_in
            )
            
            return PresignedUrlResponse(
                upload_url=response['url'],
                storage_key=key,
                expires_in=expires_in,
                fields=response['fields']
            )
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {e}")
    
    def get_public_url(self, key: str) -> str:
        """Get public URL for a stored file"""
        if self.region == "us-east-1":
            return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
        else:
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
    
    def delete_file(self, key: str) -> bool:
        """Delete a file from S3 storage"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    def file_exists(self, key: str) -> bool:
        """Check if a file exists in S3 storage"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    def get_file_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a stored file"""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return {
                "size": response.get("ContentLength"),
                "etag": response.get("ETag"),
                "last_modified": response.get("LastModified"),
                "content_type": response.get("ContentType"),
                "metadata": response.get("Metadata", {})
            }
        except ClientError:
            return None 