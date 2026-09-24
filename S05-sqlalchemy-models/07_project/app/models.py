"""Database tables as typed Python classes (SQLAlchemy 2.x).

Relationships (course.instructor, user.enrollments, ...) come in session 7.
For now the tables are linked only by their foreign-key columns.
"""

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), default='student')
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)


class Course(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        CheckConstraint('price >= 0', name='price_not_negative'),
        CheckConstraint('capacity > 0', name='capacity_positive'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str] = mapped_column(Text, default='')
    price: Mapped[int]
    capacity: Mapped[int]
    level: Mapped[str] = mapped_column(String(20), default='beginner')
    is_active: Mapped[bool] = mapped_column(default=True)
    instructor_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)


class Enrollment(Base):
    __tablename__ = 'enrollments'
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='one_enrollment_per_course'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete='CASCADE'))
    status: Mapped[str] = mapped_column(String(20), default='active')
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
