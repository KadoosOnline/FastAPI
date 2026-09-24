"""Pydantic `BaseModel`: a dataclass that checks and converts its data.

In session 1 our dataclasses trusted whatever they got. Data from the
internet can not be trusted. A Pydantic model:
* converts when it is safe:   "42" -> 42,  "true" -> True
* refuses when it is not:     "abc" for an int -> ValidationError
* reports EVERY problem at once, with the field name (`loc`)

This is what FastAPI uses for request bodies. When validation fails inside
FastAPI, you get the same list of errors as a 422 response.

    python app.py      (no server: just watch Pydantic work)
"""

from pydantic import BaseModel, ValidationError


class Course(BaseModel):
    id: int
    title: str
    price: int
    is_active: bool = True


def main() -> None:
    course = Course(id='7', title='FastAPI', price=4_800_000, is_active='yes')
    print(course)  # '7' became 7, 'yes' became True
    print(course.id + 1)

    data_from_json = {'id': 8, 'title': 'SQL', 'price': 2_900_000}
    print(Course.model_validate(data_from_json))
    print(Course.model_validate_json('{"id": 9, "title": "Docker", "price": 3000000}'))

    try:
        Course(id='abc', title=None, price=1.5)
    except ValidationError as error:
        print(f'{error.error_count()} errors:')
        for item in error.errors():
            print('  ', item['loc'], '->', item['msg'])


if __name__ == '__main__':
    main()
