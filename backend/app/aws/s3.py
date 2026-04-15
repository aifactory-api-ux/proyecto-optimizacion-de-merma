"""AWS S3 Integration Module

Provides S3 operations for the waste optimization system.
Handles file uploads, downloads, and bucket management for historical data storage.
"""

import logging
from typing import Optional, BinaryIO, List

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Manager:
    """AWS S3 manager for file operations.
    
    Provides a centralized interface for S3 operations including
    upload, download, list, and delete operations.
    
    Attributes:
        client: boto3 S3 client
        bucket_name: S3 bucket name from settings
    """
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None
    ):
        """Initialize S3 manager.
        
        Args:
            bucket_name: S3 bucket name (defaults to settings)
            region: AWS region (defaults to settings)
        """
        self._bucket_name = bucket_name or settings.AWS_S3_BUCKET
        self._region = region or settings.AWS_REGION
        self._client: Optional[boto3.client] = None
        self._initialized = False
    
    @property
    def is_connected(self) -> bool:
        """Check if S3 manager is connected."""
        return self._initialized
    
    def connect(self) -> bool:
        """Establish connection to S3.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not settings.AWS_S3_BUCKET:
            logger.warning("AWS_S3_BUCKET not configured, S3 operations will be disabled")
            return False
        
        try:
            config = Config(
                region_name=self._region,
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'standard'}
            )
            
            self._client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=config
            )
            
            # Verify connection by checking bucket exists
            self._client.head_bucket(Bucket=self._bucket_name)
            self._initialized = True
            logger.info(f"S3 connected: {self._bucket_name} in {self._region}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to connect to S3: {e}")
            self._initialized = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to S3: {e}")
            self._initialized = False
            return False
    
    def disconnect(self) -> None:
        """Close S3 connection."""
        self._client = None
        self._initialized = False
        logger.info("S3 disconnected")
    
    def upload_file(
        self,
        file_path: str,
        object_key: str,
        extra_args: Optional[dict] = None
    ) -> bool:
        """Upload a file to S3.
        
        Args:
            file_path: Local file path to upload
            object_key: S3 object key (path in bucket)
            extra_args: Optional extra arguments for upload
            
        Returns:
            True if upload successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            self._client.upload_file(
                file_path,
                self._bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            logger.info(f"Uploaded {file_path} to s3://{self._bucket_name}/{object_key}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to upload file: {e}")
            return False
    
    def upload_fileobj(
        self,
        file_obj: BinaryIO,
        object_key: str,
        extra_args: Optional[dict] = None
    ) -> bool:
        """Upload a file object to S3.
        
        Args:
            file_obj: File object to upload
            object_key: S3 object key (path in bucket)
            extra_args: Optional extra arguments for upload
            
        Returns:
            True if upload successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            self._client.upload_fileobj(
                file_obj,
                self._bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            logger.info(f"Uploaded file object to s3://{self._bucket_name}/{object_key}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to upload file object: {e}")
            return False
    
    def download_file(self, object_key: str, file_path: str) -> bool:
        """Download a file from S3.
        
        Args:
            object_key: S3 object key (path in bucket)
            file_path: Local file path to save
            
        Returns:
            True if download successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            self._client.download_file(self._bucket_name, object_key, file_path)
            logger.info(f"Downloaded s3://{self._bucket_name}/{object_key} to {file_path}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to download file: {e}")
            return False
    
    def download_fileobj(self, object_key: str, file_obj: BinaryIO) -> bool:
        """Download a file from S3 to a file object.
        
        Args:
            object_key: S3 object key (path in bucket)
            file_obj: File object to write to
            
        Returns:
            True if download successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            self._client.download_fileobj(self._bucket_name, object_key, file_obj)
            logger.info(f"Downloaded s3://{self._bucket_name}/{object_key} to file object")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to download file object: {e}")
            return False
    
    def list_objects(
        self,
        prefix: Optional[str] = None,
        max_keys: int = 1000
    ) -> List[dict]:
        """List objects in S3 bucket.
        
        Args:
            prefix: Optional prefix to filter objects
            max_keys: Maximum number of objects to return
            
        Returns:
            List of object metadata dictionaries
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return []
        
        try:
            response = self._client.list_objects_v2(
                Bucket=self._bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = response.get('Contents', [])
            logger.info(f"Listed {len(objects)} objects from s3://{self._bucket_name}")
            return objects
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to list objects: {e}")
            return []
    
    def delete_object(self, object_key: str) -> bool:
        """Delete an object from S3.
        
        Args:
            object_key: S3 object key (path in bucket)
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            self._client.delete_object(
                Bucket=self._bucket_name,
                Key=object_key
            )
            logger.info(f"Deleted s3://{self._bucket_name}/{object_key}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to delete object: {e}")
            return False
    
    def delete_objects(self, object_keys: List[str]) -> bool:
        """Delete multiple objects from S3.
        
        Args:
            object_keys: List of S3 object keys to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            objects = [{'Key': key} for key in object_keys]
            
            self._client.delete_objects(
                Bucket=self._bucket_name,
                Delete={
                    'Objects': objects,
                    'Quiet': True
                }
            )
            logger.info(f"Deleted {len(object_keys)} objects from s3://{self._bucket_name}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to delete objects: {e}")
            return False
    
    def get_object_url(self, object_key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a pre-signed URL for an object.
        
        Args:
            object_key: S3 object key (path in bucket)
            expires_in: URL expiration time in seconds
            
        Returns:
            Pre-signed URL string or None on error
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return None
        
        try:
            url = self._client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self._bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expires_in
            )
            return url
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    def get_object_metadata(self, object_key: str) -> Optional[dict]:
        """Get metadata for an S3 object.
        
        Args:
            object_key: S3 object key (path in bucket)
            
        Returns:
            Object metadata dictionary or None on error
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return None
        
        try:
            response = self._client.head_object(
                Bucket=self._bucket_name,
                Key=object_key
            )
            return response
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to get object metadata: {e}")
            return None
    
    def copy_object(
        self,
        source_key: str,
        destination_key: str
    ) -> bool:
        """Copy an object within S3.
        
        Args:
            source_key: Source object key
            destination_key: Destination object key
            
        Returns:
            True if copy successful, False otherwise
        """
        if not self._initialized or not self._client:
            logger.error("S3 client not initialized")
            return False
        
        try:
            copy_source = {
                'Bucket': self._bucket_name,
                'Key': source_key
            }
            
            self._client.copy_object(
                CopySource=copy_source,
                Bucket=self._bucket_name,
                Key=destination_key
            )
            logger.info(f"Copied s3://{self._bucket_name}/{source_key} to s3://{self._bucket_name}/{destination_key}")
            return True
            
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to copy object: {e}")
            return False


# Global S3 manager instance
_s3_manager: Optional[S3Manager] = None


def get_s3_manager() -> S3Manager:
    """Get the global S3 manager instance.
    
    Returns:
        S3Manager: Global S3 manager
    """
    global _s3_manager
    if _s3_manager is None:
        _s3_manager = S3Manager()
    return _s3_manager


def init_s3() -> bool:
    """Initialize S3 connection.
    
    Returns:
        True if initialization successful, False otherwise
    """
    manager = get_s3_manager()
    return manager.connect()
