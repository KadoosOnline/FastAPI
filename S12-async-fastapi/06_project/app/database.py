"""Async engine, async session factory, the declarative Base and `get_db`."""

from collections.abc import AsyncIterator
from datetime import datetime

from sqlalchemy import DateTime, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()
# The URL names an ASYNC driver: sqlite+aiosqlite:// or postgresql+asyncpg://
engine = create_async_engine(settings.database_url, echo=settings.database_echo)
# expire_on_commit=False: objects stay readable after commit (no lazy reload in async)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

if engine.dialect.name == 'sqlite':

    @event.listens_for(engine.sync_engine, 'connect')
    def enable_sqlite_foreign_keys(connection, _record) -> None:  # type: ignore[no-untyped-def]
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


class Base(DeclarativeBase):
    # Every Mapped[datetime] column keeps the time zone (TIMESTAMP WITH TIME ZONE).
    # Without it PostgreSQL stores "naive" times and asyncpg refuses aware ones.
    type_annotation_map = {datetime: DateTime(timezone=True)}


async def get_db() -> AsyncIterator[AsyncSession]:
    """One AsyncSession per request, closed afterwards."""
    async with SessionLocal() as session:
        yield session
