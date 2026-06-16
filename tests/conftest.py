"""Общие фикстуры pytest для проекта."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.library_catalog.data.models.book import Book


@pytest.fixture
def sample_book() -> Book:
    """ORM-объект книги (без сохранения в БД) для unit-тестов."""
    now = datetime.now(timezone.utc)
    book = Book(
        title="Clean Code",
        author="Robert Martin",
        year=2008,
        genre="Programming",
        pages=464,
        available=True,
        isbn="9780132350884",
        description="A Handbook of Agile Software Craftsmanship",
        extra={"cover_url": "https://covers.openlibrary.org/b/id/1-L.jpg"},
    )
    book.book_id = uuid4()
    book.created_at = now
    book.updated_at = now
    return book


@pytest.fixture
def book_create_payload() -> dict:
    """Корректные данные для создания книги."""
    return {
        "title": "Clean Code",
        "author": "Robert Martin",
        "year": 2008,
        "genre": "Programming",
        "pages": 464,
        "isbn": "9780132350884",
        "description": "A Handbook of Agile Software Craftsmanship",
    }
