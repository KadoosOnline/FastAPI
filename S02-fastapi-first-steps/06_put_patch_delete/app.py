"""All five methods on one resource: a complete CRUD.

    GET    /courses          list          200
    POST   /courses          create        201
    GET    /courses/{id}     read one      200 / 404
    PUT    /courses/{id}     REPLACE all   200 / 404
    PATCH  /courses/{id}     change PART   200 / 404
    DELETE /courses/{id}     remove        204 / 404

PUT vs PATCH:
* PUT sends the whole new course. A missing field is an error (422).
* PATCH sends only what changes: {"price": 100}. Every field is optional,
  and `model_dump(exclude_unset=True)` gives us only the fields the client sent.

The helper `get_or_404` avoids writing the same "not found" check five times.
"""

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class CourseIn(BaseModel):
    title: str
    price: int
    capacity: int


class CoursePatch(BaseModel):
    title: str | None = None
    price: int | None = None
    capacity: int | None = None


COURSES: dict[int, dict] = {1: {'id': 1, 'title': 'FastAPI', 'price': 4_800_000, 'capacity': 12}}


def get_or_404(course_id: int) -> dict:
    if course_id not in COURSES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Course not found')
    return COURSES[course_id]


@app.get('/courses')
def list_courses() -> list[dict]:
    return list(COURSES.values())


@app.post('/courses', status_code=status.HTTP_201_CREATED)
def create_course(data: CourseIn) -> dict:
    new_id = max(COURSES, default=0) + 1
    COURSES[new_id] = {'id': new_id, **data.model_dump()}
    return COURSES[new_id]


@app.get('/courses/{course_id}')
def get_course(course_id: int) -> dict:
    return get_or_404(course_id)


@app.put('/courses/{course_id}')
def replace_course(course_id: int, data: CourseIn) -> dict:
    get_or_404(course_id)
    COURSES[course_id] = {'id': course_id, **data.model_dump()}
    return COURSES[course_id]


@app.patch('/courses/{course_id}')
def update_course(course_id: int, data: CoursePatch) -> dict:
    course = get_or_404(course_id)
    course.update(data.model_dump(exclude_unset=True))
    return course


@app.delete('/courses/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int) -> None:
    get_or_404(course_id)
    del COURSES[course_id]


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
