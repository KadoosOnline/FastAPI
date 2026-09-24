"""Models WITH relationships, shared by the scripts of this folder.

    User 1 ──< Course            one instructor teaches many courses
    User 1 ──< Enrollment >── 1 Course
                                 many-to-many between students and courses,
                                 through an "association object" that has its
                                 own data (status, created_at)

`relationship()` adds Python attributes that follow the foreign keys:

    course.instructor        -> User
    user.courses_taught      -> list[Course]
    user.enrollments         -> list[Enrollment]
    enrollment.course        -> Course
    course.students          -> list[User]   (read-only shortcut)

`back_populates` connects the two sides: set one, the other follows.
"""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

engine = create_engine('sqlite:///relations.db')


@event.listens_for(engine, 'connect')
def enable_foreign_keys(connection, _record) -> None:  # type: ignore[no-untyped-def]
    connection.execute('PRAGMA foreign_keys=ON')


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), default='student')

    courses_taught: Mapped[list['Course']] = relationship(back_populates='instructor')
    enrollments: Mapped[list['Enrollment']] = relationship(
        back_populates='student', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'User({self.full_name!r})'


class Course(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    capacity: Mapped[int] = mapped_column(default=20)
    instructor_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    instructor: Mapped['User'] = relationship(back_populates='courses_taught')
    enrollments: Mapped[list['Enrollment']] = relationship(
        back_populates='course', cascade='all, delete-orphan'
    )
    # A read-only shortcut THROUGH the enrollments table:
    students: Mapped[list['User']] = relationship(secondary='enrollments', viewonly=True)

    def __repr__(self) -> str:
        return f'Course({self.title!r})'


class Enrollment(Base):
    __tablename__ = 'enrollments'
    __table_args__ = (UniqueConstraint('student_id', 'course_id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id', ondelete='CASCADE'))
    status: Mapped[str] = mapped_column(String(20), default='active')
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    student: Mapped['User'] = relationship(back_populates='enrollments')
    course: Mapped['Course'] = relationship(back_populates='enrollments')

    def __repr__(self) -> str:
        return f'Enrollment({self.student.full_name} -> {self.course.title}, {self.status})'


def reset_database() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        ali = User(full_name='Ali Teacher', role='instructor')
        mina = User(full_name='Mina Teacher', role='instructor')
        students = [User(full_name=name) for name in ['Sara', 'Reza', 'Nima', 'Leila']]
        courses = [
            Course(title='Python', instructor=ali),
            Course(title='FastAPI', instructor=ali, capacity=3),
            Course(title='HTML', instructor=mina),
            Course(title='SQL', instructor=mina),
        ]
        session.add_all([ali, mina, *students, *courses])
        for index, student in enumerate(students):
            for course in courses[: index + 1]:
                session.add(Enrollment(student=student, course=course))
        session.commit()
