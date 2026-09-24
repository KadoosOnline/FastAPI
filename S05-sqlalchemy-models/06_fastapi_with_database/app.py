"""FastAPI + SQLAlchemy: one session per request.

The `yield` dependency of session 4 now opens a REAL session:

    def get_db():
        with SessionLocal() as session:
            yield session

    DbSession = Annotated[Session, Depends(get_db)]

The endpoint receives an ORM object from the database and returns it through
a Pydantic schema with `from_attributes=True` (session 3). The ORM model says
how data is STORED; the schema says what the client SEES.
"""

from collections.abc import Iterator
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

engine = create_engine('sqlite:///training.db')
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]


class CourseCreate(BaseModel):
    title: str = Field(min_length=3)
    price: int = Field(ge=0)


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: int


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]
Base.metadata.create_all(engine)
app = FastAPI()


@app.post('/courses', status_code=status.HTTP_201_CREATED)
def create_course(data: CourseCreate, db: DbSession) -> CourseRead:
    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)  # reload generated values (the id) from the database
    return CourseRead.model_validate(course)


@app.get('/courses')
def list_courses(db: DbSession) -> list[CourseRead]:
    courses = db.scalars(select(Course).order_by(Course.id)).all()
    return [CourseRead.model_validate(course) for course in courses]


@app.get('/courses/{course_id}')
def get_course(course_id: int, db: DbSession) -> CourseRead:
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Course not found')
    return CourseRead.model_validate(course)


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
