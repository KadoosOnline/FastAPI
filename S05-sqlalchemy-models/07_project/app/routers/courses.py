from fastapi import APIRouter, status

from app.deps import AdminOnly, CourseServiceDep, PagingDep
from app.schemas import CourseCreate, CourseRead, Level

router = APIRouter(prefix='/courses', tags=['courses'])


@router.get('')
def list_courses(
    service: CourseServiceDep, paging: PagingDep, level: Level | None = None, q: str | None = None
) -> list[CourseRead]:
    courses = service.list_courses(level=level, q=q, offset=paging.offset, limit=paging.limit)
    return [CourseRead.model_validate(course) for course in courses]


@router.get('/{course_id}')
def get_course(course_id: int, service: CourseServiceDep) -> CourseRead:
    return CourseRead.model_validate(service.get(course_id))


@router.post('', status_code=status.HTTP_201_CREATED, dependencies=[AdminOnly])
def create_course(data: CourseCreate, service: CourseServiceDep) -> CourseRead:
    return CourseRead.model_validate(service.create(data))
