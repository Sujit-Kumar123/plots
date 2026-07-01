import uuid

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.auth.models import User
from app.common.responses import success_response
from app.database import get_db
from app.uploads.schemas import FileUploadResponse
from app.uploads.service import delete_file, generate_signed_url, get_file_with_url, upload_file

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("")
async def create_upload(
    file: UploadFile,
    current_user: User = Depends(require_permission("uploads:write")),
    db: AsyncSession = Depends(get_db),
):
    file_data = await file.read()
    file_upload = await upload_file(
        db, current_user.id, file.filename or "unnamed", file.content_type or "application/octet-stream", file_data
    )
    return success_response(data=FileUploadResponse.model_validate(file_upload).model_dump())


@router.get("/{file_id}")
async def get_upload(
    file_id: uuid.UUID,
    current_user: User = Depends(require_permission("uploads:read")),
    db: AsyncSession = Depends(get_db),
):
    file_upload = await get_file_with_url(db, file_id, current_user.id)
    response = FileUploadResponse.model_validate(file_upload)
    response.url = generate_signed_url(file_upload.blob_name)
    return success_response(data=response.model_dump())


@router.delete("/{file_id}")
async def remove_upload(
    file_id: uuid.UUID,
    current_user: User = Depends(require_permission("uploads:delete")),
    db: AsyncSession = Depends(get_db),
):
    is_admin = bool(current_user.role and current_user.role.short_name in ("admin", "superadmin"))
    await delete_file(db, file_id, current_user.id, is_admin)
    return success_response(message="File deleted")
