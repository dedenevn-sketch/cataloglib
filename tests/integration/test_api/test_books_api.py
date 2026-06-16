"""Интеграционные тесты API через ASGITransport с подменой сервиса.

БД не требуется: BookService подменяется заглушкой через dependency_overrides.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.library_catalog.api.dependencies import get_book_service
from src.library_catalog.api.v1.schemas.book import ShowBook
from src.library_catalog.domain.exceptions import BookNotFoundException
from src.library_catalog.main import app


def make_show_book(**overrides) -> ShowBook:
    now = datetime.now(timezone.utc)
    data = dict(
        book_id=uuid4(), title="Clean Code", author="Robert Martin",
        year=2008, genre="Programming", pages=464, available=True,
        isbn="9780132350884", description="desc", extra=None,
        created_at=now, updated_at=now,
    )
    data.update(overrides)
    return ShowBook(**data)


@pytest_asyncio.fixture
async def client_and_service():
    service = AsyncMock()
    app.dependency_overrides[get_book_service] = lambda: service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, service
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_root(client_and_service):
    client, _ = client_and_service
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_create_book(client_and_service):
    client, service = client_and_service
    book = make_show_book()
    service.create_book.return_value = book
    payload = {
        "title": "Clean Code", "author": "Robert Martin", "year": 2008,
        "genre": "Programming", "pages": 464, "isbn": "9780132350884",
    }
    resp = await client.post("/api/v1/books/", json=payload)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Clean Code"


@pytest.mark.asyncio
async def test_create_book_validation_error(client_and_service):
    client, _ = client_and_service
    resp = await client.post("/api/v1/books/", json={"title": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_book_not_found(client_and_service):
    client, service = client_and_service
    bid = uuid4()
    service.get_book.side_effect = BookNotFoundException(bid)
    resp = await client.get(f"/api/v1/books/{bid}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_books_pagination(client_and_service):
    client, service = client_and_service
    service.search_books.return_value = ([make_show_book()], 1)
    resp = await client.get("/api/v1/books/?page=1&page_size=20")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["pages"] == 1


@pytest.mark.asyncio
async def test_delete_book(client_and_service):
    client, service = client_and_service
    service.delete_book.return_value = None
    resp = await client.delete(f"/api/v1/books/{uuid4()}")
    assert resp.status_code == 204
