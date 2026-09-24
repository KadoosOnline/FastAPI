"""All the Pydantic schemas of the API, in one place.

For every resource: what may come IN (Create / Update) and what goes OUT
(Read). The routers never accept or return a plain dict any more.
"""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

Level = Literal['beginner', 'intermediate', 'advanced']
Role = Literal['admin', 'instructor', 'student']
Title = Annotated[str, Field(min_length=3, max_length=200)]
Price = Annotated[int, Field(ge=0, le=1_000_000_000, description='Price in Toman')]
Capacity = Annotated[int, Field(gt=0, le=500)]


# ---------- courses ----------
class CourseBase(BaseModel):
    title: Title
    description: str = Field(default='', max_length=2000)
    price: Price
    capacity: Capacity
    level: Level = 'beginner'

    @field_validator('title')
    @classmethod
    def clean_title(cls, value: str) -> str:
        return ' '.join(value.split())


class CourseCreate(CourseBase):
    instructor_id: int


class CourseUpdate(BaseModel):
    title: Title | None = None
    description: str | None = Field(default=None, max_length=2000)
    price: Price | None = None
    capacity: Capacity | None = None
    level: Level | None = None

    @model_validator(mode='after')
    def not_empty(self) -> Self:
        if not self.model_fields_set:
            raise ValueError('send at least one field to change')
        return self


class CourseRead(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime


# ---------- users ----------
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    role: Role = 'student'


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    created_at: datetime


# ---------- enrollments ----------
class EnrollmentCreate(BaseModel):
    student_id: int = Field(gt=0)


class EnrollmentRead(BaseModel):
    id: int
    student_id: int
    course_id: int
    status: Literal['active', 'cancelled'] = 'active'
    created_at: datetime
