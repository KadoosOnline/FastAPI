from typing import Annotated

from fastapi import APIRouter, Query, status

from app.deps import AdminUser, CourseServiceDep, EnrollmentServiceDep, StaffUser
from app.schemas import (
    CourseCreate,
    CourseDetail,
    CourseQuery,
    CourseRead,
    CourseReplace,
    CourseStudent,
    CourseUpdate,
    Page,
)

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get('')
async def list_courses(
    query: Annotated[CourseQuery, Query()], service: CourseServiceDep
) -> Page[CourseRead]:
    """Public: anybody can browse the catalogue."""
    return await service.list_courses(query)


@router.get('/{course_id}')
async def get_course(course_id: int, service: CourseServiceDep) -> CourseDetail:
    return await service.detail(course_id)


@router.get('/{course_id}/students')
async def list_students(
    course_id: int, actor: StaffUser, service: EnrollmentServiceDep, status: str | None = None
) -> list[CourseStudent]:
    """Admins, or the instructor of this course."""
    return await service.students_of(course_id, actor, status)


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate, actor: StaffUser, service: CourseServiceDep
) -> CourseRead:
    """Instructors create their own courses; admins choose the instructor."""
    return CourseRead.model_validate(await service.create(data, actor))


@router.put('/{course_id}')
async def replace_course(
    course_id: int, data: CourseReplace, actor: StaffUser, service: CourseServiceDep
) -> CourseRead:
    return CourseRead.model_validate(await service.replace(course_id, data, actor))


@router.patch('/{course_id}')
async def update_course(
    course_id: int, data: CourseUpdate, actor: StaffUser, service: CourseServiceDep
) -> CourseRead:
    return CourseRead.model_validate(await service.update(course_id, data, actor))


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, admin: AdminUser, service: CourseServiceDep) -> None:
    """Only admins delete courses."""
    await service.delete(course_id)
