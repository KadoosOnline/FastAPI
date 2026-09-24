"""Models: Python classes that describe database tables (SQLAlchemy 2.x style).

    class Base(DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = 'users'
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(255), unique=True)
        bio: Mapped[str | None]

The TYPE HINT is the column definition:
    Mapped[int]          -> INTEGER NOT NULL
    Mapped[str | None]   -> nullable column (NULL allowed)
    Mapped[datetime]     -> DATETIME
`mapped_column(...)` adds the details: length, unique, index, default...

Old tutorials write `email = Column(String, unique=True)`. It still works,
but the editor and mypy do not know that `user.email` is a `str`. With
`Mapped[str]` they do: auto-completion and type checking for free.

`Base.metadata.create_all(engine)` creates every table that does not exist
yet. (From session 8, Alembic does this job properly.)
"""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), default='student')
    bio: Mapped[str | None] = mapped_column(Text)  # nullable, because of `| None`
    created_at: Mapped[datetime] = mapped_column(default=utc_now)


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]  # no mapped_column needed: the hint says everything
    capacity: Mapped[int]
    instructor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))


def main() -> None:
    engine = create_engine('sqlite:///training.db', echo=True)
    Base.metadata.drop_all(engine)  # start from zero every time (demo only!)
    Base.metadata.create_all(engine)  # watch the CREATE TABLE statements

    print(User.__table__.columns.keys())
    print('email nullable?', User.__table__.c.email.nullable)
    print('bio nullable?  ', User.__table__.c.bio.nullable)


if __name__ == '__main__':
    main()
