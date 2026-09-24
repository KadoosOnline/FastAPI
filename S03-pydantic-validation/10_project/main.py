"""Training Center API — version 2 (session 3 project): validated with Pydantic.

New since session 2:
* schemas.py: CourseCreate / CourseUpdate / CourseRead, UserCreate / UserRead,
  EnrollmentCreate / EnrollmentRead
* every endpoint declares its input AND output types
* rules: title length, price >= 0, capacity 1-500, level is one of three,
  a real e-mail address, PATCH needs at least one field
* a first enrollment endpoint (full course and double enrollment -> 409)

    python main.py      then open http://127.0.0.1:8000/docs
"""

import uvicorn
from fastapi import FastAPI

from routers import courses, enrollments, users

app = FastAPI(title='Training Center API', version='2.0.0')
app.include_router(courses.router)
app.include_router(users.router)
app.include_router(enrollments.router)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
