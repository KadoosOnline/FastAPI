from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.services import CourseService, EnrollmentService, UserService

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[Session, Depends(get_db)]


def get_course_service(db: DbSession) -> CourseService:
    return CourseService(db)


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


def get_enrollment_service(db: DbSession) -> EnrollmentService:
    return EnrollmentService(db)


CourseServiceDep = Annotated[CourseService, Depends(get_course_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
EnrollmentServiceDep = Annotated[EnrollmentService, Depends(get_enrollment_service)]


def require_admin_key(
    settings: SettingsDep, x_api_key: Annotated[str | None, Header()] = None
) -> None:
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Invalid or missing X-API-Key')


AdminOnly = Depends(require_admin_key)
