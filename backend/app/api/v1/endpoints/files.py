"""File upload and download with async I/O. POST /upload, GET /{token}"""
import os
import re
import uuid as _uuid
import time
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.forms import FormFile
from app.repositories.forms import FormFileRepository
from app.utils.response import create_response

router = APIRouter()

# Directory for uploads: backend/uploads or env UPLOAD_DIR
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
    await _ensure_upload_dir()
    
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")
    
    # Read file content asynchronously
    content = await file.read()
    size = len(content)
    
    # Generate safe filename
    fname = _safe_filename(file.filename)
    ts = int(time.time() * 1000)
    uid = str(_uuid.uuid4())[:8]
    storage_name = f"file_{uid}_{ts}_{fname}"
    storage_path = os.path.join(UPLOAD_BASE, storage_name)
    
    # Write file asynchronously (non-blocking)
    async with aiofiles.open(storage_path, "wb") as f:
        await f.write(content)
    
    # Store relative path for portability
    rel_path = storage_name
    
    # Create database record
    rec = FormFile(
        original_filename=file.filename,
        storage_path=rel_path,
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
    Returns the file stream.
    
    Performance: FileResponse handles streaming efficiently
    """
    rec = await FormFileRepository.get_by_token(db, token)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    full_path = os.path.join(UPLOAD_BASE, rec.storage_path)
    
    # Check file exists (async check would be ideal but os.path.isfile is fast enough)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")
    
    # FileResponse handles streaming efficiently
    return FileResponse(full_path, filename=rec.original_filename, media_type=rec.mime_type)
