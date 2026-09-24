"""Business rules on top of a database Session (full CRUD since session 6)."""

from typing import Any

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Course, Enrollment, User
from app.schemas import CourseCreate, CourseReplace, CourseUpdate, Level, UserCreate, UserUpdate


class CourseService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_courses(
        self,
        *,
        level: Level | None = None,
        q: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        is_active: bool | None = True,
        offset: int = 0,
        limit: int = 10,
    ) -> list[Course]:
        stmt = select(Course)
        if level:
            stmt = stmt.where(Course.level == level)
        if q:
            stmt = stmt.where(Course.title.ilike(f'%{q}%'))
        if min_price is not None:
            stmt = stmt.where(Course.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Course.price <= max_price)
        if is_active is not None:
            stmt = stmt.where(Course.is_active == is_active)
        stmt = stmt.order_by(Course.id).offset(offset).limit(limit)
        return list(self.db.scalars(stmt))

    def get(self, course_id: int) -> Course:
        course = self.db.get(Course, course_id)
        if course is None:
            raise NotFoundError(f'Course {course_id} not found')
        return course

    def create(self, data: CourseCreate) -> Course:
        instructor = self.db.get(User, data.instructor_id)
        if instructor is None or instructor.role != 'instructor':
            raise BusinessRuleError('instructor_id must be an instructor')
        self._check_title_is_free(data.title, data.instructor_id)
        course = Course(**data.model_dump())
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def replace(self, course_id: int, data: CourseReplace) -> Course:
        return self._apply(self.get(course_id), data.model_dump())

    def update(self, course_id: int, data: CourseUpdate) -> Course:
        return self._apply(self.get(course_id), data.model_dump(exclude_unset=True))

    def delete(self, course_id: int) -> None:
        course = self.get(course_id)
        self.db.delete(course)
        self.db.commit()

    def _apply(self, course: Course, changes: dict[str, Any]) -> Course:
        if 'title' in changes and changes['title'] != course.title:
            self._check_title_is_free(changes['title'], course.instructor_id)
        if 'capacity' in changes:
            active = EnrollmentService(self.db).active_count(course.id)
            if changes['capacity'] < active:
                raise BusinessRuleError(f'capacity can not be lower than {active} active students')
        for field, value in changes.items():
            setattr(course, field, value)
        self.db.commit()
        self.db.refresh(course)
        return course

    def _check_title_is_free(self, title: str, instructor_id: int) -> None:
        taken = self.db.scalar(
            select(exists().where(Course.title == title, Course.instructor_id == instructor_id))
        )
        if taken:
            raise ConflictError('This instructor already has a course with this title')


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(
        self, *, role: str | None = None, offset: int = 0, limit: int = 10
    ) -> list[User]:
        stmt = select(User).order_by(User.id)
        if role:
            stmt = stmt.where(User.role == role)
        return list(self.db.scalars(stmt.offset(offset).limit(limit)))

    def get(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            raise NotFoundError(f'User {user_id} not found')
        return user

    def create(self, data: UserCreate) -> User:
        email = data.email.lower()
        if self.db.scalar(select(exists().where(User.email == email))):
            raise ConflictError('Email already registered')
        user = User(email=email, full_name=data.full_name, role=data.role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, data: UserUpdate) -> User:
        user = self.get(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> None:
        user = self.get(user_id)
        if self.db.scalar(select(exists().where(Course.instructor_id == user_id))):
            raise ConflictError('This user still teaches courses; move or delete them first')
        self.db.delete(user)
        self.db.commit()


class EnrollmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def active_count(self, course_id: int) -> int:
        stmt = select(func.count()).where(
            Enrollment.course_id == course_id, Enrollment.status == 'active'
        )
        return self.db.scalar(stmt) or 0

    def _find(self, course_id: int, student_id: int) -> Enrollment | None:
        stmt = select(Enrollment).where(
            Enrollment.course_id == course_id, Enrollment.student_id == student_id
        )
        return self.db.scalar(stmt)

    def enroll(self, course_id: int, student_id: int) -> Enrollment:
        course = CourseService(self.db).get(course_id)
        student = UserService(self.db).get(student_id)
        if student.role != 'student' or not student.is_active:
            raise BusinessRuleError('Only active students can enroll')
        if not course.is_active:
            raise BusinessRuleError('This course is closed')
        enrollment = self._find(course_id, student_id)
        if enrollment is not None and enrollment.status == 'active':
            raise ConflictError('Already enrolled')
        if self.active_count(course_id) >= course.capacity:
            raise ConflictError('Course is full')
        if enrollment is None:
            enrollment = Enrollment(course_id=course_id, student_id=student_id)
            self.db.add(enrollment)
        else:
            enrollment.status = 'active'  # a cancelled enrollment comes back
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def cancel(self, course_id: int, student_id: int) -> None:
        enrollment = self._find(course_id, student_id)
        if enrollment is None or enrollment.status != 'active':
            raise NotFoundError('No active enrollment for this student in this course')
        enrollment.status = 'cancelled'
        self.db.commit()

    def for_course(self, course_id: int) -> list[Enrollment]:
        CourseService(self.db).get(course_id)
        stmt = select(Enrollment).where(Enrollment.course_id == course_id).order_by(Enrollment.id)
        return list(self.db.scalars(stmt))
