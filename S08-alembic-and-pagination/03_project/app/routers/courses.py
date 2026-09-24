from typing import Annotated

from fastapi import APIRouter, Query, status

from app.deps import AdminOnly, CourseServiceDep, EnrollmentServiceDep
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
def list_courses(
    query: Annotated[CourseQuery, Query()], service: CourseServiceDep
) -> Page[CourseRead]:
    """Search (q), filters, sorting (sort=-price) and pagination (page, size)."""
    return service.list_courses(query)


@router.get('/{course_id}')
def get_course(course_id: int, service: CourseServiceDep) -> CourseDetail:
    return service.detail(course_id)


@router.get('/{course_id}/students')
def list_students(
    course_id: int, service: EnrollmentServiceDep, status: str | None = None
) -> list[CourseStudent]:
    """Students of a course with their enrollment status: ONE query with a JOIN."""
    return service.students_of(course_id, status)


@router.post('', status_code=status.HTTP_201_CREATED, dependencies=[AdminOnly])
def create_course(data: CourseCreate, service: CourseServiceDep) -> CourseRead:
    return CourseRead.model_validate(service.create(data))


@router.put('/{course_id}', dependencies=[AdminOnly])
def replace_course(course_id: int, data: CourseReplace, service: CourseServiceDep) -> CourseRead:
    return CourseRead.model_validate(service.replace(course_id, data))


@router.patch('/{course_id}', dependencies=[AdminOnly])
def update_course(course_id: int, data: CourseUpdate, service: CourseServiceDep) -> CourseRead:
    return CourseRead.model_validate(service.update(course_id, data))


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminOnly])
def delete_course(course_id: int, service: CourseServiceDep) -> None:
    service.delete(course_id)
