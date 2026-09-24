"""Pagination: never return 10 000 rows in one response.

Two styles:
* offset/limit     ?page=3&size=10   ->  OFFSET 20 LIMIT 10   (simple, what we use)
* cursor           ?after=137        ->  WHERE id > 137       (for endless feeds)

A good page response tells the client where it is:

    {"items": [...], "total": 45, "page": 3, "size": 10, "pages": 5}

`total` needs a second, cheap query: SELECT count(*) with the same filters.
ALWAYS order a paginated query (by something unique, like the id), or rows
can appear on two pages or on none.

    python 01_pagination.py      then try /courses?page=5&size=10
"""

import math
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import Course, get_db, rebuild


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
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> CoursePage:
    stmt = select(Course).order_by(Course.id)
    total = db.scalar(select(func.count()).select_from(Course)) or 0
    courses = db.scalars(stmt.offset((page - 1) * size).limit(size)).all()
    return CoursePage(
        items=[CourseRead.model_validate(c) for c in courses],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size),
    )


if __name__ == '__main__':
    uvicorn.run('01_pagination:app', reload=True)
