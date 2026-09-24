"""Business rules, now on top of a database Session instead of dictionaries.

Compare with session 4: the methods, their arguments and their exceptions
are the same. Only the insides changed -- the routers did not notice.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Course, Enrollment, User
from app.schemas import CourseCreate, Level, UserCreate


class CourseService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_courses(
        self, *, level: Level | None, q: str | None, offset: int, limit: int
    ) -> list[Course]:
        stmt = select(Course).order_by(Course.id)
        if level:
            stmt = stmt.where(Course.level == level)
        if q:
            stmt = stmt.where(Course.title.ilike(f'%{q}%'))
        return list(self.db.scalars(stmt.offset(offset).limit(limit)))

    def get(self, course_id: int) -> Course:
        course = self.db.get(Course, course_id)
        if course is None:
            raise NotFoundError(f'Course {course_id} not found')
        return course

    def create(self, data: CourseCreate) -> Course:
        instructor = self.db.get(User, data.instructor_id)
        if instructor is None or instructor.role != 'instructor':
            raise BusinessRuleError('instructor_id must be an instructor')
        course = Course(**data.model_dump())
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self, *, offset: int, limit: int) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id).offset(offset).limit(limit)))

    def get(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            raise NotFoundError(f'User {user_id} not found')
        return user

    def create(self, data: UserCreate) -> User:
        email = data.email.lower()
        if self.db.scalar(select(User).where(User.email == email)):
            raise ConflictError('Email already registered')
        user = User(email=email, full_name=data.full_name, role=data.role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class EnrollmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def active_count(self, course_id: int) -> int:
        stmt = select(func.count()).where(
            Enrollment.course_id == course_id, Enrollment.status == 'active'
        )
        return self.db.scalar(stmt) or 0

    def enroll(self, course_id: int, student_id: int) -> Enrollment:
        course = CourseService(self.db).get(course_id)
        student = UserService(self.db).get(student_id)
        if student.role != 'student':
            raise BusinessRuleError('Only students can enroll')
        existing = self.db.scalar(
            select(Enrollment).where(
                Enrollment.course_id == course_id, Enrollment.student_id == student_id
            )
        )
        if existing is not None:
            raise ConflictError('Already enrolled')
        if self.active_count(course_id) >= course.capacity:
            raise ConflictError('Course is full')
        enrollment = Enrollment(course_id=course_id, student_id=student_id)
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def for_course(self, course_id: int) -> list[Enrollment]:
        CourseService(self.db).get(course_id)
        stmt = select(Enrollment).where(Enrollment.course_id == course_id).order_by(Enrollment.id)
        return list(self.db.scalars(stmt))
