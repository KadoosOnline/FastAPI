"""Beyond roles: rules that depend on the DATA ("is this course yours?").

A role says what KIND of user you are. But "an instructor may edit THEIR OWN
courses" can not be decided by the role alone -- we must load the course and
compare `course.instructor_id` with `user.id`.

Such checks belong in the service (or a small permissions module), right
after loading the object. Write them as plain functions:

    def can_manage_course(course, user) -> bool: ...

To keep this example short, the "current user" comes from an `X-User-Id`
header instead of a JWT -- the rule itself is what matters here.
"""

from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel


class User(BaseModel):
    id: int
    role: str


class Course(BaseModel):
    id: int
    title: str
    instructor_id: int


USERS = {
    1: User(id=1, role='admin'),
    2: User(id=2, role='instructor'),
    3: User(id=3, role='instructor'),
}
COURSES = {10: Course(id=10, title='FastAPI', instructor_id=2)}


def current_user(x_user_id: Annotated[int, Header()]) -> User:
    return USERS[x_user_id]


def can_manage_course(course: Course, user: User) -> bool:
    return user.role == 'admin' or (user.role == 'instructor' and course.instructor_id == user.id)


app = FastAPI()


@app.patch('/courses/{course_id}')
def rename_course(
    course_id: int, title: str, user: Annotated[User, Depends(current_user)]
) -> Course:
    course = COURSES.get(course_id)
    if course is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Course not found')
    if not can_manage_course(course, user):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail='You can only manage your own courses'
        )
    course.title = title
    return course


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
