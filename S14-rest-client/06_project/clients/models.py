"""Typed models of the API's JSON, owned by the CLIENT.

They are deliberately NOT imported from the server's `app.schemas`: a real
client lives in another project and only knows the JSON contract. Unknown
fields are ignored, so a newer server does not break an older client.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Role = Literal['admin', 'instructor', 'student']
Level = Literal['beginner', 'intermediate', 'advanced']


class ApiModel(BaseModel):
    model_config = ConfigDict(extra='ignore', frozen=True)


class Token(ApiModel):
    access_token: str
    token_type: str
    expires_in: int


class User(ApiModel):
    id: int
    email: str
    full_name: str
    role: Role
    is_active: bool


class Instructor(ApiModel):
    id: int
    full_name: str
    email: str


class Course(ApiModel):
    id: int
    title: str
    description: str
    price: int
    capacity: int
    level: Level
    start_date: date | None = None
    is_active: bool
    instructor_id: int
    created_at: datetime
    instructor: Instructor | None = None  # only in GET /courses/{id}
    active_students: int | None = None  # only in GET /courses/{id}


class Page[T](ApiModel):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class Enrollment(ApiModel):
    id: int
    student_id: int
    course_id: int
    status: Literal['active', 'cancelled', 'completed']
    created_at: datetime
    course: Course | None = None


class Material(ApiModel):
    id: int
    course_id: int
    title: str
    original_filename: str
    content_type: str
    size_bytes: int
