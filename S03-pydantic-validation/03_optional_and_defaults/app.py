"""Required, optional, default: three different things.

    title: str                   REQUIRED: must be in the data
    level: str = 'beginner'      has a DEFAULT: may be left out
    description: str | None = None
                                 OPTIONAL: may be left out, or be null

A trap: `str | None` WITHOUT a default is still required -- the client must
send the key, even if the value is null.

`model_fields_set` tells which fields the client really sent. This is how a
PATCH knows the difference between "not sent" and "sent as null".
"""

from pydantic import BaseModel, ValidationError


class CourseForm(BaseModel):
    title: str
    level: str = 'beginner'
    description: str | None = None
    teacher_note: str | None  # required, but may be null!


def main() -> None:
    form = CourseForm(title='FastAPI', teacher_note=None)
    print(form)
    print('sent by the client:', form.model_fields_set)

    try:
        CourseForm(title='FastAPI')
    except ValidationError as error:
        print(error.errors()[0]['loc'], error.errors()[0]['msg'])

    patch = CourseForm(title='FastAPI', teacher_note=None, description=None)
    print(patch.model_dump(exclude_unset=True))  # only what was sent


if __name__ == '__main__':
    main()
