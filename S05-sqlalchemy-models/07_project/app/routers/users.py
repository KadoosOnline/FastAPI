from fastapi import APIRouter, status

from app.deps import AdminOnly, PagingDep, UserServiceDep
from app.schemas import UserCreate, UserRead

router = APIRouter(prefix='/users', tags=['users'])


@router.get('', dependencies=[AdminOnly])
def list_users(service: UserServiceDep, paging: PagingDep) -> list[UserRead]:
    return [
        UserRead.model_validate(u)
        for u in service.list_users(offset=paging.offset, limit=paging.limit)
    ]


@router.get('/{user_id}', dependencies=[AdminOnly])
def get_user(user_id: int, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(service.get(user_id))


@router.post('', status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(service.create(data))
