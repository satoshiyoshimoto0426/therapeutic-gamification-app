class AppError(Exception):
    pass


class ValidationError(AppError):
    pass


class NotFoundError(AppError):
    """Entity not found."""
    pass


class DatabaseError(AppError):
    """Database operation failed."""
    pass

