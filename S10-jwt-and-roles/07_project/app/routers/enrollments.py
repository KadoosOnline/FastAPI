from fastapi import APIRouter, status

from app.deps import EnrollmentServiceDep, StudentUser
from app.schemas import EnrollmentRead

router = APIRouter(prefix='/courses/{course_id}/enrollments', tags=['enrollments'])


@router.post('', status_code=status.HTTP_201_CREATED)
def enroll(course_id: int, student: StudentUser, service: EnrollmentServiceDep) -> EnrollmentRead:
    """The logged-in student enrolls THEMSELF: no student_id in the body any more."""
    return EnrollmentRead.model_validate(service.enroll(course_id, student.id))


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
def cancel_my_enrollment(
    course_id: int, student: StudentUser, service: EnrollmentServiceDep
) -> None:
    service.cancel(course_id, student.id)
