from datetime import datetime
from uuid import UUID

from ..core.exceptions import AppException, NotFoundException


class BookNotFoundException(NotFoundException):
    def __init__(self, book_id: UUID):
        super().__init__(resource="Book", identifier=book_id)


class BookAlreadyExistsException(AppException):
    def __init__(self, isbn: str):
        super().__init__(
            message=f"Book with ISBN '{isbn}' already exists",
            status_code=409,
        )


class InvalidYearException(AppException):
    def __init__(self, year: int):
        super().__init__(
            message=f"Year {year} is invalid (must be 1000-{current_year})",
            status_code=400,
        )


class InvalidPagesException(AppException):
    def __init__(self, pages: int):
        super().__init__(
            message=f"Pages count must be positive, got {pages}",
            status_code=400,
        )


class OpenLibraryException(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=f"Open Library API error: {message}",
            status_code=503,
        )


class OpenLibraryTimeoutException(OpenLibraryException):
    def __init__(self, timeout: float):
        super().__init__(message=f"timeout after {timeout}s")
        self.status_code = 504
