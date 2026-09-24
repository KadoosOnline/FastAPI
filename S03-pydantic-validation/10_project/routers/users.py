from fastapi import APIRouter, HTTPException, status

from data import USERS, next_id, now
from schemas import UserCreate, UserRead

router = APIRouter(prefix='/users', tags=['users'])


@router.get('')
def list_users() -> list[UserRead]:
    return list(USERS.values())


@router.get('/{user_id}')
def get_user(user_id: int) -> UserRead:
    if user_id not in USERS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='User not found')
    return USERS[user_id]


@router.post('', status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate) -> UserRead:
    email = data.email.lower()
    if any(user.email == email for user in USERS.values()):
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Email already registered')
    user = UserRead(id=next_id(USERS), created_at=now(), **data.model_dump() | {'email': email})
    USERS[user.id] = user
    return user
