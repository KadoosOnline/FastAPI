"""The models whose history Alembic tracks.

Migration 0001 created the table with id, title and price. Then the `level`
column was added here and migration 0002 was generated from the difference.
"""

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = 'sqlite:///school.db'


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]
    level: Mapped[str] = mapped_column(String(20), server_default='beginner')
