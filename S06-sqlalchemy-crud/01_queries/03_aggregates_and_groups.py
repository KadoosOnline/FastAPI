"""Counting, summing, grouping -- let the DATABASE do the maths.

Never load 10 000 rows into Python just to count them:

    select(func.count()).select_from(Course)
    select(func.avg(Course.price))
    select(Course.level, func.count()).group_by(Course.level)
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Course, User, engine, reset_database


def main() -> None:
    reset_database()
    with Session(engine) as session:
        print('active courses:', session.scalar(select(func.count()).where(Course.is_active)))
        print('average price :', round(session.scalar(select(func.avg(Course.price))) or 0))
        print('cheapest      :', session.scalar(select(func.min(Course.price))))

        per_level = session.execute(
            select(Course.level, func.count().label('n')).group_by(Course.level).order_by('level')
        )
        for level, n in per_level:
            print(f'  {level:<13} {n}')

        per_teacher = session.execute(
            select(User.full_name, func.count(Course.id), func.sum(Course.price))
            .join(Course, Course.instructor_id == User.id)
            .group_by(User.id)
        )
        for name, n, total in per_teacher:
            print(f'  {name:<13} {n} courses, {total:,} IRT')


if __name__ == '__main__':
    main()
