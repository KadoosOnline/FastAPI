"""Every dependency of the API, as ready-to-use `Annotated` types."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings
from app.services import CourseService, EnrollmentService, UserService
from app.store import Store, get_store

SettingsDep = Annotated[Settings, Depends(get_settings)]
StoreDep = Annotated[Store, Depends(get_store)]


@dataclass
class Paging:
    offset: int
    limit: int


def get_paging(settings: SettingsDep, page: int = 1, size: int = 10) -> Paging:
    size = max(1, min(size, settings.max_page_size))
    return Paging(offset=(max(page, 1) - 1) * size, limit=size)


PagingDep = Annotated[Paging, Depends(get_paging)]


def get_course_service(store: StoreDep) -> CourseService:
    return CourseService(store)


def get_user_service(store: StoreDep) -> UserService:
    return UserService(store)


CourseServiceDep = Annotated[CourseService, Depends(get_course_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_enrollment_service(
    store: StoreDep, courses: CourseServiceDep, users: UserServiceDep
) -> EnrollmentService:
    return EnrollmentService(store, courses, users)


EnrollmentServiceDep = Annotated[EnrollmentService, Depends(get_enrollment_service)]


def require_admin_key(
    settings: SettingsDep, x_api_key: Annotated[str | None, Header()] = None
) -> None:
    """Temporary "authentication": sessions 9-10 replace it with real users + JWT."""
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Invalid or missing X-API-Key')


AdminOnly = Depends(require_admin_key)
