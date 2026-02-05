"""S3-compatible client utilities for file storage (MinIO/AWS S3)"""
import io
from typing import Optional, BinaryIO
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.client import Config
from app.core.config import settings


class MinIOClient:
    """S3-compatible client wrapper for file operations (MinIO/AWS S3)"""

    def __init__(self):
        self._client = None
        self._bucket = settings.MINIO_BUCKET

    @property
    def client(self):
        """Lazy initialization of S3 client"""
        if self._client is None:
            # Configure endpoint URL for MinIO compatibility
            endpoint_url = None
            if settings.MINIO_ENDPOINT:
                protocol = "https" if settings.MINIO_SECURE else "http"
                endpoint_url = f"{protocol}://{settings.MINIO_ENDPOINT}"
            
            # Configure boto3 client
            config = Config(
                signature_version='s3v4',
                s3={
                    'addressing_style': 'path'  # Required for MinIO compatibility
                }
            )
            
            self._client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                config=config
            )
        return self._client

    @property
    def bucket(self):
        return self._bucket

    def _ensure_bucket(self):
        """Ensure the bucket exists"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.client.create_bucket(Bucket=self.bucket)
                except ClientError as create_error:
                    raise Exception(f"Failed to create S3 bucket: {create_error}")
            else:
                raise Exception(f"Failed to access S3 bucket: {e}")

    def upload_file(self, object_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload file data to S3-compatible storage"""
        self._ensure_bucket()
        try:
            data_stream = io.BytesIO(file_data)
            self.client.put_object(
                Bucket=self.bucket,
                Key=object_name,
                Body=data_stream,
                ContentType=content_type
            )
            return object_name
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3 storage: {e}")

    def download_file(self, object_name: str) -> tuple[bytes, str]:
        """Download file from S3-compatible storage"""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=object_name)
            data = response['Body'].read()
            content_type = response.get('ContentType', 'application/octet-stream')
            return data, content_type
        except ClientError as e:
            raise Exception(f"Failed to download file from S3 storage: {e}")

    def delete_file(self, object_name: str) -> bool:
        """Delete file from S3-compatible storage"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3 storage: {e}")

    def copy_file(self, source_object: str, destination_object: str) -> str:
        """Copy a file within the S3-compatible bucket."""
        try:
            copy_source = {
                'Bucket': self.bucket,
                'Key': source_object
            }
            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket,
                Key=destination_object
            )
            return destination_object
        except ClientError as e:
            raise Exception(f"Failed to copy file in S3 storage: {e}")

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in S3-compatible storage"""
        try:
            self.client.head_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError:
            return False


# Global instance - now lazy and S3-compatible
minio_client = MinIOClient()