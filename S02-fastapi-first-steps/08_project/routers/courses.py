from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from data import COURSES, next_id

router = APIRouter(prefix='/courses', tags=['courses'])


class CourseIn(BaseModel):
    title: str
    price: int
    capacity: int
    level: str = 'beginner'


class CoursePatch(BaseModel):
    title: str | None = None
    price: int | None = None
    capacity: int | None = None
    level: str | None = None


def get_or_404(course_id: int) -> dict:
    if course_id not in COURSES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'Course {course_id} not found')
    return COURSES[course_id]


@router.get('')
def list_courses(
    level: str | None = None,
    max_price: int | None = None,
    q: str | None = None,
) -> list[dict]:
    result = list(COURSES.values())
    if level:
        result = [c for c in result if c['level'] == level]
    if max_price is not None:
        result = [c for c in result if c['price'] <= max_price]
    if q:
        result = [c for c in result if q.lower() in c['title'].lower()]
    return result


@router.get('/{course_id}')
def get_course(course_id: int) -> dict:
    return get_or_404(course_id)


@router.post('', status_code=status.HTTP_201_CREATED)
def create_course(data: CourseIn) -> dict:
    course_id = next_id(COURSES)
    COURSES[course_id] = {'id': course_id, **data.model_dump()}
    return COURSES[course_id]


@router.put('/{course_id}')
def replace_course(course_id: int, data: CourseIn) -> dict:
    get_or_404(course_id)
    COURSES[course_id] = {'id': course_id, **data.model_dump()}
    return COURSES[course_id]


@router.patch('/{course_id}')
def update_course(course_id: int, data: CoursePatch) -> dict:
    course = get_or_404(course_id)
    course.update(data.model_dump(exclude_unset=True))
    return course


@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int) -> None:
    get_or_404(course_id)
    del COURSES[course_id]
