"""Pagination written once, used by every list endpoint (async version)."""

from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Page, PageParams


async def paginate[S: BaseModel](
    db: AsyncSession,
    stmt: Select,
    params: PageParams,
    schema: type[S],  # type: ignore[type-arg]
) -> Page[S]:
    total = await db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    rows = (await db.scalars(stmt.offset(params.offset).limit(params.size))).all()
    return Page[S](
        items=[schema.model_validate(row) for row in rows],
        total=total,
        page=params.page,
        size=params.size,
    )
