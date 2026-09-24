"""Request body: sending data TO the server (POST).

The client sends JSON in the body:

    POST /courses
    {"title": "Git", "price": 3000000, "capacity": 20}

We describe the expected shape with a small Pydantic model (the whole of
session 3 is about Pydantic; here we only need the basics). A parameter
whose type is a `BaseModel` is read from the body.

FastAPI then:
* parses the JSON,
* checks every field and its type (missing field or "abc" as price -> 422),
* gives us a real object: `course.title`, `course.price`.
"""

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class NewCourse(BaseModel):
    title: str
    price: int
    capacity: int = 20  # optional in the JSON, with a default


COURSES: list[dict] = []


@app.post('/courses')
def create_course(course: NewCourse) -> dict:
    new = {'id': len(COURSES) + 1, **course.model_dump()}
    COURSES.append(new)
    return new


@app.get('/courses')
def list_courses() -> list[dict]:
    return COURSES


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
