from typing import Annotated

from fastapi import APIRouter, Query, status

from app.deps import AdminOnly, CourseServiceDep, EnrollmentServiceDep, PagingDep
from app.schemas import (
    CourseCreate,
    CourseDetail,
    CourseRead,
    CourseReplace,
    CourseStudent,
    CourseUpdate,
    Level,
)

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get('')
def list_courses(
    service: CourseServiceDep,
    paging: PagingDep,
    level: Level | None = None,
    q: Annotated[str | None, Query(min_length=2)] = None,
    min_price: Annotated[int | None, Query(ge=0)] = None,
    max_price: Annotated[int | None, Query(ge=0)] = None,
    is_active: bool | None = True,
) -> list[CourseRead]:
    courses = service.list_courses(
        level=level,
        q=q,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        offset=paging.offset,
        limit=paging.limit,
    )
    return [CourseRead.model_validate(course) for course in courses]


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
