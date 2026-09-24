"""Authorization rules that depend on the data, not only on the role."""

from app.exceptions import PermissionDeniedError
from app.models import Course, User


def can_manage_course(course: Course, user: User) -> bool:
    """Admins manage every course; instructors only their own."""
    if user.role == 'admin':
        return True
    return user.role == 'instructor' and course.instructor_id == user.id


def ensure_can_manage_course(course: Course, user: User) -> None:
    if not can_manage_course(course, user):
        raise PermissionDeniedError('You can only manage your own courses')
