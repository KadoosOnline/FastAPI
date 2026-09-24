from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.deps import AuthServiceDep
from app.schemas import LoginResult, UserRead, UserRegister

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, service: AuthServiceDep) -> UserRead:
    return UserRead.model_validate(service.register(data))


@router.post('/login')
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep
) -> LoginResult:
    """OAuth2 password form: fields `username` (the e-mail) and `password`."""
    user = service.authenticate(form.username, form.password)
    return LoginResult(message='Login successful', user=UserRead.model_validate(user))
