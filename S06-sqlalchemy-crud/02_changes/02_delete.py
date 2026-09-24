"""DELETE: remove an object, or many rows at once.

    session.delete(course); session.commit()
    session.execute(delete(Course).where(Course.is_active == False))

A missing object must become a clean 404 in the API, never a crash:
check `None` first.

Soft delete: often you do not really delete; you set `is_active = False` so
the history (payments, enrollments) stays correct.
"""

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from models import Course, engine, reset_database


def delete_course(session: Session, course_id: int) -> bool:
    course = session.get(Course, course_id)
    if course is None:
        return False  # the API turns this into 404
    session.delete(course)
    session.commit()
    return True


def main() -> None:
    reset_database()
    with Session(engine) as session:
        print('delete 3 :', delete_course(session, 3))
        print('delete 3 :', delete_course(session, 3))

        result = session.execute(delete(Course).where(Course.is_active.is_(False)))
        session.commit()
        print('bulk deleted:', result.rowcount)

        course = session.get(Course, 1)
        assert course is not None
        course.is_active = False  # soft delete
        session.commit()
        print('left:', session.scalar(select(func.count()).select_from(Course)), 'rows')


if __name__ == '__main__':
    main()
