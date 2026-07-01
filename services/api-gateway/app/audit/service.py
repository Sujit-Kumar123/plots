"""Audit log writer and reader — operates directly on the DB."""
import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditLog
from app.database import AsyncSessionFactory

logger = logging.getLogger(__name__)


async def log_action(
    user_id: uuid.UUID | None,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Write an audit event directly to the DB. Never raises — errors are logged only."""
    try:
        async with AsyncSessionFactory() as session:
            session.add(
                AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details or {},
                    ip_address=ip_address,
                )
            )
            await session.commit()
    except Exception as exc:
        logger.error("audit_write_failed action=%s error=%s", action, exc)


async def query_audit_logs(
    db: AsyncSession,
    page: int,
    page_size: int,
    action: str | None = None,
    resource_type: str | None = None,
    user_id: uuid.UUID | None = None,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog).where(AuditLog.is_deleted.is_(False))

    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = (
        query.offset((page - 1) * page_size)
        .limit(page_size)
        .order_by(AuditLog.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total
