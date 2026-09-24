"""A catalogue of 45 courses for the list-API examples (rebuilt at every start)."""

import random
from collections.abc import Iterator

from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

engine = create_engine('sqlite:///catalogue.db')
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    level: Mapped[str] = mapped_column(String(20))
    price: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))


TOPICS = ['Python', 'FastAPI', 'Django', 'SQL', 'Flask', 'Git', 'Linux', 'React', 'HTML']
LEVELS = ['beginner', 'intermediate', 'advanced']


def rebuild() -> None:
    random.seed(7)  # the same "random" data every time
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        for number in range(1, 46):
            topic = random.choice(TOPICS)
            session.add(
                Course(
                    title=f'{topic} {number:02d}',
                    level=random.choice(LEVELS),
                    price=random.randrange(10, 60) * 100_000,
                    is_active=number % 9 != 0,
                )
            )
        session.add_all(User(full_name=f'Student {n}') for n in range(1, 24))
        session.commit()


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
