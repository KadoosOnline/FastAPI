"""Async SQLAlchemy: the same ORM, awaited.

    engine = create_async_engine('sqlite+aiosqlite:///async.db')   # an async DRIVER
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as session:
        session.add(obj)                           # add is NOT awaited (no I/O)
        await session.commit()                     # I/O -> await
        course = await session.get(Course, 1)
        result = await session.scalars(select(Course))

Drivers: aiosqlite for SQLite, asyncpg for PostgreSQL
    postgresql+asyncpg://user:pass@localhost/db

Two rules that surprise everybody:
1. NO lazy loading. `course.instructor` without eager loading raises
   `MissingGreenlet` (there is no `await` in an attribute access). Load
   relationships in the query: `selectinload(...)` / `joinedload(...)`.
2. `expire_on_commit=False`, otherwise reading an attribute after commit
   would need a (forbidden) lazy reload.
"""

import asyncio

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

engine = create_async_engine('sqlite+aiosqlite:///async.db')
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    courses: Mapped[list['Course']] = relationship(back_populates='instructor')


class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    instructor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    instructor: Mapped[User] = relationship(back_populates='courses')


async def main() -> None:
    async with engine.begin() as connection:
        # create_all is a sync function: run it inside the async connection
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        ali = User(full_name='Ali Teacher')
        session.add_all(
            [Course(title='Python', instructor=ali), Course(title='FastAPI', instructor=ali)]
        )
        await session.commit()
        print('after commit, still readable:', ali.full_name)

    async with SessionLocal() as session:
        courses = (await session.scalars(select(Course))).all()
        try:
            print(courses[0].instructor.full_name)
        except MissingGreenlet:
            print('lazy loading in async -> MissingGreenlet!')

    async with SessionLocal() as session:
        stmt = select(Course).options(selectinload(Course.instructor)).order_by(Course.id)
        for course in await session.scalars(stmt):
            print(f'{course.title} by {course.instructor.full_name}')

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
