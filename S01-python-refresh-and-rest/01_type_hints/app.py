"""Modern type hints: the language FastAPI reads.

In the Advanced Python course we wrote type hints mostly as documentation.
In FastAPI they become *instructions*. When you write

    def get_course(course_id: int, q: str | None = None): ...

FastAPI reads the hints and decides: `course_id` must be converted to `int`
(and a 422 error is returned if it cannot be), and `q` is optional.
So from today on: **every parameter and every return value gets a hint.**

The modern spellings (Python 3.10+). Never import `List`, `Dict`,
`Optional` from `typing` any more:

    list[str]            not  List[str]
    dict[str, int]       not  Dict[str, int]
    str | None           not  Optional[str]
    int | float          not  Union[int, float]
    tuple[int, str]      a pair: exactly two items
    tuple[int, ...]      any number of ints

Hints are NOT checked when the program runs. Python happily passes a `str`
where you promised an `int`. A *type checker* (mypy, or the one inside
VS Code / PyCharm) finds the mistake before you run anything:

    pip install mypy
    mypy app.py
"""

from typing import Literal

# A type alias: give a complicated type a name once, and reuse it.
Price = int  # Toman. Money is never a float!
Level = Literal['beginner', 'intermediate', 'advanced']  # only these 3 strings


def average_price(prices: list[Price]) -> float:
    """`list[Price]` in, `float` out. An empty list is handled, not crashed."""
    if not prices:
        return 0.0
    return sum(prices) / len(prices)


def find_course(courses: dict[int, str], course_id: int) -> str | None:
    """`str | None` tells every caller: "be ready, I may have nothing for you"."""
    return courses.get(course_id)


def describe(title: str, level: Level = 'beginner', tags: list[str] | None = None) -> str:
    """Never use a mutable default like `tags: list[str] = []` (it is shared!)."""
    tags = tags or []
    tag_text = ', '.join(tags) if tags else 'no tags'
    return f'{title} [{level}] ({tag_text})'


def split_name(full_name: str) -> tuple[str, str]:
    """A tuple with a fixed shape: (first name, last name)."""
    first, _, last = full_name.strip().partition(' ')
    return first, last


def main() -> None:
    courses: dict[int, str] = {1: 'Python', 2: 'FastAPI'}

    print(average_price([2_500_000, 4_800_000]))
    print(average_price([]))

    # The type checker forces us to handle the `None` case before using the value.
    title = find_course(courses, 3)
    if title is None:
        print('course 3 does not exist')
    else:
        print(title.upper())

    print(describe('FastAPI', 'advanced', ['web', 'api']))
    print(split_name('Sara Ahmadi'))

    # Try it: uncomment the next line and run `mypy app.py`.
    # describe('FastAPI', 'expert')   # error: "expert" is not a valid Level


if __name__ == '__main__':
    main()
