"""`scalar`, `scalars`, `execute`: which one do I need?

    session.scalars(select(Course))       many OBJECTS        -> .all(), .first()
    session.scalar(select(Course)...)     ONE value or None   (the first column of the first row)
    session.execute(select(Course.title, Course.price))
                                          ROWS with several columns -> row.title, row.price
    session.get(Course, 3)                by primary key, or None (uses the identity map)

And to be strict about "exactly one":
    .scalar_one()           exactly one row, else an exception
    .scalar_one_or_none()   zero or one row, else an exception
"""

from sqlalchemy import func, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session

from models import Course, engine, reset_database


def main() -> None:
    reset_database()
    with Session(engine) as session:
        courses = session.scalars(select(Course).order_by(Course.id)).all()
        print('scalars   ->', courses[:2], '...')

        count = session.scalar(select(func.count()).select_from(Course))
        print('scalar    ->', count)

        rows = session.execute(select(Course.title, Course.price).where(Course.price > 3_000_000))
        for row in rows:
            print('execute   ->', row.title, row.price)

        print('get       ->', session.get(Course, 3), session.get(Course, 99))

        one = session.execute(select(Course).where(Course.title == 'FastAPI')).scalar_one()
        print('scalar_one->', one)

        for title in ['Nothing', None]:
            stmt = select(Course).where(Course.title == title) if title else select(Course)
            try:
                session.execute(stmt).scalar_one()
            except (NoResultFound, MultipleResultsFound) as error:
                print('error     ->', type(error).__name__)


if __name__ == '__main__':
    main()
