"""Build a query step by step from optional filters.

A `select` object can be extended: every `.where()` returns a NEW statement.
So a search function adds only the conditions the user asked for:

    stmt = select(Course)
    if level:
        stmt = stmt.where(Course.level == level)
    if q:
        stmt = stmt.where(Course.title.ilike(f'%{q}%'))

The values are always sent as PARAMETERS, never glued into the SQL text,
so this is safe against SQL injection.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Course, engine, reset_database


def search_courses(
    session: Session,
    *,
    q: str | None = None,
    level: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    only_active: bool = True,
) -> list[Course]:
    stmt = select(Course)
    if q:
        stmt = stmt.where(Course.title.ilike(f'%{q}%'))
    if level:
        stmt = stmt.where(Course.level == level)
    if min_price is not None:
        stmt = stmt.where(Course.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Course.price <= max_price)
    if only_active:
        stmt = stmt.where(Course.is_active)
    return list(session.scalars(stmt.order_by(Course.price)))


def main() -> None:
    reset_database()
    with Session(engine) as session:
        print(search_courses(session))
        print(search_courses(session, q='python'))
        print(search_courses(session, level='beginner', only_active=False))
        print(search_courses(session, min_price=2_000_000, max_price=3_000_000))
        print(search_courses(session, q="x' OR 1=1 --"))  # injection attempt: just no results


if __name__ == '__main__':
    main()
