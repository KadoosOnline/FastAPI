"""One resource, three schemas: Create, Update, Read.

The data going IN and the data coming OUT are not the same shape:

    CourseCreate   what the client sends to create    (no id, no created_at)
    CourseUpdate   what the client sends to PATCH     (every field optional)
    CourseRead     what the API sends back            (id, created_at, ...)

Later there will also be a DATABASE model (session 5). Four classes for
one "course" can look like too much, but each one answers a different
question: "what may the client set?", "what may the client change?", "what
may the client see?", "how is it stored?". Mixing them is how APIs leak
passwords or let a student set `role: admin`.
"""

from datetime import UTC, datetime

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()


class CourseBase(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    price: int = Field(ge=0)
    capacity: int = Field(gt=0, le=500)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    price: int | None = Field(default=None, ge=0)
    capacity: int | None = Field(default=None, gt=0, le=500)


class CourseRead(CourseBase):
    id: int
    created_at: datetime


COURSES: dict[int, CourseRead] = {}


@app.post('/courses', status_code=status.HTTP_201_CREATED)
def create_course(data: CourseCreate) -> CourseRead:
    course = CourseRead(id=len(COURSES) + 1, created_at=datetime.now(UTC), **data.model_dump())
    COURSES[course.id] = course
    return course


@app.patch('/courses/{course_id}')
def update_course(course_id: int, data: CourseUpdate) -> CourseRead:
    if course_id not in COURSES:
        raise HTTPException(404, detail='Course not found')
    updated = COURSES[course_id].model_copy(update=data.model_dump(exclude_unset=True))
    COURSES[course_id] = updated
    return updated


@app.get('/courses')
def list_courses() -> list[CourseRead]:
    return list(COURSES.values())


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
