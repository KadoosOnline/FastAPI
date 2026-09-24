"""Cascades: what happens to the children when the parent changes?

`cascade='all, delete-orphan'` on `Course.enrollments` means:
* deleting a course deletes its enrollments too
* removing an enrollment from `course.enrollments` deletes that row
  (it became an "orphan")

Without it, deleting a course that still has enrollments fails on the
foreign key -- which is sometimes exactly what you want (see instructors:
no cascade on `courses_taught`, so a teacher with courses can not vanish).
"""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Course, Enrollment, User, engine, reset_database


def count_enrollments(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Enrollment)) or 0


def main() -> None:
    reset_database()
    with Session(engine) as session:
        print('enrollments:', count_enrollments(session))

        python = session.scalar(select(Course).where(Course.title == 'Python'))
        assert python is not None
        python.enrollments.pop()  # orphan -> deleted
        session.commit()
        print('after removing one from the list:', count_enrollments(session))

        session.delete(python)  # its enrollments go with it
        session.commit()
        print('after deleting the course:', count_enrollments(session))

        ali = session.scalar(select(User).where(User.full_name == 'Ali Teacher'))
        session.delete(ali)
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            # No cascade on courses_taught: SQLAlchemy tries to set instructor_id = NULL,
            # and the NOT NULL column refuses. A teacher with courses can not vanish.
            print('refused:', error.orig)


if __name__ == '__main__':
    main()
