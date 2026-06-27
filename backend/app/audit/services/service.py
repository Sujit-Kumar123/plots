import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditLog
from app.common.exceptions import InternalException
from app.common.pagination import PaginationParams

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    user_id: uuid.UUID | None,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
    )
    db.add(entry)
    try:
        await db.flush()
    except OperationalError as exc:
        logger.error("DB error writing audit log (action=%s resource=%s): %s", action, resource_type, exc)
        raise InternalException("Audit log could not be saved")
    return entry


async def query_audit_logs(
    db: AsyncSession,
    pagination: PaginationParams,
    action: str | None = None,
    resource_type: str | None = None,
    user_id: uuid.UUID | None = None,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog)

    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    count_query = select(func.count()).select_from(query.subquery())
    try:
        total = (await db.execute(count_query)).scalar_one()
    except OperationalError as exc:
        logger.error("DB error counting audit logs: %s", exc)
        raise InternalException("Could not retrieve audit logs")

    query = query.offset(pagination.offset).limit(pagination.page_size).order_by(AuditLog.created_at.desc())
    try:
        result = await db.execute(query)
    except OperationalError as exc:
        logger.error("DB error querying audit logs: %s", exc)
        raise InternalException("Could not retrieve audit logs")

    logs = list(result.scalars().all())
    return logs, total
