from fastapi import APIRouter

router = APIRouter(prefix='/users', tags=['users'])

USERS = [{'id': 1, 'email': 'sara@example.com'}]


@router.get('')
def list_users() -> list[dict]:
    return USERS
