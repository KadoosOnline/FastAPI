from fastapi import APIRouter, status

from app.deps import AdminOnly, CourseServiceDep, PagingDep
from app.schemas import CourseCreate, CourseRead, CourseUpdate, Level

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get('')
def list_courses(
    service: CourseServiceDep, paging: PagingDep, level: Level | None = None, q: str | None = None
) -> list[CourseRead]:
    return service.list_courses(level=level, q=q, offset=paging.offset, limit=paging.limit)


@router.get('/{course_id}')
def get_course(course_id: int, service: CourseServiceDep) -> CourseRead:
    return service.get(course_id)


@router.post('', status_code=status.HTTP_201_CREATED, dependencies=[AdminOnly])
def create_course(data: CourseCreate, service: CourseServiceDep) -> CourseRead:
    return service.create(data)


@router.patch('/{course_id}', dependencies=[AdminOnly])
def update_course(course_id: int, data: CourseUpdate, service: CourseServiceDep) -> CourseRead:
    return service.update(course_id, data)


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminOnly])
def delete_course(course_id: int, service: CourseServiceDep) -> None:
    service.delete(course_id)
