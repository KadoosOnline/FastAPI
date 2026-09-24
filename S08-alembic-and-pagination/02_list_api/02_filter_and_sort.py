"""Filtering, search and sorting -- designed as query parameters.

All the list options are declared as ONE Pydantic model and read from the
query string with `Annotated[CourseQuery, Query()]`:

    /courses?q=py&level=advanced&min_price=2000000&sort=-price&page=2

Design rules:
* every parameter optional, with a sensible default
* validate everything (422 for `size=1000` or `min_price > max_price`)
* sorting from a WHITE LIST: the client picks a name, we map it to a column.
  Never pass the client's text into `order_by` directly.
* `extra='forbid'`: a typo like `?levle=advanced` is an error, not silently ignored
"""

import math
from typing import Annotated, Literal, Self

import uvicorn
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import Course, get_db, rebuild

SortField = Literal['title', '-title', 'price', '-price', 'id', '-id']

SORT_COLUMNS = {
    'title': Course.title.asc(),
    '-title': Course.title.desc(),
    'price': Course.price.asc(),
    '-price': Course.price.desc(),
    'id': Course.id.asc(),
    '-id': Course.id.desc(),
}


class CourseQuery(BaseModel):
    model_config = ConfigDict(extra='forbid')

    q: str | None = Field(default=None, min_length=2, max_length=50)
    level: Literal['beginner', 'intermediate', 'advanced'] | None = None
    min_price: int | None = Field(default=None, ge=0)
    max_price: int | None = Field(default=None, ge=0)
    is_active: bool | None = True
    sort: SortField = 'id'
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)

    @model_validator(mode='after')
    def check_prices(self) -> Self:
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError('min_price is greater than max_price')
        return self


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    level: str
    price: int


class CoursePage(BaseModel):
    items: list[CourseRead]
    total: int
    page: int
    size: int
    pages: int


rebuild()
app = FastAPI()


@app.get('/courses')
def list_courses(
    params: Annotated[CourseQuery, Query()], db: Annotated[Session, Depends(get_db)]
) -> CoursePage:
    stmt = select(Course)
    if params.q:
        stmt = stmt.where(Course.title.ilike(f'%{params.q}%'))
    if params.level:
        stmt = stmt.where(Course.level == params.level)
    if params.min_price is not None:
        stmt = stmt.where(Course.price >= params.min_price)
    if params.max_price is not None:
        stmt = stmt.where(Course.price <= params.max_price)
    if params.is_active is not None:
        stmt = stmt.where(Course.is_active == params.is_active)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(SORT_COLUMNS[params.sort], Course.id)  # id breaks ties
    courses = db.scalars(stmt.offset((params.page - 1) * params.size).limit(params.size)).all()
    return CoursePage(
        items=[CourseRead.model_validate(c) for c in courses],
        total=total,
        page=params.page,
        size=params.size,
        pages=math.ceil(total / params.size),
    )


if __name__ == '__main__':
    uvicorn.run('02_filter_and_sort:app', reload=True)
