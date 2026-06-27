import uuid
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.schemas import AuditLogResponse
from app.audit.services import query_audit_logs
from app.auth.dependencies import require_permission
from app.auth.models import User
from app.common.pagination import PaginatedResponse, PaginationParams
from app.common.responses import success_response
from app.database import get_db

router = APIRouter(prefix="/api/admin/audit", tags=["audit"])


@router.get("")
async def get_audit_logs(
    pagination: PaginationParams = Depends(),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    user_id: uuid.UUID | None = Query(None),
    current_user: User = Depends(require_permission("audit:read")),
    db: AsyncSession = Depends(get_db),
):
    logs, total = await query_audit_logs(db, pagination, action, resource_type, user_id)
    return success_response(
        data=PaginatedResponse(
            items=[AuditLogResponse.model_validate(log).model_dump() for log in logs],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=ceil(total / pagination.page_size) if total > 0 else 0,
        ).model_dump()
    )
