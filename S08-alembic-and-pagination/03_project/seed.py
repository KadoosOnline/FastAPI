"""Put demo data in the database (safe to run again: it skips existing rows).

The tables are created by Alembic now, not by this script:

    alembic upgrade head
    python seed.py
"""

from datetime import date

from sqlalchemy import inspect, select

from app.database import SessionLocal, engine
from app.models import Course, User

USERS = [
    ('admin@kadoos.ir', 'Site Admin', 'admin'),
    ('teacher@kadoos.ir', 'Ali Teacher', 'instructor'),
    ('teacher2@kadoos.ir', 'Mina Teacher', 'instructor'),
    ('sara@example.com', 'Sara Ahmadi', 'student'),
    ('reza@example.com', 'Reza Karimi', 'student'),
]

COURSES = [
    ('Python Basics', 2_500_000, 20, 'beginner', 'teacher@kadoos.ir', date(2026, 10, 3)),
    ('Advanced Python', 3_500_000, 15, 'advanced', 'teacher@kadoos.ir', date(2026, 11, 1)),
    ('FastAPI', 4_800_000, 2, 'advanced', 'teacher@kadoos.ir', date(2026, 10, 20)),
    ('HTML and CSS', 1_900_000, 25, 'beginner', 'teacher2@kadoos.ir', date(2026, 10, 5)),
    ('SQL for Developers', 2_900_000, 10, 'intermediate', 'teacher2@kadoos.ir', None),
]


def main() -> None:
    if not inspect(engine).has_table('courses'):
        raise SystemExit('No tables yet. Run first:  alembic upgrade head')
    with SessionLocal() as db:
        for email, name, role in USERS:
            if db.scalar(select(User).where(User.email == email)) is None:
                db.add(User(email=email, full_name=name, role=role))
        db.flush()
        for title, price, capacity, level, teacher, start in COURSES:
            if db.scalar(select(Course).where(Course.title == title)) is None:
                instructor = db.scalar(select(User).where(User.email == teacher))
                assert instructor is not None
                db.add(
                    Course(
                        title=title,
                        price=price,
                        capacity=capacity,
                        level=level,
                        instructor_id=instructor.id,
                        start_date=start,
                    )
                )
        db.commit()
    print('Demo data ready.')


if __name__ == '__main__':
    main()
