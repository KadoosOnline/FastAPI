"""Generics: one class that works for many types, and stays type safe.

We will store users, courses and enrollments. Writing a `UserStore`,
a `CourseStore` and an `EnrollmentStore` would be the same code three times.
A *generic* class takes the type as a parameter:

    class Repository[T]:             # Python 3.12 syntax
        def get(self, item_id: int) -> T: ...

    users = Repository[User]()       # users.get(1) is a User
    courses = Repository[Course]()   # courses.get(1) is a Course

`[T: HasId]` adds a *bound*: T may be any type that has an `id`. We describe
"has an id" with a `Protocol` -- structural typing: a class does not need to
inherit from anything, it just needs the attribute ("duck typing, checked").

Where you will meet generics again in this course:
* `Page[CourseRead]` -- one pagination response model for every resource (S08)
* `Mapped[int]`, `Mapped[list["Course"]]` -- SQLAlchemy columns (S05)
* `list[CourseRead]` as a response model (S03)
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


class HasId(Protocol):
    id: int


class Repository[T: HasId]:
    """An in-memory store. Later in the course a database replaces the dict."""

    def __init__(self) -> None:
        self._items: dict[int, T] = {}

    def add(self, item: T) -> T:
        self._items[item.id] = item
        return item

    def get(self, item_id: int) -> T | None:
        return self._items.get(item_id)

    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        return [item for item in self._items.values() if predicate(item)]

    def __len__(self) -> int:
        return len(self._items)


@dataclass
class User:
    id: int
    email: str


@dataclass
class Course:
    id: int
    title: str
    price: int


def first_or_none[T](items: list[T]) -> T | None:
    """A generic *function*: returns the same type that the list holds."""
    return items[0] if items else None


def main() -> None:
    users = Repository[User]()
    courses = Repository[Course]()

    users.add(User(1, 'sara@example.com'))
    courses.add(Course(1, 'Python', 2_500_000))
    courses.add(Course(2, 'FastAPI', 4_800_000))

    cheap = courses.filter(lambda course: course.price < 3_000_000)
    print(cheap)

    course = first_or_none(cheap)  # the editor knows: Course | None
    if course:
        print(course.title)  # auto-completion works here

    user = users.get(1)
    print(user.email if user else 'no user')
    print(len(users), len(courses))


if __name__ == '__main__':
    main()
