from __future__ import annotations

from typing import Any


class DomainError(Exception):
    status_code = 400
    code = "domain_error"
    message = "Domain error"

    def __init__(self, message: str | None = None, details: Any = None) -> None:
        super().__init__(message or self.message)
        self.details = details
        self.message = message or self.message


class NotFoundDomainError(DomainError):
    status_code = 404
    code = "not_found"
    message = "Resource not found"


class ConflictDomainError(DomainError):
    status_code = 409
    code = "conflict"
    message = "Conflict"
