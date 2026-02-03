"""File upload and download with async I/O. POST /upload, GET /{token}"""
import os
import re
import uuid as _uuid
import time
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.forms import FormFile
from app.repositories.forms import FormFileRepository
from app.utils.response import create_response
from app.utils.minio import minio_client

router = APIRouter()

# Directory for uploads: backend/uploads or env UPLOAD_DIR (fallback for local dev)
UPLOAD_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "uploads"))


async def _ensure_upload_dir():
    """Ensure upload directory exists (async-safe)"""
    os.makedirs(UPLOAD_BASE, exist_ok=True)


def _safe_filename(name: str) -> str:
    """Sanitize filename to prevent directory traversal"""
    name = os.path.basename(name)
    return re.sub(r"[^\w\-_.]", "_", name)[:200]


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    field_id: str = Form(...),
    submission_id: int = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file with async I/O for better performance.
    Returns { token, field_id, original_filename, ... }.
    
    Performance optimization: Uses aiofiles for non-blocking file writes
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")
    
    # Read file content asynchronously
    content = await file.read()
    size = len(content)
    
    # Generate safe filename for MinIO object name
    fname = _safe_filename(file.filename)
    ts = int(time.time() * 1000)
    uid = str(_uuid.uuid4())[:8]
    object_name = f"file_{uid}_{ts}_{fname}"
    
    # Upload to MinIO
    try:
        minio_client.upload_file(object_name, content, file.content_type or "application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload file: {str(e)}")
    
    # Store object name in database (not local path)
    rec = FormFile(
        original_filename=file.filename,
        storage_path=object_name,  # This is now the MinIO object name
        mime_type=file.content_type or "application/octet-stream",
        file_size=size,
        submission_id=submission_id,
        field_id=field_id,
        uploaded_by=current_user.username,
    )
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    
    return create_response(data={
        "token": str(rec.token),
        "field_id": rec.field_id,
        "original_filename": rec.original_filename,
        "file_size": rec.file_size,
        "mime_type": rec.mime_type,
        "message": "File uploaded successfully",
    })


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
