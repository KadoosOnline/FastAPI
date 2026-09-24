"""Engine, session factory, the declarative Base, and the `get_db` dependency."""

from collections.abc import Iterator
from datetime import datetime

from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=settings.database_echo)
SessionLocal = sessionmaker(engine)

if engine.dialect.name == 'sqlite':

    @event.listens_for(engine, 'connect')
    def enable_sqlite_foreign_keys(connection, _record) -> None:  # type: ignore[no-untyped-def]
        connection.execute('PRAGMA foreign_keys=ON')


class Base(DeclarativeBase):
    # Every Mapped[datetime] column keeps the time zone (TIMESTAMP WITH TIME ZONE).
    # Without it PostgreSQL stores "naive" times and asyncpg refuses aware ones.
    type_annotation_map = {datetime: DateTime(timezone=True)}


def get_db() -> Iterator[Session]:
    """One session per request; closed (and rolled back if needed) afterwards."""
    with SessionLocal() as session:
        yield session
