"""API schemas. `from_attributes=True` lets them read SQLAlchemy objects."""

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

Level = Literal['beginner', 'intermediate', 'advanced']
Role = Literal['admin', 'instructor', 'student']
Title = Annotated[str, Field(min_length=3, max_length=200)]
Price = Annotated[int, Field(ge=0, le=1_000_000_000, description='Price in Toman')]
Capacity = Annotated[int, Field(gt=0, le=500)]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


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


class CourseReplace(CourseBase):
    """PUT: the complete new state (the instructor does not change here)."""

    is_active: bool


class CourseUpdate(BaseModel):
    """PATCH: only the fields that are sent are changed."""

    title: Title | None = None
    description: str | None = Field(default=None, max_length=2000)
    price: Price | None = None
    capacity: Capacity | None = None
    level: Level | None = None
    is_active: bool | None = None

    @model_validator(mode='after')
    def not_empty_and_no_nulls(self) -> Self:
        if not self.model_fields_set:
            raise ValueError('send at least one field to change')
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f'{name} can not be null')
        return self


class CourseRead(CourseBase, ORMModel):
    id: int
    is_active: bool
    instructor_id: int
    created_at: datetime


# ---------- users ----------
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    role: Role = 'student'


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    role: Role | None = None
    is_active: bool | None = None


class UserRead(ORMModel):
    id: int
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
    created_at: datetime


# ---------- enrollments ----------
class EnrollmentCreate(BaseModel):
    student_id: int = Field(gt=0)


class EnrollmentRead(ORMModel):
    id: int
    student_id: int
    course_id: int
    status: str
    created_at: datetime
