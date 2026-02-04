"""File download only. Uploads are handled at submission time."""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.repositories.forms import FormFileRepository
from app.utils.minio import minio_client

router = APIRouter()

# Directory for uploads: backend/uploads or env UPLOAD_DIR (fallback for local dev)
UPLOAD_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "uploads"))


@router.post("/upload")
async def upload_file():
    """Direct uploads are disabled; files are stored only on submission."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Direct uploads are disabled. Submit files with the form submission."
    )


@router.get("/{token}")
async def get_file(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download a file by token.
    Returns the file stream from MinIO or local storage.
    
    Performance: Streaming response for efficient file serving
    """
    rec = await FormFileRepository.get_by_token(db, token)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    # Try MinIO first (for new files)
    try:
        file_data, content_type = minio_client.download_file(rec.storage_path)
        return Response(
            content=file_data,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={rec.original_filename}"}
        )
    except Exception:
        # Fallback to local storage for existing files
        full_path = os.path.join(UPLOAD_BASE, rec.storage_path)
        if not os.path.isfile(full_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage")
        
        from fastapi.responses import FileResponse
        return FileResponse(full_path, filename=rec.original_filename, media_type=rec.mime_type)
