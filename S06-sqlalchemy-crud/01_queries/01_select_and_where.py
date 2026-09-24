"""`select()` + `where()`: build a query, then run it.

    stmt = select(Course).where(Course.price < 3_000_000).order_by(Course.price)
    courses = session.scalars(stmt).all()

`Course.price < 3_000_000` does NOT compare numbers: it builds a piece of SQL
(`courses.price < :price_1`). Print the statement to see it.

Several conditions:
    .where(a, b)            a AND b
    .where(or_(a, b))       a OR b
    .where(Course.level.in_(['beginner', 'intermediate']))
    .where(Course.title.ilike('%python%'))       case-insensitive LIKE
"""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from models import Course, engine, reset_database


def main() -> None:
    reset_database()
    with Session(engine) as session:
        stmt = select(Course).where(Course.price < 3_000_000).order_by(Course.price)
        print(stmt)  # the SQL, with placeholders
        print(session.scalars(stmt).all())

        both = select(Course).where(Course.level == 'advanced', Course.instructor_id == 1)
        print(session.scalars(both).all())

        either = select(Course).where(or_(Course.level == 'beginner', Course.price > 4_000_000))
        print(session.scalars(either).all())

        in_list = select(Course.title).where(Course.level.in_(['beginner', 'intermediate']))
        print(session.scalars(in_list).all())

        like = select(Course).where(Course.title.ilike('%python%'), Course.is_active)
        print(session.scalars(like).all())


if __name__ == '__main__':
    main()
