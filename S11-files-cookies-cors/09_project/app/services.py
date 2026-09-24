"""Business rules on top of a database Session (full CRUD since session 6)."""

from pathlib import Path as FilePath
from typing import Any

from fastapi import UploadFile
from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import Settings
from app.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.models import Course, CourseMaterial, Enrollment, User
from app.pagination import paginate
from app.permissions import can_manage_course, ensure_can_manage_course
from app.schemas import (
    CourseCreate,
    CourseDetail,
    CourseQuery,
    CourseRead,
    CourseReplace,
    CourseStudent,
    CourseUpdate,
    InstructorSummary,
    Page,
    Token,
    UserCreate,
    UserQuery,
    UserRead,
    UserRegister,
    UserUpdate,
)
from app.security import create_access_token, hash_password, verify_password
from app.storage import LocalStorage

SORT_COLUMNS = {
    'title': Course.title.asc(),
    '-title': Course.title.desc(),
    'price': Course.price.asc(),
    '-price': Course.price.desc(),
    'start_date': Course.start_date.asc(),
    '-start_date': Course.start_date.desc(),
    'id': Course.id.asc(),
    '-id': Course.id.desc(),
}


class CourseService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_courses(self, query: CourseQuery) -> Page[CourseRead]:
        stmt = select(Course)
        if query.q:
            stmt = stmt.where(Course.title.ilike(f'%{query.q}%'))
        if query.level:
            stmt = stmt.where(Course.level == query.level)
        if query.instructor_id is not None:
            stmt = stmt.where(Course.instructor_id == query.instructor_id)
        if query.min_price is not None:
            stmt = stmt.where(Course.price >= query.min_price)
        if query.max_price is not None:
            stmt = stmt.where(Course.price <= query.max_price)
        if query.starts_after is not None:
            stmt = stmt.where(Course.start_date >= query.starts_after)
        if query.is_active is not None:
            stmt = stmt.where(Course.is_active == query.is_active)
        stmt = stmt.order_by(SORT_COLUMNS[query.sort], Course.id)  # id breaks ties
        return paginate(self.db, stmt, query, CourseRead)

    def get(self, course_id: int) -> Course:
        course = self.db.get(Course, course_id)
        if course is None:
            raise NotFoundError(f'Course {course_id} not found')
        return course

    def detail(self, course_id: int) -> CourseDetail:
        """The course AND its instructor in one query (joinedload), plus a count."""
        stmt = select(Course).options(joinedload(Course.instructor)).where(Course.id == course_id)
        course = self.db.scalar(stmt)
        if course is None:
            raise NotFoundError(f'Course {course_id} not found')
        active = EnrollmentService(self.db).active_count(course_id)
        return CourseDetail(
            **CourseRead.model_validate(course).model_dump(),
            instructor=InstructorSummary.model_validate(course.instructor),
            active_students=active,
        )

    def create(self, data: CourseCreate, actor: User) -> Course:
        instructor_id = self._choose_instructor(data.instructor_id, actor)
        self._check_title_is_free(data.title, instructor_id)
        course = Course(**data.model_dump(exclude={'instructor_id'}), instructor_id=instructor_id)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def replace(self, course_id: int, data: CourseReplace, actor: User) -> Course:
        course = self.get(course_id)
        ensure_can_manage_course(course, actor)
        return self._apply(course, data.model_dump())

    def update(self, course_id: int, data: CourseUpdate, actor: User) -> Course:
        course = self.get(course_id)
        ensure_can_manage_course(course, actor)
        return self._apply(course, data.model_dump(exclude_unset=True))

    def _choose_instructor(self, requested_id: int | None, actor: User) -> int:
        """Instructors always teach what they create; admins must say who teaches."""
        if actor.role == 'instructor':
            if requested_id not in (None, actor.id):
                raise PermissionDeniedError('Instructors can only create their own courses')
            return actor.id
        if requested_id is None:
            raise BusinessRuleError('instructor_id is required when an admin creates a course')
        instructor = self.db.get(User, requested_id)
        if instructor is None or instructor.role != 'instructor' or not instructor.is_active:
            raise BusinessRuleError('instructor_id must be an active instructor')
        return instructor.id

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

    def list_users(self, query: UserQuery) -> Page[UserRead]:
        stmt = select(User).order_by(User.id)
        if query.role:
            stmt = stmt.where(User.role == query.role)
        return paginate(self.db, stmt, query, UserRead)

    def get(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            raise NotFoundError(f'User {user_id} not found')
        return user

    def create(self, data: UserCreate) -> User:
        email = data.email.lower()
        if self.db.scalar(select(exists().where(User.email == email))):
            raise ConflictError('Email already registered')
        user = User(
            email=email,
            full_name=data.full_name,
            role=data.role,
            hashed_password=hash_password(data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def courses_taught(self, user_id: int) -> list[Course]:
        user = self.get(user_id)
        return sorted(user.courses_taught, key=lambda course: course.title)

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

    def enroll_many(self, student_id: int, course_ids: list[int]) -> list[Enrollment]:
        """All or nothing: if one course fails, none of the enrollments stays."""
        student = UserService(self.db).get(student_id)
        if student.role != 'student' or not student.is_active:
            raise BusinessRuleError('Only active students can enroll')
        enrollments = []
        try:
            for course_id in dict.fromkeys(course_ids):  # remove duplicates, keep order
                course = CourseService(self.db).get(course_id)
                if not course.is_active:
                    raise BusinessRuleError(f'{course.title} is closed')
                if self._find(course_id, student_id) is not None:
                    raise ConflictError(f'Already enrolled in {course.title}')
                if self.active_count(course_id) >= course.capacity:
                    raise ConflictError(f'{course.title} is full')
                enrollment = Enrollment(student=student, course=course)
                self.db.add(enrollment)
                self.db.flush()  # so the next active_count() sees it
                enrollments.append(enrollment)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return enrollments

    def for_student(self, student_id: int) -> list[Enrollment]:
        """Enrollments with their course: 2 queries in total, not 1 + N."""
        UserService(self.db).get(student_id)
        stmt = (
            select(Enrollment)
            .options(selectinload(Enrollment.course))
            .where(Enrollment.student_id == student_id)
            .order_by(Enrollment.id)
        )
        return list(self.db.scalars(stmt))

    def students_of(
        self, course_id: int, actor: User, status: str | None = None
    ) -> list[CourseStudent]:
        """One query with a JOIN, returning (enrollment, user) pairs."""
        ensure_can_manage_course(CourseService(self.db).get(course_id), actor)
        stmt = (
            select(Enrollment, User)
            .join(Enrollment.student)
            .where(Enrollment.course_id == course_id)
            .order_by(User.full_name)
        )
        if status:
            stmt = stmt.where(Enrollment.status == status)
        return [
            CourseStudent(
                student_id=user.id,
                full_name=user.full_name,
                email=user.email,
                status=enrollment.status,
                enrolled_at=enrollment.created_at,
            )
            for enrollment, user in self.db.execute(stmt).tuples()
        ]

    def for_course(self, course_id: int) -> list[Enrollment]:
        CourseService(self.db).get(course_id)
        stmt = select(Enrollment).where(Enrollment.course_id == course_id).order_by(Enrollment.id)
        return list(self.db.scalars(stmt))


class AuthService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    def register(self, data: UserRegister) -> User:
        """Public registration: always a student (see UserRegister)."""
        return UserService(self.db).create(UserCreate(**data.model_dump(), role='student'))

    def authenticate(self, email: str, password: str) -> User:
        """Return the user if the credentials are right, otherwise raise.

        Unknown e-mail and wrong password give the SAME error, so an attacker
        can not find out which e-mails are registered.
        """
        user = self.db.scalar(select(User).where(User.email == email.lower()))
        if user is None:
            verify_password(password, '!')  # same time as a real check
            raise AuthenticationError('Incorrect email or password')
        valid, new_hash = verify_password(password, user.hashed_password)
        if not valid:
            raise AuthenticationError('Incorrect email or password')
        if not user.is_active:
            raise PermissionDeniedError('This account is disabled')
        if new_hash is not None:
            user.hashed_password = new_hash
            self.db.commit()
        return user

    def login(self, email: str, password: str) -> Token:
        user = self.authenticate(email, password)
        return Token(
            access_token=create_access_token(user.id, user.role, self.settings),
            expires_in=self.settings.access_token_expire_minutes * 60,
        )


class MaterialService:
    """Course materials: files on disk, metadata in the database (session 11)."""

    def __init__(self, db: Session, storage: LocalStorage) -> None:
        self.db = db
        self.storage = storage

    def upload(self, course_id: int, upload: UploadFile, title: str, actor: User) -> CourseMaterial:
        course = CourseService(self.db).get(course_id)
        ensure_can_manage_course(course, actor)
        extension = self.storage.check_type(upload)
        stored_name, size = self.storage.save(upload, extension)
        material = CourseMaterial(
            course_id=course.id,
            title=title,
            original_filename=FilePath(upload.filename or 'file').name,
            stored_filename=stored_name,
            content_type=upload.content_type or 'application/octet-stream',
            size_bytes=size,
            uploaded_by_id=actor.id,
        )
        self.db.add(material)
        try:
            self.db.commit()
        except Exception:
            self.storage.delete(stored_name)  # no orphan file without a database row
            raise
        self.db.refresh(material)
        return material

    def list_for_course(self, course_id: int, actor: User) -> list[CourseMaterial]:
        course = CourseService(self.db).get(course_id)
        self._ensure_can_read(course, actor)
        stmt = select(CourseMaterial).where(CourseMaterial.course_id == course_id)
        return list(self.db.scalars(stmt.order_by(CourseMaterial.id)))

    def get_file(self, material_id: int, actor: User) -> tuple[CourseMaterial, FilePath]:
        material = self._get(material_id)
        self._ensure_can_read(material.course, actor)
        path = self.storage.path_for(material.stored_filename)
        if not path.is_file():
            raise NotFoundError('The file of this material is missing')
        return material, path

    def delete(self, material_id: int, actor: User) -> None:
        material = self._get(material_id)
        ensure_can_manage_course(material.course, actor)
        stored_name = material.stored_filename
        self.db.delete(material)
        self.db.commit()
        self.storage.delete(stored_name)

    def _get(self, material_id: int) -> CourseMaterial:
        material = self.db.get(CourseMaterial, material_id)
        if material is None:
            raise NotFoundError(f'Material {material_id} not found')
        return material

    def _ensure_can_read(self, course: Course, user: User) -> None:
        """Staff of the course, or a student who is (or was) enrolled in it."""
        if can_manage_course(course, user):
            return
        enrollment = self.db.scalar(
            select(Enrollment).where(
                Enrollment.course_id == course.id, Enrollment.student_id == user.id
            )
        )
        if enrollment is None or enrollment.status == 'cancelled':
            raise PermissionDeniedError('Only students of this course can see its materials')
