"""Write pagination ONCE: a generic `Page[T]` and a `paginate()` helper.

Every list endpoint needs the same four steps: count, order, offset/limit,
wrap in a page. Copy-pasting them into every endpoint means copy-pasting the
bugs too. Generics (session 1) let one function serve every model:

    class Page[T](BaseModel):           Page[CourseRead], Page[UserRead], ...
    def paginate(db, stmt, params, schema) -> Page[...]

and a `PageParams` dependency reads `page` and `size` for every endpoint.
"""

import math
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field, computed_field
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from database import Course, User, get_db, rebuild


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    size: int

    @computed_field
    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.size)


def paginate[S: BaseModel](
    db: Session,
    stmt: Select,
    params: PageParams,
    schema: type[S],  # type: ignore[type-arg]
) -> Page[S]:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    rows = db.scalars(stmt.offset((params.page - 1) * params.size).limit(params.size)).all()
    return Page[S](
        items=[schema.model_validate(row) for row in rows],
        total=total,
        page=params.page,
        size=params.size,
    )


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: int


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str


DbSession = Annotated[Session, Depends(get_db)]
Paging = Annotated[PageParams, Query()]

rebuild()
app = FastAPI()


@app.get('/courses')
def list_courses(db: DbSession, paging: Paging) -> Page[CourseRead]:
    return paginate(db, select(Course).order_by(Course.id), paging, CourseRead)


@app.get('/users')
def list_users(db: DbSession, paging: Paging) -> Page[UserRead]:
    return paginate(db, select(User).order_by(User.full_name, User.id), paging, UserRead)


if __name__ == '__main__':
    uvicorn.run('03_reusable_paginate:app', reload=True)
