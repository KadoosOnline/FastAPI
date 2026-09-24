"""Serialization: from a model back to a dict or JSON.

    model_dump()                      -> dict
    model_dump(exclude={'password'})  -> dict without some fields
    model_dump(exclude_unset=True)    -> only fields that were given
    model_dump_json()                 -> JSON text (dates become ISO strings)

`@computed_field` adds a value that is calculated, not stored.

`from_attributes=True` lets a model read ANY object with attributes (a
dataclass, and in session 5 a SQLAlchemy row) -- not only dicts.
"""

from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: int
    capacity: int
    enrolled: int
    created_at: datetime

    @computed_field
    @property
    def seats_left(self) -> int:
        return self.capacity - self.enrolled


@dataclass
class CourseRow:
    """Pretend this came from a database."""

    id: int
    title: str
    price: int
    capacity: int
    enrolled: int
    created_at: datetime
    internal_note: str


def main() -> None:
    row = CourseRow(1, 'FastAPI', 4_800_000, 12, 10, datetime(2026, 9, 24, 18, 0), 'secret')

    course = CourseRead.model_validate(row)  # reads attributes, ignores internal_note
    print(course.model_dump())
    print(course.model_dump(include={'title', 'seats_left'}))
    print(course.model_dump_json(indent=2))


if __name__ == '__main__':
    main()
