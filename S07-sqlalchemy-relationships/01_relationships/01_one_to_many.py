"""One-to-many: an instructor and their courses.

The foreign key column (`Course.instructor_id`) is what the database stores.
The relationship attributes are what Python sees:

    course.instructor           the User object, loaded when you touch it
    teacher.courses_taught      a list of Course objects

You may set either side. `Course(title=..., instructor=ali)` fills in
`instructor_id` for you at flush time, and `ali.courses_taught` already
contains the new course (thanks to `back_populates`).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Course, User, engine, reset_database


def main() -> None:
    reset_database()
    with Session(engine) as session:
        ali = session.scalar(select(User).where(User.full_name == 'Ali Teacher'))
        assert ali is not None
        print(ali, 'teaches', ali.courses_taught)

        course = session.get(Course, 3)
        assert course is not None
        print(course, 'is taught by', course.instructor)

        git_course = Course(title='Git', instructor=ali)
        print('before flush, instructor_id =', git_course.instructor_id)
        print('already in the list?', git_course in ali.courses_taught)
        session.add(git_course)
        session.flush()
        print('after flush, instructor_id  =', git_course.instructor_id)

        # Move a course to another teacher by changing the relationship
        mina = course.instructor
        git_course.instructor = mina
        session.commit()
        print('Mina now teaches', mina.courses_taught)


if __name__ == '__main__':
    main()
