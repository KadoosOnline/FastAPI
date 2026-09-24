"""Roles: a dependency FACTORY that builds "require one of these roles" checks.

    def require_roles(*roles):          # a function that RETURNS a dependency
        def checker(user: CurrentUser):
            if user.role not in roles: raise 403
            return user
        return checker

    AdminUser = Annotated[User, Depends(require_roles('admin'))]

This is the higher-order-function idea of session 1 at work: a closure that
remembers `roles`. Endpoints read like a sentence:

    def delete_course(course_id: int, admin: AdminUser): ...

401 = "I do not know who you are" (no / bad token).
403 = "I know who you are, and you are not allowed".

Log in with admin@kadoos.ir, teacher@kadoos.ir or sara@example.com (all
Password123) through the Authorize button in /docs and try every endpoint.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

SECRET_KEY = 'change-me-this-must-be-a-long-random-secret-0123456789'


class User(BaseModel):
    id: int
    email: str
    role: str


USERS = {
    'admin@kadoos.ir': User(id=1, email='admin@kadoos.ir', role='admin'),
    'teacher@kadoos.ir': User(id=2, email='teacher@kadoos.ir', role='instructor'),
    'sara@example.com': User(id=3, email='sara@example.com', role='student'),
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
app = FastAPI()


@app.post('/auth/token')
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict[str, str]:
    user = USERS.get(form.username)
    if user is None or form.password != 'Password123':  # hashing skipped: see session 9
        raise HTTPException(401, detail='Incorrect email or password')
    claims = {'sub': user.email, 'exp': datetime.now(UTC) + timedelta(minutes=30)}
    return {'access_token': jwt.encode(claims, SECRET_KEY, 'HS256'), 'token_type': 'bearer'}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        email = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])['sub']
    except jwt.InvalidTokenError:
        raise HTTPException(
            401, detail='Invalid token', headers={'WWW-Authenticate': 'Bearer'}
        ) from None
    return USERS[email]


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: str) -> Callable[[User], User]:
    def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail=f'Requires one of the roles: {", ".join(roles)}'
            )
        return user

    return checker


AdminUser = Annotated[User, Depends(require_roles('admin'))]
StaffUser = Annotated[User, Depends(require_roles('admin', 'instructor'))]
StudentUser = Annotated[User, Depends(require_roles('student'))]


@app.get('/users/me')
def me(user: CurrentUser) -> User:
    return user


@app.post('/courses')
def create_course(user: StaffUser) -> dict[str, str]:
    return {'created by': user.email}


@app.delete('/courses/{course_id}')
def delete_course(course_id: int, admin: AdminUser) -> dict[str, str | int]:
    return {'deleted': course_id, 'by': admin.email}


@app.post('/courses/{course_id}/enrollments')
def enroll(course_id: int, student: StudentUser) -> dict[str, str | int]:
    return {'enrolled': student.email, 'course': course_id}


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
