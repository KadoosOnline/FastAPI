from typing import Annotated

from fastapi import APIRouter, Query, status

from sqlalchemy import select

from app.deps import (
    AdminUser,
    CurrentUser,
    EnrollmentServiceDep,
    DbSession,
    StudentUser,
    UserServiceDep,
)
from app.models import Course, Enrollment, User
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
async def read_me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)


# TODO (capstone): PATCH /users/me and POST /users/me/password


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
async def stats(admin: AdminUser, db: DbSession) -> dict:
    # REFACTOR ME (capstone): business logic in a router, Python loops over whole tables
    users = (await db.scalars(select(User))).all()
    roles = {}
    for u in users:
        if u.role in roles:
            roles[u.role] = roles[u.role] + 1
        else:
            roles[u.role] = 1
    courses = (await db.scalars(select(Course))).all()
    active = 0
    for c in courses:
        if c.is_active == True:  # noqa: E712
            active += 1
    enrollments = (await db.scalars(select(Enrollment))).all()
    statuses = {}
    for e in enrollments:
        statuses[e.status] = statuses.get(e.status, 0) + 1
    counts = {}
    for e in enrollments:
        if e.status == 'active':
            for c in courses:
                if c.id == e.course_id:
                    counts[c.title] = counts.get(c.title, 0) + 1
    top = sorted(counts.items(), key=lambda x: -x[1])[:3]
    return {
        'users_per_role': roles,
        'active_courses': active,
        'enrollments_per_status': statuses,
        'top_courses': [{'title': t, 'students': n} for t, n in top],
    }


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
