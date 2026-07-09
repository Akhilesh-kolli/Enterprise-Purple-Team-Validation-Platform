"""
Custom exceptions for the application.
"""


class AppException(Exception):
    """Base exception for the application."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(AppException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class NotFoundError(AppException):
    """Raised when resource is not found."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    """Raised when validation fails."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class ConflictError(AppException):
    """Raised when resource already exists."""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class InternalError(AppException):
    """Raised when internal error occurs."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)
