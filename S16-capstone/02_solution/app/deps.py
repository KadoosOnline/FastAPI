"""Every dependency of the API: database, services, current user and roles."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.exceptions import AuthenticationError, PermissionDeniedError
from app.models import User
from app.security import decode_access_token
from app.services import (
    AuthService,
    CourseService,
    EnrollmentService,
    MaterialService,
    UserService,
)
from app.storage import LocalStorage

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[AsyncSession, Depends(get_db)]

# Reads "Authorization: Bearer <token>" (401 if missing) and adds the
# Authorize button to /docs, which posts the login form to tokenUrl.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(token: TokenDep, db: DbSession, settings: SettingsDep) -> User:
    payload = decode_access_token(token, settings)
    user = await db.get(User, int(payload.sub))
    if user is None:
        raise AuthenticationError('The user of this token no longer exists')
    if not user.is_active:
        raise PermissionDeniedError('This account is disabled')
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: str) -> Callable[[User], Awaitable[User]]:
    """A dependency factory: `Depends(require_roles('admin', 'instructor'))`."""

    async def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise PermissionDeniedError(f'This action requires the role: {" or ".join(roles)}')
        return user

    return checker


AdminUser = Annotated[User, Depends(require_roles('admin'))]
StaffUser = Annotated[User, Depends(require_roles('admin', 'instructor'))]
StudentUser = Annotated[User, Depends(require_roles('student'))]


def get_auth_service(db: DbSession, settings: SettingsDep) -> AuthService:
    return AuthService(db, settings)


def get_course_service(db: DbSession) -> CourseService:
    return CourseService(db)


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


def get_enrollment_service(db: DbSession) -> EnrollmentService:
    return EnrollmentService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CourseServiceDep = Annotated[CourseService, Depends(get_course_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
EnrollmentServiceDep = Annotated[EnrollmentService, Depends(get_enrollment_service)]


def get_material_service(db: DbSession, settings: SettingsDep) -> MaterialService:
    storage = LocalStorage(settings.upload_dir, max_bytes=settings.max_upload_mb * 1024 * 1024)
    return MaterialService(db, storage)


MaterialServiceDep = Annotated[MaterialService, Depends(get_material_service)]
