"""Domain-level exceptions.

These are plain Python exceptions with no framework dependency. The API
layer maps them to HTTP status codes via a global exception handler.
"""
from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain errors."""


class DocumentNotFoundError(DomainError):
    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        super().__init__(f"Document '{document_id}' was not found")


class UserNotFoundError(DomainError):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User '{user_id}' was not found")


class AccessDeniedError(DomainError):
    def __init__(self, message: str = "You do not have access to this resource") -> None:
        super().__init__(message)


class UnsupportedFileTypeError(DomainError):
    def __init__(self, filename: str) -> None:
        self.filename = filename
        super().__init__(
            f"Unsupported file type for '{filename}'. Only .txt and .md files are supported."
        )


class ValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
