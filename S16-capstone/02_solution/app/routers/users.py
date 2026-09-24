from typing import Annotated

from fastapi import APIRouter, Query, status

from app.deps import AdminUser, CurrentUser, EnrollmentServiceDep, StudentUser, UserServiceDep
from app.schemas import (
    CourseRead,
    EnrollMany,
    EnrollmentWithCourse,
    Page,
    PasswordChange,
    Stats,
    UserCreate,
    UserQuery,
    UserRead,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter(prefix='/users', tags=['users'])


# ----- the current user -----
@router.get('/me')
async def read_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


@router.patch('/me')
async def update_me(data: UserUpdateMe, user: CurrentUser, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(await service.update_me(user, data))


@router.post('/me/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(data: PasswordChange, user: CurrentUser, service: UserServiceDep) -> None:
    await service.change_password(user, data)


@router.get('/me/enrollments')
async def my_enrollments(
    user: CurrentUser, service: EnrollmentServiceDep
) -> list[EnrollmentWithCourse]:
    return [EnrollmentWithCourse.model_validate(e) for e in await service.for_student(user.id)]


@router.post('/me/enrollments', status_code=status.HTTP_201_CREATED)
async def enroll_many(
    data: EnrollMany, student: StudentUser, service: EnrollmentServiceDep
) -> list[EnrollmentWithCourse]:
    """Enroll in several courses at once: all or nothing."""
    enrollments = await service.enroll_many(student.id, data.course_ids)
    return [EnrollmentWithCourse.model_validate(e) for e in enrollments]


@router.get('/me/courses-taught')
async def my_courses_taught(user: CurrentUser, service: UserServiceDep) -> list[CourseRead]:
    return [CourseRead.model_validate(c) for c in await service.courses_taught(user.id)]


# ----- administration -----
@router.get('/stats')
async def stats(admin: AdminUser, service: UserServiceDep) -> Stats:
    """Numbers for the admin dashboard. Declared BEFORE /{user_id} on purpose."""
    return await service.stats()


@router.get('')
async def list_users(
    query: Annotated[UserQuery, Query()], admin: AdminUser, service: UserServiceDep
) -> Page[UserRead]:
    return await service.list_users(query)


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, admin: AdminUser, service: UserServiceDep) -> UserRead:
    """Admins create users with any role. Public sign-up is POST /auth/register."""
    return UserRead.model_validate(await service.create(data))


@router.get('/{user_id}')
async def get_user(user_id: int, admin: AdminUser, service: UserServiceDep) -> UserRead:
    return UserRead.model_validate(await service.get(user_id))


@router.patch('/{user_id}')
async def update_user(
    user_id: int, data: UserUpdate, admin: AdminUser, service: UserServiceDep
) -> UserRead:
    return UserRead.model_validate(await service.update(user_id, data))


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, admin: AdminUser, service: UserServiceDep) -> None:
    await service.delete(user_id)
