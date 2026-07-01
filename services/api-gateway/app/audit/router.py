import uuid
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.service import query_audit_logs
from app.common.responses import success_response
from app.database import get_db

router = APIRouter(tags=["admin-audit"])


async def _require_admin(request: Request) -> None:
    role = getattr(request.state, "user_role", None)
    if role not in ("admin", "superadmin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


@router.get("/audit")
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    user_id: uuid.UUID | None = Query(None),
    _: None = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    logs, total = await query_audit_logs(db, page, page_size, action, resource_type, user_id)
    total_pages = ceil(total / page_size) if total > 0 else 0
    return success_response(
        data={
            "items": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id) if log.user_id else None,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": str(log.resource_id) if log.resource_id else None,
                    "details": log.details,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
        message="Audit logs retrieved",
    )
