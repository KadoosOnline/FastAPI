from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from data import USERS, next_id

router = APIRouter(prefix='/users', tags=['users'])


class UserIn(BaseModel):
    email: str
    full_name: str
    role: str = 'student'


@router.get('')
def list_users(role: str | None = None) -> list[dict]:
    users = list(USERS.values())
    return [u for u in users if u['role'] == role] if role else users


@router.get('/{user_id}')
def get_user(user_id: int) -> dict:
    if user_id not in USERS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='User not found')
    return USERS[user_id]


@router.post('', status_code=status.HTTP_201_CREATED)
def create_user(data: UserIn) -> dict:
    email = data.email.lower()
    if any(user['email'] == email for user in USERS.values()):
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Email already registered')
    user_id = next_id(USERS)
    USERS[user_id] = {'id': user_id, **data.model_dump(), 'email': email}
    return USERS[user_id]


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    if user_id not in USERS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='User not found')
    del USERS[user_id]
