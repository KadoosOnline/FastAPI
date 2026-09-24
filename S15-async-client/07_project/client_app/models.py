"""Typed models of the JSON this app needs -- and nothing more."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    model_config = ConfigDict(extra='ignore', frozen=True)


class Token(ApiModel):
    access_token: str
    expires_in: int


class User(ApiModel):
    id: int
    email: str
    full_name: str
    role: Literal['admin', 'instructor', 'student']


class Course(ApiModel):
    id: int
    title: str
    price: int
    capacity: int
    level: str
    instructor_id: int


class CoursePage(ApiModel):
    items: list[Course]
    total: int
    page: int
    pages: int


class Student(ApiModel):
    student_id: int
    full_name: str
    email: str
    status: Literal['active', 'cancelled', 'completed']
    enrolled_at: datetime
