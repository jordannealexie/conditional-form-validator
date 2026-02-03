"""MinIO client utilities for file storage"""
import io
from typing import Optional, BinaryIO
from minio import Minio
from minio.error import S3Error
from app.core.config import settings


class MinIOClient:
    """MinIO client wrapper for file operations"""

    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Ensure the bucket exists"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            raise Exception(f"Failed to create/access MinIO bucket: {e}")

    def upload_file(self, object_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload file data to MinIO"""
        try:
            data_stream = io.BytesIO(file_data)
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=data_stream,
                length=len(file_data),
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            raise Exception(f"Failed to upload file to MinIO: {e}")

    def download_file(self, object_name: str) -> tuple[bytes, str]:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(self.bucket, object_name)
            data = response.read()
            content_type = response.headers.get('content-type', 'application/octet-stream')
            response.close()
            response.release_conn()
            return data, content_type
        except S3Error as e:
            raise Exception(f"Failed to download file from MinIO: {e}")

    def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket, object_name)
            return True
        except S3Error as e:
            raise Exception(f"Failed to delete file from MinIO: {e}")

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in MinIO"""
        try:
            self.client.stat_object(self.bucket, object_name)
            return True
        except S3Error:
            return False


# Global instance
minio_client = MinIOClient()