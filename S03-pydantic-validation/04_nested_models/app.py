"""Nested models: a model inside a model, a list of models.

JSON is a tree. Pydantic models can be too:

    {
      "title": "FastAPI",
      "instructor": {"id": 1, "full_name": "Ali"},
      "sessions": [{"number": 1, "topic": "Intro"}, ...]
    }

Every level is validated, and the error `loc` shows the full path:
('sessions', 1, 'number').
"""

from pydantic import BaseModel, Field, ValidationError


class Instructor(BaseModel):
    id: int
    full_name: str


class ClassSession(BaseModel):
    number: int = Field(ge=1, le=16)
    topic: str


class Course(BaseModel):
    title: str
    instructor: Instructor
    tags: list[str] = []
    sessions: list[ClassSession] = []


def main() -> None:
    course = Course.model_validate(
        {
            'title': 'FastAPI',
            'instructor': {'id': 1, 'full_name': 'Ali Teacher'},
            'tags': ['web', 'api'],
            'sessions': [{'number': 1, 'topic': 'Refresh'}, {'number': 2, 'topic': 'Routes'}],
        }
    )
    print(course.instructor.full_name, [s.topic for s in course.sessions])

    try:
        Course.model_validate(
            {
                'title': 'X',
                'instructor': {'id': 1},
                'sessions': [{'number': 1, 'topic': 'a'}, {'number': 99, 'topic': 'b'}],
            }
        )
    except ValidationError as error:
        for item in error.errors():
            print(item['loc'], item['msg'])


if __name__ == '__main__':
    main()
