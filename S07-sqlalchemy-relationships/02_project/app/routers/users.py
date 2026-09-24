from fastapi import APIRouter, status

from app.deps import AdminOnly, EnrollmentServiceDep, PagingDep, UserServiceDep
from app.schemas import (
    CourseRead,
    EnrollMany,
    EnrollmentWithCourse,
    Role,
    UserCreate,
    UserRead,
    UserUpdate,
)

router = APIRouter(prefix='/users', tags=['users'])


@router.get('', dependencies=[AdminOnly])
def list_users(
    service: UserServiceDep, paging: PagingDep, role: Role | None = None
) -> list[UserRead]:
    users = service.list_users(role=role, offset=paging.offset, limit=paging.limit)
    return [UserRead.model_validate(user) for user in users]


@router.get('/{user_id}', dependencies=[AdminOnly])
def get_user(user_id: int, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(service.get(user_id))


@router.post('', status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, service: UserServiceDep) -> UserRead:
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
