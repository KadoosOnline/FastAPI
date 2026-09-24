"""Typed domain models built with dataclasses."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from training_center.exceptions import ValidationError


def utc_now() -> datetime:
    return datetime.now(UTC)


class Role(StrEnum):
    ADMIN = 'admin'
    INSTRUCTOR = 'instructor'
    STUDENT = 'student'


@dataclass(slots=True, kw_only=True)
class User:
    id: int
    email: str
    full_name: str
    role: Role = Role.STUDENT
    is_active: bool = True
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        self.email = self.email.strip().lower()
        if '@' not in self.email or self.email.startswith('@'):
            raise ValidationError('email', f'invalid email address: {self.email!r}')
        if len(self.full_name.strip()) < 2:
            raise ValidationError('full_name', 'full name is too short')


@dataclass(slots=True, kw_only=True)
class Course:
    id: int
    title: str
    price: int
    capacity: int
    instructor_id: int
    student_ids: set[int] = field(default_factory=set)
    is_active: bool = True

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValidationError('price', 'price cannot be negative')
        if self.capacity <= 0:
            raise ValidationError('capacity', 'capacity must be positive')

    @property
    def seats_left(self) -> int:
        return self.capacity - len(self.student_ids)

    @property
    def is_full(self) -> bool:
        return self.seats_left <= 0
