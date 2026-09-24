"""A small course API -- the application under test in test_app.py."""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()


class CourseIn(BaseModel):
    title: str = Field(min_length=3)
    price: int = Field(ge=0)


class Course(CourseIn):
    id: int


COURSES: dict[int, Course] = {}


@app.post('/courses', status_code=status.HTTP_201_CREATED)
def create_course(data: CourseIn) -> Course:
    course = Course(id=len(COURSES) + 1, **data.model_dump())
    COURSES[course.id] = course
    return course


@app.get('/courses/{course_id}')
def get_course(course_id: int) -> Course:
    if course_id not in COURSES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Course not found')
    return COURSES[course_id]
