"""A small exception hierarchy: catch broadly (`TrainingCenterError`) or narrowly."""


class TrainingCenterError(Exception):
    """Base class of all expected business errors."""


class ValidationError(TrainingCenterError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f'{field}: {message}')
        self.field = field
        self.message = message


class NotFoundError(TrainingCenterError):
    def __init__(self, entity: str, entity_id: int) -> None:
        super().__init__(f'{entity} {entity_id} not found')
        self.entity = entity
        self.entity_id = entity_id


class DuplicateError(TrainingCenterError):
    pass


class CourseFullError(TrainingCenterError):
    pass


class AlreadyEnrolledError(TrainingCenterError):
    pass


class PermissionDeniedError(TrainingCenterError):
    pass
