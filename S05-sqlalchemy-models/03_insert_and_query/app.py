"""Insert and read rows with the Session.

    session.add(obj) / session.add_all([...])   stage new objects
    session.commit()                             write them (one transaction)
    session.get(User, 1)                         by primary key, or None
    session.scalars(select(User).where(...))     many objects
    session.scalar(select(...))                  the first value, or None

`select(User)` builds a query object -- nothing runs until the session
executes it. After `commit()`, the new objects have their `id`.
"""

from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int]
    level: Mapped[str] = mapped_column(String(20), default='beginner')

    def __repr__(self) -> str:
        return f'Course({self.id}, {self.title!r}, {self.price:,})'


engine = create_engine('sqlite:///training.db')


def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        python = Course(title='Python Basics', price=2_500_000)
        session.add(python)
        session.add_all(
            [
                Course(title='FastAPI', price=4_800_000, level='advanced'),
                Course(title='HTML and CSS', price=1_900_000),
            ]
        )
        print('before commit, id =', python.id)
        session.commit()
        print('after commit,  id =', python.id)

    with Session(engine) as session:
        print(session.get(Course, 2))
        print(session.get(Course, 99))

        cheap = session.scalars(
            select(Course).where(Course.price < 3_000_000).order_by(Course.price)
        )
        print(cheap.all())

        count = session.scalar(select(func.count()).select_from(Course))
        print('courses:', count)

        titles = session.scalars(select(Course.title).where(Course.level == 'beginner')).all()
        print(titles)


if __name__ == '__main__':
    main()
