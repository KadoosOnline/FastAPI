"""Business logic. Services know the rules; they know nothing about HTTP."""

from app.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    EnrollmentRead,
    Level,
    UserCreate,
    UserRead,
)
from app.store import Store, now


class CourseService:
    def __init__(self, store: Store) -> None:
        self.store = store

    def list_courses(
        self, *, level: Level | None, q: str | None, offset: int, limit: int
    ) -> list[CourseRead]:
        courses = list(self.store.courses.values())
        if level:
            courses = [c for c in courses if c.level == level]
        if q:
            courses = [c for c in courses if q.lower() in c.title.lower()]
        return courses[offset : offset + limit]

    def get(self, course_id: int) -> CourseRead:
        if course_id not in self.store.courses:
            raise NotFoundError(f'Course {course_id} not found')
        return self.store.courses[course_id]

    def create(self, data: CourseCreate) -> CourseRead:
        instructor = self.store.users.get(data.instructor_id)
        if instructor is None or instructor.role != 'instructor':
            raise BusinessRuleError('instructor_id must be an instructor')
        course = CourseRead(
            id=self.store.next_id(self.store.courses), created_at=now(), **data.model_dump()
        )
        self.store.courses[course.id] = course
        return course

    def update(self, course_id: int, data: CourseUpdate) -> CourseRead:
        course = self.get(course_id)
        updated = course.model_copy(update=data.model_dump(exclude_unset=True))
        self.store.courses[course_id] = updated
        return updated

    def delete(self, course_id: int) -> None:
        self.get(course_id)
        del self.store.courses[course_id]


class UserService:
    def __init__(self, store: Store) -> None:
        self.store = store

    def list_users(self, *, offset: int, limit: int) -> list[UserRead]:
        return list(self.store.users.values())[offset : offset + limit]

    def get(self, user_id: int) -> UserRead:
        if user_id not in self.store.users:
            raise NotFoundError(f'User {user_id} not found')
        return self.store.users[user_id]

    def create(self, data: UserCreate) -> UserRead:
        email = data.email.lower()
        if any(user.email == email for user in self.store.users.values()):
            raise ConflictError('Email already registered')
        user = UserRead(
            id=self.store.next_id(self.store.users),
            created_at=now(),
            **data.model_dump() | {'email': email},
        )
        self.store.users[user.id] = user
        return user


class EnrollmentService:
    def __init__(self, store: Store, courses: CourseService, users: UserService) -> None:
        self.store = store
        self.courses = courses
        self.users = users

    def enroll(self, course_id: int, student_id: int) -> EnrollmentRead:
        course = self.courses.get(course_id)
        student = self.users.get(student_id)
        if student.role != 'student':
            raise BusinessRuleError('Only students can enroll')
        active = self.for_course(course_id)
        if any(e.student_id == student_id for e in active):
            raise ConflictError('Already enrolled')
        if len(active) >= course.capacity:
            raise ConflictError('Course is full')
        enrollment = EnrollmentRead(
            id=self.store.next_id(self.store.enrollments),
            student_id=student_id,
            course_id=course_id,
            created_at=now(),
        )
        self.store.enrollments[enrollment.id] = enrollment
        return enrollment

    def for_course(self, course_id: int) -> list[EnrollmentRead]:
        self.courses.get(course_id)
        return [
            e
            for e in self.store.enrollments.values()
            if e.course_id == course_id and e.status == 'active'
        ]
