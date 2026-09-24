r"""`Field(...)`: rules for one field.

    title: str = Field(min_length=3, max_length=200)
    price: int = Field(ge=0)                 ge = greater or equal
    capacity: int = Field(gt=0, le=500)      gt = greater than, le = less or equal
    code: str = Field(pattern=r'^[A-Z]{3}-\d{3}$')

With `Annotated` (session 1) a rule can be defined ONCE and reused:

    Price = Annotated[int, Field(ge=0, description='Price in Toman')]

`description` and `examples` appear in /docs.
"""

from typing import Annotated

from pydantic import BaseModel, Field, ValidationError

Price = Annotated[int, Field(ge=0, le=1_000_000_000, description='Price in Toman')]
Title = Annotated[str, Field(min_length=3, max_length=200)]


class Course(BaseModel):
    title: Title
    code: str = Field(pattern=r'^[A-Z]{3}-\d{3}$', examples=['FST-101'])
    price: Price
    capacity: int = Field(gt=0, le=500)


def main() -> None:
    print(Course(title='FastAPI', code='FST-101', price=4_800_000, capacity=12))

    bad_courses = [
        {'title': 'AI', 'code': 'FST-101', 'price': 1, 'capacity': 1},
        {'title': 'FastAPI', 'code': 'fst101', 'price': 1, 'capacity': 1},
        {'title': 'FastAPI', 'code': 'FST-101', 'price': -5, 'capacity': 0},
    ]
    for data in bad_courses:
        try:
            Course(**data)
        except ValidationError as error:
            print([f'{e["loc"][0]}: {e["msg"]}' for e in error.errors()])


if __name__ == '__main__':
    main()
