"""The same models on PostgreSQL: only the URL changes.

SQLite is perfect for learning. Real servers use PostgreSQL: many users at
the same time, strict types, real concurrency. With SQLAlchemy the code stays
the same -- only the connection string is different:

    postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
                 ^ the driver (psycopg 3)

Install PostgreSQL on Windows 11 or Ubuntu and create the course database
first: see README.md in this folder. Then:

    python app.py

Without PostgreSQL you can still run it on SQLite:

    DATABASE_URL=sqlite:///training.db python app.py        (Linux / macOS)
    set DATABASE_URL=sqlite:///training.db && python app.py (Windows cmd)

Common connection errors and what they mean:
    "connection refused"               the PostgreSQL service is not running
    "password authentication failed"   wrong user / password in the URL
    "database ... does not exist"      setup.sql was not run, or a wrong name
    "No module named psycopg"          pip install -r ../requirements.txt
"""

import os

from sqlalchemy import String, create_engine, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql+psycopg://training:training@localhost:5432/training'
)


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = 'courses_demo'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]


def main() -> None:
    engine = create_engine(DATABASE_URL, echo=False)
    try:
        Base.metadata.create_all(engine)
    except OperationalError as error:
        print('Could not connect:', error.orig)
        return

    with Session(engine) as session:
        session.add(Course(title='FastAPI', price=4_800_000))
        session.commit()
        courses = session.scalars(select(Course)).all()
        print(engine.dialect.name, '->', [(c.id, c.title) for c in courses])


if __name__ == '__main__':
    main()
