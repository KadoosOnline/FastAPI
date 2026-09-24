"""In-memory storage. One object, shared by every request (until session 5)."""

from datetime import UTC, datetime

from app.schemas import CourseRead, EnrollmentRead, UserRead


def now() -> datetime:
    return datetime.now(UTC)


class Store:
    def __init__(self) -> None:
        self.users: dict[int, UserRead] = {}
        self.courses: dict[int, CourseRead] = {}
        self.enrollments: dict[int, EnrollmentRead] = {}
        self._seed()

    @staticmethod
    def next_id(table: dict) -> int:
        return max(table, default=0) + 1

    def _seed(self) -> None:
        self.users[1] = UserRead(
            id=1,
            email='teacher@kadoos.ir',
            full_name='Ali Teacher',
            role='instructor',
            created_at=now(),
        )
        self.users[2] = UserRead(
            id=2,
            email='sara@example.com',
            full_name='Sara Ahmadi',
            role='student',
            created_at=now(),
        )
        self.courses[1] = CourseRead(
            id=1,
            title='Python Basics',
            price=2_500_000,
            capacity=20,
            instructor_id=1,
            created_at=now(),
        )
        self.courses[2] = CourseRead(
            id=2,
            title='FastAPI',
            price=4_800_000,
            capacity=2,
            level='advanced',
            instructor_id=1,
            created_at=now(),
        )


store = Store()


def get_store() -> Store:
    return store
