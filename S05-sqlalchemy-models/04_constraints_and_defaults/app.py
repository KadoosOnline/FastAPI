"""Constraints and defaults: rules that the DATABASE enforces.

Pydantic checks the request (session 3). The database is the last line of
defence: it protects the data even from our own bugs and from other programs.

    unique=True                  two users can not share an email
    nullable (via `| None`)      NULL allowed or not
    CheckConstraint('price >= 0')
    ForeignKey('users.id')       the instructor must exist
    default=...                  set by Python when inserting
    server_default=func.now()    set by the database itself
    onupdate=...                 set again on every UPDATE

A broken rule raises `IntegrityError`. The session is then unusable until
you call `session.rollback()`.
"""

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, create_engine, event, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)


class Course(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        CheckConstraint('price >= 0', name='price_not_negative'),
        CheckConstraint('capacity > 0', name='capacity_positive'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]
    capacity: Mapped[int]
    instructor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))


engine = create_engine('sqlite:///training.db')


@event.listens_for(engine, 'connect')
def enable_foreign_keys(connection, _record) -> None:  # type: ignore[no-untyped-def]
    """SQLite ignores foreign keys unless you ask. PostgreSQL always checks them."""
    connection.execute('PRAGMA foreign_keys=ON')


def try_to_save(session: Session, obj: object) -> None:
    session.add(obj)
    try:
        session.commit()
        print('saved   ', obj.__class__.__name__)
    except IntegrityError as error:
        session.rollback()  # REQUIRED after a failed commit
        print('REFUSED ', error.orig)


def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        try_to_save(session, User(email='sara@example.com'))
        try_to_save(session, User(email='sara@example.com'))  # unique
        try_to_save(session, Course(title='A', price=-1, capacity=5, instructor_id=1))  # check
        try_to_save(session, Course(title='B', price=1, capacity=5, instructor_id=42))  # FK
        try_to_save(session, Course(title='C', price=1, capacity=5, instructor_id=1))

        user = session.get(User, 1)
        assert user is not None
        print('created_at:', user.created_at, '| active:', user.is_active)


if __name__ == '__main__':
    main()
