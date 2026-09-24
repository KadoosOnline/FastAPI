"""One transaction, many rows: enroll a student in several courses at once.

"Take these three courses" must succeed completely or not at all. If the
third course is full, the first two enrollments must not stay behind.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Course, Enrollment, User, engine, reset_database


class CourseFullError(Exception):
    pass


def enroll_in_many(student_id: int, course_ids: list[int]) -> None:
    with Session(engine) as session, session.begin():
        student = session.get(User, student_id)
        assert student is not None
        for course_id in course_ids:
            course = session.get(Course, course_id)
            assert course is not None
            taken = session.scalar(
                select(func.count()).where(
                    Enrollment.course_id == course_id, Enrollment.status == 'active'
                )
            )
            if (taken or 0) >= course.capacity:
                raise CourseFullError(f'{course.title} is full')
            session.add(Enrollment(student=student, course=course))
            session.flush()  # send it now, so the next count sees it


def enrollments_of(student_id: int) -> list[str]:
    with Session(engine) as session:
        student = session.get(User, student_id)
        assert student is not None
        return [e.course.title for e in student.enrollments]


def main() -> None:
    reset_database()
    omid_id = 7
    with Session(engine) as session:
        session.add(User(id=omid_id, full_name='Omid'))
        session.commit()

    try:
        enroll_in_many(omid_id, [3, 4, 2])  # FastAPI (id 2) already has 3 students
    except CourseFullError as error:
        print('refused:', error)
    print('Omid takes:', enrollments_of(omid_id))

    enroll_in_many(omid_id, [3, 4])
    print('Omid takes:', enrollments_of(omid_id))


if __name__ == '__main__':
    main()
