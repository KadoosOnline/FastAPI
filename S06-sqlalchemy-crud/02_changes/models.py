"""Shared models and demo data for the scripts of this folder."""

from sqlalchemy import ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine('sqlite:///changes.db', echo=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), default='student')

    def __repr__(self) -> str:
        return f'User({self.id}, {self.email!r})'


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]
    level: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True)
    instructor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    def __repr__(self) -> str:
        return f'Course({self.id}, {self.title!r}, {self.price:,})'


def reset_database() -> None:
    """Drop everything and insert the same demo data every time."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                User(email='ali@kadoos.ir', full_name='Ali Teacher', role='instructor'),
                User(email='mina@kadoos.ir', full_name='Mina Teacher', role='instructor'),
                User(email='sara@example.com', full_name='Sara Ahmadi'),
            ]
        )
        session.flush()
        session.add_all(
            [
                Course(title='Python Basics', price=2_500_000, level='beginner', instructor_id=1),
                Course(title='Advanced Python', price=3_500_000, level='advanced', instructor_id=1),
                Course(title='FastAPI', price=4_800_000, level='advanced', instructor_id=1),
                Course(title='HTML and CSS', price=1_900_000, level='beginner', instructor_id=2),
                Course(title='SQL', price=2_900_000, level='intermediate', instructor_id=2),
                Course(
                    title='Old PHP',
                    price=900_000,
                    level='beginner',
                    instructor_id=2,
                    is_active=False,
                ),
            ]
        )
        session.commit()
