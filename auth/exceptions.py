"""Domain-specific exceptions for auth workflows."""


class AuthError(RuntimeError):
    """Base class for auth-related errors."""


class DuplicateEmailError(AuthError):
    """Raised when attempting to register an email that already exists."""

    def __init__(self, email: str):
        super().__init__(f"An account with email '{email}' already exists.")


class InvalidCredentialsError(AuthError):
    """Raised when provided credentials are invalid."""

    def __init__(self):
        super().__init__("Incorrect email or password.")


class UserNotFoundError(AuthError):
    """Raised when a user lookup fails."""

    def __init__(self, email: str):
        super().__init__(f"No account found for email '{email}'.")
