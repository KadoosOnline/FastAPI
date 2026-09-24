"""UPDATE: change the object, then commit.

The ORM way: load the object, change its attributes, `commit()`. The session
tracks what changed ("dirty" objects) and writes only those columns.

    course = session.get(Course, 1)
    course.price = 2_700_000
    session.commit()

For many rows at once, a bulk `update()` statement is faster (one SQL
statement, no objects loaded):

    session.execute(update(Course).where(...).values(price=Course.price * 110 // 100))
"""

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from models import Course, engine, reset_database


def main() -> None:
    reset_database()
    with Session(engine) as session:
        course = session.get(Course, 1)
        assert course is not None
        course.price = 2_700_000
        course.title = 'Python Basics (2026)'
        print('dirty before commit:', session.dirty)
        session.commit()
        print('after commit       :', session.get(Course, 1))

        # "apply these changes" from a dict -- exactly what a PATCH endpoint does
        changes = {'level': 'intermediate', 'price': 3_000_000}
        for field, value in changes.items():
            setattr(course, field, value)
        session.commit()
        print('patched            :', course, course.level)

        result = session.execute(
            update(Course).where(Course.level == 'advanced').values(price=Course.price * 110 // 100)
        )
        session.commit()
        print('bulk updated rows  :', result.rowcount)
        print(session.scalars(select(Course).where(Course.level == 'advanced')).all())


if __name__ == '__main__':
    main()
