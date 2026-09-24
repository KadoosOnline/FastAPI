"""The fake database of session 3: dictionaries of Pydantic "Read" models."""

from datetime import UTC, datetime

from schemas import CourseRead, EnrollmentRead, UserRead


def now() -> datetime:
    return datetime.now(UTC)


USERS: dict[int, UserRead] = {
    1: UserRead(
        id=1,
        email='teacher@kadoos.ir',
        full_name='Ali Teacher',
        role='instructor',
        created_at=now(),
    ),
    2: UserRead(
        id=2, email='sara@example.com', full_name='Sara Ahmadi', role='student', created_at=now()
    ),
}

COURSES: dict[int, CourseRead] = {
    1: CourseRead(
        id=1, title='Python Basics', price=2_500_000, capacity=20, instructor_id=1, created_at=now()
    ),
    2: CourseRead(
        id=2,
        title='FastAPI',
        price=4_800_000,
        capacity=2,
        level='advanced',
        instructor_id=1,
        created_at=now(),
    ),
}

ENROLLMENTS: dict[int, EnrollmentRead] = {}


def next_id(table: dict) -> int:
    return max(table, default=0) + 1
