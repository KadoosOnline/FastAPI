from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.deps import AuthServiceDep
from app.schemas import Token, UserRead, UserRegister

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, service: AuthServiceDep) -> UserRead:
    return UserRead.model_validate(service.register(data))


@router.post('/token')
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep) -> Token:
    """OAuth2 password flow: form fields `username` (the e-mail) and `password`.

    Send the returned token as `Authorization: Bearer <access_token>`.
    """
    return service.login(form.username, form.password)
