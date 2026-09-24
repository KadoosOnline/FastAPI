from fastapi import APIRouter, HTTPException, status

from data import COURSES, USERS, next_id, now
from schemas import CourseCreate, CourseRead, CourseUpdate, Level

router = APIRouter(prefix='/courses', tags=['courses'])


def get_course_or_404(course_id: int) -> CourseRead:
    if course_id not in COURSES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'Course {course_id} not found')
    return COURSES[course_id]


@router.get('')
def list_courses(
    level: Level | None = None, max_price: int | None = None, q: str | None = None
) -> list[CourseRead]:
    result = list(COURSES.values())
    if level:
        result = [c for c in result if c.level == level]
    if max_price is not None:
        result = [c for c in result if c.price <= max_price]
    if q:
        result = [c for c in result if q.lower() in c.title.lower()]
    return result


@router.get('/{course_id}')
def get_course(course_id: int) -> CourseRead:
    return get_course_or_404(course_id)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_course(data: CourseCreate) -> CourseRead:
    instructor = USERS.get(data.instructor_id)
    if instructor is None or instructor.role != 'instructor':
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail='instructor_id is not an instructor'
        )
    course = CourseRead(id=next_id(COURSES), created_at=now(), **data.model_dump())
    COURSES[course.id] = course
    return course


@router.patch('/{course_id}')
def update_course(course_id: int, data: CourseUpdate) -> CourseRead:
    course = get_course_or_404(course_id)
    updated = course.model_copy(update=data.model_dump(exclude_unset=True))
    COURSES[course_id] = updated
    return updated


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int) -> None:
    get_course_or_404(course_id)
    del COURSES[course_id]
