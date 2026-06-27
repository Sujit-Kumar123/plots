import logging
import uuid
from datetime import datetime, timedelta, timezone

from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobServiceClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import (
    ForbiddenException,
    InternalException,
    NotFoundException,
    ValidationException,
)
from app.config import settings
from app.uploads.models import FileUpload

logger = logging.getLogger(__name__)


def _get_blob_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)


async def upload_file(
    db: AsyncSession,
    user_id: uuid.UUID,
    file_name: str,
    content_type: str,
    file_data: bytes,
) -> FileUpload:
    blob_name = f"{user_id}/{uuid.uuid4()}/{file_name}"

    try:
        async with _get_blob_service_client() as blob_service:
            container_client = blob_service.get_container_client(settings.azure_storage_container)
            blob_client = container_client.get_blob_client(blob_name)
            await blob_client.upload_blob(file_data, content_type=content_type)
    except AzureError as exc:
        logger.error("Azure blob upload failed for user %s: %s", user_id, exc)
        raise InternalException("File upload failed, please try again")

    file_upload = FileUpload(
        user_id=user_id,
        file_name=file_name,
        blob_name=blob_name,
        content_type=content_type,
        size_bytes=len(file_data),
    )
    db.add(file_upload)
    try:
        await db.flush()
    except IntegrityError as exc:
        logger.error("DB integrity error saving file record: %s", exc)
        raise InternalException("File record could not be saved")
    except OperationalError as exc:
        logger.error("DB operational error saving file record: %s", exc)
        raise InternalException("Database error during file upload")
    return file_upload


async def get_file_with_url(db: AsyncSession, file_id: uuid.UUID, user_id: uuid.UUID) -> FileUpload:
    result = await db.execute(select(FileUpload).where(FileUpload.id == file_id, FileUpload.is_deleted == False))
    file_upload = result.scalar_one_or_none()
    if not file_upload:
        raise NotFoundException("File not found")
    return file_upload


def generate_signed_url(blob_name: str, expires_hours: int = 1) -> str:
    """Generate a signed URL for blob access."""
    parts = dict(item.split("=", 1) for item in settings.azure_storage_connection_string.split(";") if "=" in item)
    account_name = parts.get("AccountName", "")
    account_key = parts.get("AccountKey", "")

    if not account_name or not account_key:
        raise ValidationException("Azure storage credentials are not configured")

    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=settings.azure_storage_container,
        blob_name=blob_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=expires_hours),
    )
    return f"https://{account_name}.blob.core.windows.net/{settings.azure_storage_container}/{blob_name}?{sas_token}"


async def delete_file(db: AsyncSession, file_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool = False) -> None:
    result = await db.execute(select(FileUpload).where(FileUpload.id == file_id, FileUpload.is_deleted == False))
    file_upload = result.scalar_one_or_none()
    if not file_upload:
        raise NotFoundException("File not found")

    if file_upload.user_id != user_id and not is_admin:
        raise ForbiddenException("Cannot delete another user's file")

    try:
        async with _get_blob_service_client() as blob_service:
            container_client = blob_service.get_container_client(settings.azure_storage_container)
            blob_client = container_client.get_blob_client(file_upload.blob_name)
            await blob_client.delete_blob()
    except ResourceNotFoundError:
        logger.warning("Blob already deleted from storage: %s", file_upload.blob_name)
    except AzureError as exc:
        logger.error("Azure blob deletion failed for %s: %s", file_upload.blob_name, exc)
        raise InternalException("File deletion from storage failed")

    file_upload.is_deleted = True
    try:
        await db.flush()
    except OperationalError as exc:
        logger.error("DB error marking file as deleted: %s", exc)
        raise InternalException("Database error during file deletion")
