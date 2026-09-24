"""Put demo data in the database (safe to run again: it skips existing rows).

alembic upgrade head
python seed.py
"""

import asyncio
from datetime import date

from sqlalchemy import inspect, select

from app.database import SessionLocal, engine
from app.models import Course, User
from app.security import hash_password

DEMO_PASSWORD = 'Password123'  # the same for every demo account

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


async def main() -> None:
    async with engine.connect() as connection:
        has_tables = await connection.run_sync(lambda sync: inspect(sync).has_table('courses'))
    if not has_tables:
        raise SystemExit('No tables yet. Run first:  alembic upgrade head')

    async with SessionLocal() as db:
        for email, name, role in USERS:
            if await db.scalar(select(User).where(User.email == email)) is None:
                db.add(
                    User(
                        email=email,
                        full_name=name,
                        role=role,
                        hashed_password=hash_password(DEMO_PASSWORD),
                    )
                )
        await db.flush()
        for title, price, capacity, level, teacher, start in COURSES:
            if await db.scalar(select(Course).where(Course.title == title)) is None:
                instructor = await db.scalar(select(User).where(User.email == teacher))
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
        await db.commit()
    await engine.dispose()
    print(f'Demo data ready. Every demo password is {DEMO_PASSWORD}')


if __name__ == '__main__':
    asyncio.run(main())
