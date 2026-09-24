"""Pagination written once, used by every list endpoint."""

from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas import Page, PageParams


def paginate[S: BaseModel](
    db: Session,
    stmt: Select,
    params: PageParams,
    schema: type[S],  # type: ignore[type-arg]
) -> Page[S]:
    """Count the matching rows, fetch one page, convert every row with `schema`."""
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    rows = db.scalars(stmt.offset(params.offset).limit(params.size)).all()
    return Page[S](
        items=[schema.model_validate(row) for row in rows],
        total=total,
        page=params.page,
        size=params.size,
    )
