from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='/courses', tags=['courses'])

COURSES = {1: {'id': 1, 'title': 'FastAPI'}, 2: {'id': 2, 'title': 'Python'}}


@router.get('')  # the full path is /courses
def list_courses() -> list[dict]:
    return list(COURSES.values())


@router.get('/{course_id}')  # the full path is /courses/{course_id}
def get_course(course_id: int) -> dict:
    if course_id not in COURSES:
        raise HTTPException(404, detail='Course not found')
    return COURSES[course_id]
