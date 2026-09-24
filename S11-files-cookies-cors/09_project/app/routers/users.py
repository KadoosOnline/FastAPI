from typing import Annotated

from fastapi import APIRouter, Query, status

from app.deps import AdminUser, CurrentUser, EnrollmentServiceDep, StudentUser, UserServiceDep
from app.schemas import (
    CourseRead,
    EnrollMany,
    EnrollmentWithCourse,
    Page,
    UserCreate,
    UserQuery,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix='/users', tags=['users'])


# ----- the current user -----
@router.get('/me')
def read_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.get('/me/enrollments')
def my_enrollments(user: CurrentUser, service: EnrollmentServiceDep) -> list[EnrollmentWithCourse]:
    return [EnrollmentWithCourse.model_validate(e) for e in service.for_student(user.id)]


@router.post('/me/enrollments', status_code=status.HTTP_201_CREATED)
def enroll_many(
    data: EnrollMany, student: StudentUser, service: EnrollmentServiceDep
) -> list[EnrollmentWithCourse]:
    """Enroll in several courses at once: all or nothing."""
    enrollments = service.enroll_many(student.id, data.course_ids)
    return [EnrollmentWithCourse.model_validate(e) for e in enrollments]


@router.get('/me/courses-taught')
def my_courses_taught(user: CurrentUser, service: UserServiceDep) -> list[CourseRead]:
    return [CourseRead.model_validate(c) for c in service.courses_taught(user.id)]


# ----- administration -----
@router.get('')
def list_users(
    query: Annotated[UserQuery, Query()], admin: AdminUser, service: UserServiceDep
) -> Page[UserRead]:
    return service.list_users(query)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, admin: AdminUser, service: UserServiceDep) -> UserRead:
    """Admins create users with any role. Public sign-up is POST /auth/register."""
    return UserRead.model_validate(service.create(data))


@router.get('/{user_id}')
def get_user(user_id: int, admin: AdminUser, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(service.get(user_id))


@router.patch('/{user_id}')
def update_user(
    user_id: int, data: UserUpdate, admin: AdminUser, service: UserServiceDep
) -> UserRead:
    return UserRead.model_validate(service.update(user_id, data))


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, admin: AdminUser, service: UserServiceDep) -> None:
    service.delete(user_id)
