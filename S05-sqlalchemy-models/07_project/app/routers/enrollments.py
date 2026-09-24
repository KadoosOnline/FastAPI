from fastapi import APIRouter, status

from app.deps import EnrollmentServiceDep
from app.schemas import EnrollmentCreate, EnrollmentRead

router = APIRouter(prefix='/courses/{course_id}/enrollments', tags=['enrollments'])


@router.post('', status_code=status.HTTP_201_CREATED)
def enroll(course_id: int, data: EnrollmentCreate, service: EnrollmentServiceDep) -> EnrollmentRead:
    return EnrollmentRead.model_validate(service.enroll(course_id, data.student_id))


@router.get('')
def list_enrollments(course_id: int, service: EnrollmentServiceDep) -> list[EnrollmentRead]:
    return [EnrollmentRead.model_validate(e) for e in service.for_course(course_id)]
