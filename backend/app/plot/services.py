import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ForbiddenException, NotFoundException
from app.plot.models import Sheet
from app.plot.schemas import SheetCreate, SheetUpdate


class SheetService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _get_owned(self, sheet_id: uuid.UUID, user_id: uuid.UUID) -> Sheet:
        result = await self.db.execute(
            select(Sheet).where(Sheet.id == sheet_id, Sheet.is_deleted == False)  # noqa: E712
        )
        sheet = result.scalar_one_or_none()
        if not sheet:
            raise NotFoundException("Sheet not found")
        if sheet.user_id != user_id:
            raise ForbiddenException("Access denied")
        return sheet

    # ── CRUD ──────────────────────────────────────────────────────────────────

    async def create(self, user_id: uuid.UUID, data: SheetCreate) -> Sheet:
        sheet = Sheet(
            user_id=user_id,
            name=data.name,
            sheet_w=data.sheet_w,
            sheet_d=data.sheet_d,
            grid_step=data.grid_step,
            elements=data.elements,
        )
        self.db.add(sheet)
        await self.db.flush()
        await self.db.refresh(sheet)
        return sheet

    async def get(self, sheet_id: uuid.UUID, user_id: uuid.UUID) -> Sheet:
        return await self._get_owned(sheet_id, user_id)

    async def list(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 12,
        search: str | None = None,
    ) -> tuple[list[Sheet], int]:
        base = (
            select(Sheet)
            .where(Sheet.user_id == user_id, Sheet.is_deleted == False)  # noqa: E712
        )
        if search:
            base = base.where(Sheet.name.ilike(f"%{search}%"))

        total: int = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar_one()

        items = list(
            (
                await self.db.execute(
                    base.order_by(Sheet.updated_at.desc())
                    .offset((page - 1) * page_size)
                    .limit(page_size)
                )
            ).scalars().all()
        )
        return items, total

    async def update(self, sheet_id: uuid.UUID, user_id: uuid.UUID, data: SheetUpdate) -> Sheet:
        sheet = await self._get_owned(sheet_id, user_id)
        if data.name is not None:
            sheet.name = data.name
        if data.sheet_w is not None:
            sheet.sheet_w = data.sheet_w
        if data.sheet_d is not None:
            sheet.sheet_d = data.sheet_d
        if data.grid_step is not None:
            sheet.grid_step = data.grid_step
        if data.elements is not None:
            sheet.elements = data.elements
        await self.db.flush()
        await self.db.refresh(sheet)
        return sheet

    async def delete(self, sheet_id: uuid.UUID, user_id: uuid.UUID) -> None:
        sheet = await self._get_owned(sheet_id, user_id)
        sheet.is_deleted = True
        await self.db.flush()
