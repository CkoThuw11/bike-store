class DomainException(Exception):
    """
    Base for all known domain/application errors.
    Every subclass must provide a unique `code` for the global handler
    to map it to the correct HTTP status code.
    """

    def __init__(self, message: str, code: str) -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)

    @staticmethod
    def _format_id(entity_id: str | int | dict) -> str:
        if isinstance(entity_id, dict):
            return ", ".join(f"{k}={v}" for k, v in entity_id.items())
        return str(entity_id)


# Validation & Business Rules


class DomainValidationException(DomainException):
    """Raised when input violates domain validation rules."""

    def __init__(self, message: str):
        super().__init__(message=message, code="VALIDATION_ERROR")


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""

    def __init__(self, message: str):
        super().__init__(message=message, code="BUSINESS_RULE_VIOLATION")


# Entity Errors


class EntityNotFoundError(DomainException):
    def __init__(self, entity_name: str, entity_id: str | int | dict):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(
            message=f"{entity_name} with identifier '{self._format_id(entity_id)}' not found",
            code="ENTITY_NOT_FOUND",
        )


class EntityAlreadyExistsException(DomainException):
    def __init__(self, entity_name: str, entity_id: str | int | dict):
        self.entity_name = entity_name
        self.entity_id = entity_id
        super().__init__(
            message=f"{entity_name} with identifier '{self._format_id(entity_id)}' already exists",
            code="ENTITY_ALREADY_EXISTS",
        )


# Auth — Credentials


class InvalidCredentialsException(DomainException):
    def __init__(self) -> None:
        super().__init__(message="Invalid email or password", code="INVALID_CREDENTIALS")


class InvalidAccountStatusException(DomainException):
    """Raised when a user account is inactive, banned, or otherwise ineligible to login."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(message=f"Account {user_id} is not active", code="ACCOUNT_INACTIVE")


class EmailAlreadyExistsError(DomainException):
    """Raised when registering with an already registered email."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(message=f"{email} is already registered", code="EMAIL_ALREADY_EXISTS")


class InsufficientPermissionsError(DomainException):
    """Raised when a user lacks the required role for an action."""

    def __init__(self) -> None:
        super().__init__(message="Insufficient permissions", code="FORBIDDEN")


# Auth — Token


class TokenMissingError(DomainException):
    """Raised when no token is provided in the request."""

    def __init__(self) -> None:
        super().__init__(message="No token provided", code="TOKEN_MISSING")


class TokenInvalidError(DomainException):
    """Raised when a token is malformed or has an invalid signature."""

    def __init__(self) -> None:
        super().__init__(message="Invalid token", code="TOKEN_INVALID")


class TokenExpiredException(DomainException):
    """Raised when an access or refresh token has expired."""

    def __init__(self) -> None:
        super().__init__(message="Token has expired", code="TOKEN_EXPIRED")


class TokenRevokedException(DomainException):
    """Raised when a revoked refresh token is reused — indicates potential token theft."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(
            message=f"Revoked token reuse detected for user '{user_id}'", code="TOKEN_REVOKED"
        )


# Security


class SecurityBreachException(DomainException):
    """Raised when a security breach is detected (e.g., refresh token reuse after revocation)."""

    def __init__(self, user_id: int, reason: str):
        self.user_id = user_id
        self.reason = reason
        super().__init__(
            message=f"Security breach detected for user '{user_id}': {reason}",
            code="SECURITY_BREACH",
        )
