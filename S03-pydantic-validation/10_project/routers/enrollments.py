from fastapi import APIRouter, HTTPException, status

from data import ENROLLMENTS, USERS, next_id, now
from routers.courses import get_course_or_404
from schemas import EnrollmentCreate, EnrollmentRead

router = APIRouter(prefix='/courses/{course_id}/enrollments', tags=['enrollments'])


@router.post('', status_code=status.HTTP_201_CREATED)
def enroll(course_id: int, data: EnrollmentCreate) -> EnrollmentRead:
    course = get_course_or_404(course_id)
    student = USERS.get(data.student_id)
    if student is None or student.role != 'student':
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='student_id is not a student')
    active = [e for e in ENROLLMENTS.values() if e.course_id == course_id and e.status == 'active']
    if any(e.student_id == student.id for e in active):
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Already enrolled')
    if len(active) >= course.capacity:
        raise HTTPException(status.HTTP_409_CONFLICT, detail='Course is full')
    enrollment = EnrollmentRead(
        id=next_id(ENROLLMENTS), student_id=student.id, course_id=course_id, created_at=now()
    )
    ENROLLMENTS[enrollment.id] = enrollment
    return enrollment


@router.get('')
def list_enrollments(course_id: int) -> list[EnrollmentRead]:
    get_course_or_404(course_id)
    return [e for e in ENROLLMENTS.values() if e.course_id == course_id]
