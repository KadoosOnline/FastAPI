"""Registration: validate the password, store only its hash, never send it back.

Three schemas again (session 3), now with a security reason:
* UserCreate  has `password` (plain text, only in memory, only on the way IN)
* the stored user has `hashed_password`
* UserRead    has NEITHER -- a response model is our guarantee

Also: a public registration endpoint must not accept `role`. Otherwise
anybody registers as admin. Pydantic ignores unknown fields, so a client
that sends "role": "admin" still becomes a student.
"""

from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pwdlib import PasswordHash
from pydantic import AfterValidator, BaseModel, EmailStr, Field

password_hash = PasswordHash.recommended()


def strong_password(value: str) -> str:
    if value.isdigit() or value.isalpha():
        raise ValueError('use letters AND digits')
    if value.lower() in {'password1', 'password123', 'qwerty123'}:
        raise ValueError('this password is too common')
    return value


Password = Annotated[str, Field(min_length=8, max_length=128), AfterValidator(strong_password)]


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2)
    password: Password


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str


USERS: dict[str, dict] = {}  # email -> stored user
app = FastAPI()


@app.post('/auth/register', status_code=status.HTTP_201_CREATED)
def register(data: UserCreate) -> UserRead:
    email = data.email.lower()
    if email in USERS:
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Email already registered')
    user = {
        'id': len(USERS) + 1,
        'email': email,
        'full_name': data.full_name,
        'role': 'student',  # ALWAYS student here
        'hashed_password': password_hash.hash(data.password),
    }
    USERS[email] = user
    return UserRead(**user)


@app.get('/debug/stored-users')
def stored_users() -> list[dict]:
    """Only to SEE what is stored in class. Never ship an endpoint like this!"""
    return list(USERS.values())


if __name__ == '__main__':
    uvicorn.run('app:app', reload=True)
