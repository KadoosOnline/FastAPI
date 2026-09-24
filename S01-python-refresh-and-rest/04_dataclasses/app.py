"""Dataclasses: typed data models with almost no code.

A backend is mostly *data moving around*: a user, a course, an enrollment.
`@dataclass` writes `__init__`, `__repr__` and `__eq__` for us from the
type-hinted fields.

Options we use a lot:
    @dataclass(slots=True)     less memory, and no typos like `user.emial = ...`
    @dataclass(frozen=True)    immutable: a value object (money, an address)
    @dataclass(kw_only=True)   callers must write names: User(id=1, email=...)
    field(default_factory=...) a fresh default for every object (lists, dates)
    __post_init__              validate or normalise right after creation

Why this matters for FastAPI: in session 3 we switch to Pydantic's
`BaseModel`, which looks almost the same but also *validates and converts*
data coming from JSON. Knowing dataclasses makes Pydantic feel familiar.
"""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class Role(StrEnum):
    """A StrEnum is a str too: Role.ADMIN == "admin" is True. Great for JSON."""

    ADMIN = 'admin'
    INSTRUCTOR = 'instructor'
    STUDENT = 'student'


def utc_now() -> datetime:
    return datetime.now(UTC)


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
        if '@' not in self.email:
            raise ValueError(f'invalid email: {self.email!r}')


@dataclass(frozen=True, slots=True)
class Money:
    amount: int
    currency: str = 'IRT'

    def __add__(self, other: 'Money') -> 'Money':
        if other.currency != self.currency:
            raise ValueError('cannot add different currencies')
        return Money(self.amount + other.amount, self.currency)


@dataclass(slots=True, kw_only=True)
class Course:
    id: int
    title: str
    price: Money
    capacity: int
    student_ids: list[int] = field(default_factory=list)  # NOT `= []`

    @property
    def seats_left(self) -> int:
        return self.capacity - len(self.student_ids)


def main() -> None:
    sara = User(id=1, email='  Sara@Example.COM ', full_name='Sara')
    print(sara)  # a readable __repr__ for free
    print(sara.role == 'student')  # True: StrEnum compares with str

    course = Course(id=1, title='FastAPI', price=Money(4_800_000), capacity=2)
    course.student_ids.append(sara.id)
    print(course.seats_left)
    print(course.price + Money(200_000))

    # asdict() turns the object into plain dicts -- one step before JSON.
    print(asdict(course))

    try:
        # mypy reports this line before we even run it; Python refuses it at run time.
        course.price.amount = 0  # type: ignore[misc]
    except AttributeError as error:
        print('frozen:', error)

    try:
        User(id=2, email='not-an-email', full_name='X')
    except ValueError as error:
        print('rejected:', error)


if __name__ == '__main__':
    main()
