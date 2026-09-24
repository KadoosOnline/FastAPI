"""Many-to-many through an association object: students <-> courses.

A student takes many courses; a course has many students. The link table
`enrollments` is a full model (`Enrollment`) because the link has data of
its own: a status and a date.

    enroll:            session.add(Enrollment(student=sara, course=python))
    a student's list:  [e.course for e in sara.enrollments]
    a course's list:   course.students          (viewonly shortcut)
    only active ones:  a select with a join and a where
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Course, Enrollment, User, engine, reset_database


def main() -> None:
    reset_database()
    with Session(engine) as session:
        leila = session.scalar(select(User).where(User.full_name == 'Leila'))
        assert leila is not None
        print('Leila takes:', [e.course.title for e in leila.enrollments])

        fastapi = session.scalar(select(Course).where(Course.title == 'FastAPI'))
        assert fastapi is not None
        print('FastAPI students:', fastapi.students)

        # Cancel one enrollment (data on the link!)
        link = next(e for e in fastapi.enrollments if e.student is leila)
        link.status = 'cancelled'
        session.commit()

        active_students = session.scalars(
            select(User)
            .join(Enrollment, Enrollment.student_id == User.id)
            .where(Enrollment.course_id == fastapi.id, Enrollment.status == 'active')
            .order_by(User.full_name)
        ).all()
        print('active in FastAPI:', active_students)

        # Enroll a new student through the relationship
        omid = User(full_name='Omid')
        omid.enrollments.append(Enrollment(course=fastapi))
        session.add(omid)
        session.commit()
        print('after Omid:', fastapi.students)


if __name__ == '__main__':
    main()
