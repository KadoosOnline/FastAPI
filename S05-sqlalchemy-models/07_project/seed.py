"""Put demo data in the database (safe to run again: it skips existing rows).

python seed.py
"""

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import Course, User

USERS = [
    ('admin@kadoos.ir', 'Site Admin', 'admin'),
    ('teacher@kadoos.ir', 'Ali Teacher', 'instructor'),
    ('teacher2@kadoos.ir', 'Mina Teacher', 'instructor'),
    ('sara@example.com', 'Sara Ahmadi', 'student'),
    ('reza@example.com', 'Reza Karimi', 'student'),
]

COURSES = [
    ('Python Basics', 2_500_000, 20, 'beginner', 'teacher@kadoos.ir'),
    ('Advanced Python', 3_500_000, 15, 'advanced', 'teacher@kadoos.ir'),
    ('FastAPI', 4_800_000, 2, 'advanced', 'teacher@kadoos.ir'),
    ('HTML and CSS', 1_900_000, 25, 'beginner', 'teacher2@kadoos.ir'),
    ('SQL for Developers', 2_900_000, 10, 'intermediate', 'teacher2@kadoos.ir'),
]


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        for email, name, role in USERS:
            if db.scalar(select(User).where(User.email == email)) is None:
                db.add(User(email=email, full_name=name, role=role))
        db.flush()  # send the INSERTs so the users get ids, without committing yet
        for title, price, capacity, level, teacher in COURSES:
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
                    )
                )
        db.commit()
    print('Demo data ready.')


if __name__ == '__main__':
    main()
