"""Business rules, now ASYNC (session 12).

Compared with session 11 the logic is identical. What changed:
* every method that talks to the database is `async def`
* every database call is awaited: `await self.db.get(...)`, `await self.db.commit()`
* `self.db.add(...)` is NOT awaited: it only stages an object, no I/O happens
* no lazy loading: relationships are loaded in the query (`selectinload`,
  `joinedload`) or fetched with an explicit query
"""

from pathlib import Path as FilePath
from typing import Any

from fastapi import UploadFile
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

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
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_courses(self, query: CourseQuery) -> Page[CourseRead]:
        stmt = select(Course)
        if query.q:
            stmt = stmt.where(Course.title.ilike(f'%{query.q}%'))
        if query.level:
            stmt = stmt.where(Course.level == query.level)
        if query.instructor_id is not None:
            stmt = stmt.where(Course.instructor_id == query.instructor_id)
        if query.min_price is not None:
            stmt = stmt.where(Course.price <= query.min_price)
        if query.max_price is not None:
            stmt = stmt.where(Course.price <= query.max_price)
        if query.starts_after is not None:
            stmt = stmt.where(Course.start_date >= query.starts_after)
        if query.is_active is not None:
            stmt = stmt.where(Course.is_active == query.is_active)
        stmt = stmt.order_by(SORT_COLUMNS[query.sort], Course.id)
        return await paginate(self.db, stmt, query, CourseRead)

    async def get(self, course_id: int) -> Course:
        course = await self.db.get(Course, course_id)
        if course is None:
            raise NotFoundError(f'Course {course_id} not found')
        return course

    async def detail(self, course_id: int) -> CourseDetail:
        stmt = select(Course).options(joinedload(Course.instructor)).where(Course.id == course_id)
        course = await self.db.scalar(stmt)
        if course is None:
            raise NotFoundError(f'Course {course_id} not found')
        active = await EnrollmentService(self.db).active_count(course_id)
        return CourseDetail(
            **CourseRead.model_validate(course).model_dump(),
            instructor=InstructorSummary.model_validate(course.instructor),
            active_students=active,
        )

    async def create(self, data: CourseCreate, actor: User) -> Course:
        instructor_id = await self._choose_instructor(data.instructor_id, actor)
        await self._check_title_is_free(data.title, instructor_id)
        course = Course(**data.model_dump(exclude={'instructor_id'}), instructor_id=instructor_id)
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def replace(self, course_id: int, data: CourseReplace, actor: User) -> Course:
        course = await self.get(course_id)
        ensure_can_manage_course(course, actor)
        return await self._apply(course, data.model_dump())

    async def update(self, course_id: int, data: CourseUpdate, actor: User) -> Course:
        course = await self.get(course_id)
        ensure_can_manage_course(course, actor)
        return await self._apply(course, data.model_dump(exclude_unset=True))

    async def delete(self, course_id: int) -> None:
        course = await self.get(course_id)
        await self.db.delete(course)  # delete() IS awaited in AsyncSession
        await self.db.commit()

    async def _choose_instructor(self, requested_id: int | None, actor: User) -> int:
        if actor.role == 'instructor':
            if requested_id not in (None, actor.id):
                raise PermissionDeniedError('Instructors can only create their own courses')
            return actor.id
        if requested_id is None:
            raise BusinessRuleError('instructor_id is required when an admin creates a course')
        instructor = await self.db.get(User, requested_id)
        if instructor is None or instructor.role != 'instructor' or not instructor.is_active:
            raise BusinessRuleError('instructor_id must be an active instructor')
        return instructor.id

    async def _apply(self, course: Course, changes: dict[str, Any]) -> Course:
        if 'title' in changes and changes['title'] != course.title:
            await self._check_title_is_free(changes['title'], course.instructor_id)
        if 'capacity' in changes:
            active = await EnrollmentService(self.db).active_count(course.id)
            if changes['capacity'] < active:
                raise BusinessRuleError(f'capacity can not be lower than {active} active students')
        for field, value in changes.items():
            setattr(course, field, value)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def _check_title_is_free(self, title: str, instructor_id: int) -> None:
        taken = await self.db.scalar(
            select(exists().where(Course.title == title, Course.instructor_id == instructor_id))
        )
        if taken:
            raise ConflictError('This instructor already has a course with this title')


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_users(self, query: UserQuery) -> Page[UserRead]:
        stmt = select(User).order_by(User.id)
        if query.role:
            stmt = stmt.where(User.role == query.role)
        return await paginate(self.db, stmt, query, UserRead)

    async def get(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if user is None:
            raise NotFoundError(f'User {user_id} not found')
        return user

    async def create(self, data: UserCreate) -> User:
        email = data.email.lower()
        if await self.db.scalar(select(exists().where(User.email == email))):
            raise ConflictError('Email already registered')
        user = User(
            email=email,
            full_name=data.full_name,
            role=data.role,
            hashed_password=hash_password(data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def courses_taught(self, user_id: int) -> list[Course]:
        # `user.courses_taught` would be a lazy load -> not allowed in async: query instead
        await self.get(user_id)
        stmt = select(Course).where(Course.instructor_id == user_id).order_by(Course.title)
        return list(await self.db.scalars(stmt))

    async def update(self, user_id: int, data: UserUpdate) -> User:
        user = await self.get(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # TODO (capstone): update_me(user, data) and change_password(user, data)

    async def delete(self, user_id: int) -> None:
        user = await self.get(user_id)
        if await self.db.scalar(select(exists().where(Course.instructor_id == user_id))):
            raise ConflictError('This user still teaches courses; move or delete them first')
        await self.db.delete(user)
        await self.db.commit()


class EnrollmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def active_count(self, course_id: int) -> int:
        stmt = select(func.count()).where(
            Enrollment.course_id == course_id, Enrollment.status == 'active'
        )
        return await self.db.scalar(stmt) or 0

    async def _find(self, course_id: int, student_id: int) -> Enrollment | None:
        stmt = select(Enrollment).where(
            Enrollment.course_id == course_id, Enrollment.student_id == student_id
        )
        return await self.db.scalar(stmt)

    async def enroll(self, course_id: int, student_id: int) -> Enrollment:
        course = await CourseService(self.db).get(course_id)
        student = await UserService(self.db).get(student_id)
        if student.role != 'student' or not student.is_active:
            raise BusinessRuleError('Only active students can enroll')
        if not course.is_active:
            raise BusinessRuleError('This course is closed')
        enrollment = await self._find(course_id, student_id)
        if enrollment is not None and enrollment.status == 'active':
            raise ConflictError('Already enrolled')
        if await self.active_count(course_id) > course.capacity:
            raise ConflictError('Course is full')
        if enrollment is None:
            enrollment = Enrollment(course_id=course_id, student_id=student_id)
            self.db.add(enrollment)
        else:
            enrollment.status = 'active'
        await self.db.commit()
        await self.db.refresh(enrollment)
        return enrollment

    async def cancel(self, course_id: int, student_id: int) -> None:
        enrollment = await self._find(course_id, student_id)
        if enrollment is None or enrollment.status != 'active':
            raise NotFoundError('No active enrollment for this student in this course')
        enrollment.status = 'cancelled'
        await self.db.commit()

    async def enroll_many(self, student_id: int, course_ids: list[int]) -> list[Enrollment]:
        """All or nothing: if one course fails, none of the enrollments stays."""
        student = await UserService(self.db).get(student_id)
        if student.role != 'student' or not student.is_active:
            raise BusinessRuleError('Only active students can enroll')
        enrollments = []
        try:
            for course_id in dict.fromkeys(course_ids):
                course = await CourseService(self.db).get(course_id)
                if not course.is_active:
                    raise BusinessRuleError(f'{course.title} is closed')
                if await self._find(course_id, student_id) is not None:
                    raise ConflictError(f'Already enrolled in {course.title}')
                if await self.active_count(course_id) >= course.capacity:
                    raise ConflictError(f'{course.title} is full')
                enrollment = Enrollment(student=student, course=course)
                self.db.add(enrollment)
                await self.db.flush()
                enrollments.append(enrollment)
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
        return enrollments

    async def for_student(self, student_id: int) -> list[Enrollment]:
        await UserService(self.db).get(student_id)
        stmt = select(Enrollment).where(Enrollment.student_id == student_id).order_by(Enrollment.id)
        return list(await self.db.scalars(stmt))

    async def students_of(
        self, course_id: int, actor: User, status: str | None = None
    ) -> list[CourseStudent]:
        await CourseService(self.db).get(course_id)
        stmt = (
            select(Enrollment, User)
            .join(Enrollment.student)
            .where(Enrollment.course_id == course_id)
            .order_by(User.full_name)
        )
        if status:
            stmt = stmt.where(Enrollment.status == status)
        rows = await self.db.execute(stmt)
        return [
            CourseStudent(
                student_id=user.id,
                full_name=user.full_name,
                email=user.email,
                status=enrollment.status,
                enrolled_at=enrollment.created_at,
            )
            for enrollment, user in rows.tuples()
        ]


class AuthService:
    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings

    async def register(self, data: UserRegister) -> User:
        return await UserService(self.db).create(UserCreate(**data.model_dump(), role='student'))

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.db.scalar(select(User).where(User.email == email.lower()))
        if user is None:
            verify_password(password, '!')
            raise AuthenticationError('Incorrect email or password')
        valid, new_hash = verify_password(password, user.hashed_password)
        if not valid:
            raise AuthenticationError('Incorrect email or password')
        if not user.is_active:
            raise PermissionDeniedError('This account is disabled')
        if new_hash is not None:
            user.hashed_password = new_hash
            await self.db.commit()
        return user

    async def login(self, email: str, password: str) -> Token:
        user = await self.authenticate(email, password)
        return Token(
            access_token=create_access_token(user.id, user.role, self.settings),
            expires_in=self.settings.access_token_expire_minutes * 60,
        )


class MaterialService:
    def __init__(self, db: AsyncSession, storage: LocalStorage) -> None:
        self.db = db
        self.storage = storage

    async def upload(
        self, course_id: int, upload: UploadFile, title: str, actor: User
    ) -> CourseMaterial:
        course = await CourseService(self.db).get(course_id)
        ensure_can_manage_course(course, actor)
        extension = await self.storage.check_type(upload)
        stored_name, size = await self.storage.save(upload, extension)
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
            await self.db.commit()
        except Exception:
            await self.storage.delete(stored_name)
            raise
        await self.db.refresh(material)
        return material

    async def list_for_course(self, course_id: int, actor: User) -> list[CourseMaterial]:
        course = await CourseService(self.db).get(course_id)
        await self._ensure_can_read(course, actor)
        stmt = select(CourseMaterial).where(CourseMaterial.course_id == course_id)
        return list(await self.db.scalars(stmt.order_by(CourseMaterial.id)))

    async def get_file(self, material_id: int, actor: User) -> tuple[CourseMaterial, FilePath]:
        material = await self._get(material_id)
        await self._ensure_can_read(material.course, actor)
        path = self.storage.path_for(material.stored_filename)
        if not path.is_file():
            raise NotFoundError('The file of this material is missing')
        return material, path

    async def delete(self, material_id: int, actor: User) -> None:
        material = await self._get(material_id)
        ensure_can_manage_course(material.course, actor)
        stored_name = material.stored_filename
        await self.db.delete(material)
        await self.db.commit()
        await self.storage.delete(stored_name)

    async def _get(self, material_id: int) -> CourseMaterial:
        # material.course is needed afterwards: load it in the same query (no lazy load)
        stmt = (
            select(CourseMaterial)
            .options(joinedload(CourseMaterial.course))
            .where(CourseMaterial.id == material_id)
        )
        material = await self.db.scalar(stmt)
        if material is None:
            raise NotFoundError(f'Material {material_id} not found')
        return material

    async def _ensure_can_read(self, course: Course, user: User) -> None:
        if can_manage_course(course, user):
            return
        enrollment = await self._find_enrollment(course.id, user.id)
        if enrollment is None:
            raise PermissionDeniedError('Only students of this course can see its materials')

    async def _find_enrollment(self, course_id: int, user_id: int) -> Enrollment | None:
        stmt = select(Enrollment).where(
            Enrollment.course_id == course_id, Enrollment.student_id == user_id
        )
        return await self.db.scalar(stmt)
