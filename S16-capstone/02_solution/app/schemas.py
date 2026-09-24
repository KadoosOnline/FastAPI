"""API schemas. `from_attributes=True` lets them read SQLAlchemy objects."""

import math
from datetime import date, datetime
from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

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
    start_date: date | None = None

    @field_validator('title')
    @classmethod
    def clean_title(cls, value: str) -> str:
        return ' '.join(value.split())


class CourseCreate(CourseBase):
    """Instructors create courses for themselves; an admin must name the instructor."""

    instructor_id: int | None = None


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
    start_date: date | None = None
    is_active: bool | None = None

    @model_validator(mode='after')
    def not_empty_and_no_nulls(self) -> Self:
        if not self.model_fields_set:
            raise ValueError('send at least one field to change')
        for name in self.model_fields_set - {'start_date'}:  # start_date may be cleared
            if getattr(self, name) is None:
                raise ValueError(f'{name} can not be null')
        return self


class CourseRead(CourseBase, ORMModel):
    id: int
    is_active: bool
    instructor_id: int
    created_at: datetime


# ---------- users ----------
def check_password_strength(value: str) -> str:
    if value.isdigit() or value.isalpha():
        raise ValueError('use letters AND digits')
    if value.lower() in {'password1', 'password123', 'qwerty123', '12345678a'}:
        raise ValueError('this password is too common')
    return value


Password = Annotated[
    str, Field(min_length=8, max_length=128), AfterValidator(check_password_strength)
]


class UserRegister(BaseModel):
    """Public sign-up. There is NO role field: everybody starts as a student."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: Password


class UserCreate(UserRegister):
    """Admins create users with any role."""

    role: Role = 'student'


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    role: Role | None = None
    is_active: bool | None = None


class UserUpdateMe(BaseModel):
    """PATCH /users/me: what a user may change about themself (not role, not is_active)."""

    full_name: str = Field(min_length=2, max_length=120)


class PasswordChange(BaseModel):
    old_password: str
    new_password: Password


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


# ---------- session 7: related data ----------
class InstructorSummary(ORMModel):
    id: int
    full_name: str
    email: EmailStr


class CourseDetail(CourseRead):
    instructor: InstructorSummary
    active_students: int


class CourseStudent(BaseModel):
    student_id: int
    full_name: str
    email: EmailStr
    status: str
    enrolled_at: datetime


class EnrollmentWithCourse(EnrollmentRead):
    course: CourseRead


class EnrollMany(BaseModel):
    course_ids: list[int] = Field(min_length=1, max_length=10)


# ---------- session 8: pagination, filtering, sorting ----------
CourseSort = Literal['title', '-title', 'price', '-price', 'start_date', '-start_date', 'id', '-id']


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class Page[T](BaseModel):
    """One page of any resource: Page[CourseRead], Page[UserRead], ..."""

    items: list[T]
    total: int
    page: int
    size: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pages(self) -> int:
        return math.ceil(self.total / self.size)


class UserQuery(PageParams):
    model_config = ConfigDict(extra='forbid')

    role: Role | None = None


class CourseQuery(PageParams):
    """Every option of GET /courses, read from the query string."""

    model_config = ConfigDict(extra='forbid')

    q: str | None = Field(default=None, min_length=2, max_length=50)
    level: Level | None = None
    instructor_id: int | None = None
    min_price: int | None = Field(default=None, ge=0)
    max_price: int | None = Field(default=None, ge=0)
    starts_after: date | None = None
    is_active: bool | None = True
    sort: CourseSort = 'id'

    @model_validator(mode='after')
    def check_price_range(self) -> Self:
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError('min_price is greater than max_price')
        return self


# ---------- sessions 9-10: authentication ----------
class Token(BaseModel):
    access_token: str
    token_type: Literal['bearer'] = 'bearer'
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """The claims inside our JWT access tokens."""

    sub: str  # the user id, as a string (JWT rule)
    role: Role
    exp: int
    iat: int


# ---------- session 11: course materials ----------
class MaterialRead(ORMModel):
    id: int
    course_id: int
    title: str
    original_filename: str
    content_type: str
    size_bytes: int
    uploaded_by_id: int | None
    created_at: datetime


# ---------- session 16: statistics ----------
class Stats(BaseModel):
    users_per_role: dict[str, int]
    active_courses: int
    enrollments_per_status: dict[str, int]
    top_courses: list[dict[str, int | str]]
