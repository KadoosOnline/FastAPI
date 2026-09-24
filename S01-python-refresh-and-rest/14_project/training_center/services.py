"""Business rules. The service *composes* repositories instead of inheriting from them."""

from training_center.decorators import log_calls
from training_center.exceptions import (
    AlreadyEnrolledError,
    CourseFullError,
    PermissionDeniedError,
    ValidationError,
)
from training_center.models import Course, Role, User
from training_center.repository import InMemoryRepository


class TrainingCenterService:
    def __init__(
        self, users: InMemoryRepository[User], courses: InMemoryRepository[Course]
    ) -> None:
        self.users = users
        self.courses = courses

    def register_user(self, email: str, full_name: str, role: Role = Role.STUDENT) -> User:
        if self.users.find(lambda user: user.email == email.strip().lower()):
            raise ValidationError('email', 'email already registered')
        return self.users.add(
            User(id=self.users.next_id(), email=email, full_name=full_name, role=role)
        )

    def create_course(self, actor_id: int, *, title: str, price: int, capacity: int) -> Course:
        actor = self.users.get(actor_id)
        if actor.role is not Role.INSTRUCTOR:
            raise PermissionDeniedError('only instructors can create courses')
        course = Course(
            id=self.courses.next_id(),
            title=title,
            price=price,
            capacity=capacity,
            instructor_id=actor.id,
        )
        return self.courses.add(course)

    @log_calls
    def enroll(self, student_id: int, course_id: int) -> Course:
        student = self.users.get(student_id)
        course = self.courses.get(course_id)
        if student.role is not Role.STUDENT or not student.is_active:
            raise PermissionDeniedError('only active students can enroll')
        if student.id in course.student_ids:
            raise AlreadyEnrolledError(f'user {student.id} is already in course {course.id}')
        if course.is_full:
            raise CourseFullError(f'course {course.id} is full')
        course.student_ids.add(student.id)
        return course

    def students_of(self, course_id: int) -> list[User]:
        course = self.courses.get(course_id)
        return sorted(
            (self.users.get(student_id) for student_id in course.student_ids),
            key=lambda user: user.full_name,
        )

    def search_courses(
        self, text: str | None = None, *, max_price: int | None = None
    ) -> list[Course]:
        def matches(course: Course) -> bool:
            if text is not None and text.lower() not in course.title.lower():
                return False
            return max_price is None or course.price <= max_price

        return sorted(self.courses.find(matches), key=lambda course: course.price)
