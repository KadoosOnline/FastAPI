"""Higher-order functions: functions that take or return functions.

    sorted(courses, key=lambda c: c.price)     # a function passed IN
    make_price_filter(1_000_000)               # a function coming OUT

Why a backend developer cares: FastAPI is built on this idea.
* You give FastAPI your function, and it calls it for you on each request.
* `Depends(get_db)` -- you pass a *function* that FastAPI calls to produce a value.
* A "dependency factory" like `require_role("admin")` (session 10) is a
  function that *returns* a new dependency function. That is a closure.

`Callable[[int], bool]` is the type hint for "a function that takes an int
and returns a bool".
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial, reduce


@dataclass
class Course:
    title: str
    price: int
    level: str


COURSES = [
    Course('Python Basics', 2_500_000, 'beginner'),
    Course('FastAPI', 4_800_000, 'advanced'),
    Course('HTML and CSS', 1_900_000, 'beginner'),
    Course('SQL', 2_900_000, 'intermediate'),
]

CoursePredicate = Callable[[Course], bool]


def make_max_price_filter(max_price: int) -> CoursePredicate:
    """Returns a NEW function that remembers `max_price` (a closure)."""

    def predicate(course: Course) -> bool:
        return course.price <= max_price

    return predicate


def make_level_filter(level: str) -> CoursePredicate:
    return lambda course: course.level == level


def all_of(*predicates: CoursePredicate) -> CoursePredicate:
    """Combine many filters into one -- this is how search filters are built."""
    return lambda course: all(predicate(course) for predicate in predicates)


def apply_discount(percent: int, price: int) -> int:
    return price * (100 - percent) // 100


def main() -> None:
    by_price = sorted(COURSES, key=lambda course: course.price)
    print([course.title for course in by_price])

    cheap_beginner = all_of(make_max_price_filter(2_600_000), make_level_filter('beginner'))
    print([course.title for course in filter(cheap_beginner, COURSES)])

    # map + partial: "fix" the first argument of a function
    ten_percent_off = partial(apply_discount, 10)
    print(list(map(ten_percent_off, [c.price for c in COURSES])))

    # reduce: fold a list into one value (sum() is a special case of it)
    total = reduce(lambda acc, course: acc + course.price, COURSES, 0)
    print(f'total: {total:,}')


if __name__ == '__main__':
    main()
