from typing import Annotated

from fastapi import APIRouter, Query, status

from app.deps import AdminOnly, EnrollmentServiceDep, UserServiceDep
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


@router.get('', dependencies=[AdminOnly])
def list_users(query: Annotated[UserQuery, Query()], service: UserServiceDep) -> Page[UserRead]:
    # A query model must be the ONLY query parameter of the endpoint:
    # that is why `role` lives inside UserQuery instead of next to it.
    return service.list_users(query)


@router.get('/{user_id}', dependencies=[AdminOnly])
def get_user(user_id: int, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(service.get(user_id))


@router.post('', status_code=status.HTTP_201_CREATED, dependencies=[AdminOnly])
def create_user(data: UserCreate, service: UserServiceDep) -> UserRead:
    """Admins create users with any role. Public sign-up is POST /auth/register."""
    return UserRead.model_validate(service.create(data))


@router.patch('/{user_id}', dependencies=[AdminOnly])
def update_user(user_id: int, data: UserUpdate, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(service.update(user_id, data))


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminOnly])
def delete_user(user_id: int, service: UserServiceDep) -> None:
    service.delete(user_id)


@router.get('/{user_id}/enrollments')
def user_enrollments(user_id: int, service: EnrollmentServiceDep) -> list[EnrollmentWithCourse]:
    return [EnrollmentWithCourse.model_validate(e) for e in service.for_student(user_id)]


@router.post('/{user_id}/enrollments', status_code=status.HTTP_201_CREATED)
def enroll_many(
    user_id: int, data: EnrollMany, service: EnrollmentServiceDep
) -> list[EnrollmentWithCourse]:
    enrollments = service.enroll_many(user_id, data.course_ids)
    return [EnrollmentWithCourse.model_validate(e) for e in enrollments]


@router.get('/{user_id}/courses-taught')
def courses_taught(user_id: int, service: UserServiceDep) -> list[CourseRead]:
    return [CourseRead.model_validate(c) for c in service.courses_taught(user_id)]
