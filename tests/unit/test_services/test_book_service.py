"""Unit-тесты BookService (репозиторий и клиент мокаются)."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.library_catalog.api.v1.schemas.book import BookCreate, BookUpdate
from src.library_catalog.domain.exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidPagesException,
    InvalidYearException,
)
from src.library_catalog.domain.services.book_service import BookService


def make_service(repo: AsyncMock, ol: AsyncMock) -> BookService:
    return BookService(book_repository=repo, openlibrary_client=ol)


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def ol() -> AsyncMock:
    client = AsyncMock()
    client.enrich.return_value = {"cover_url": "https://example/cover.jpg"}
    return client


@pytest.mark.asyncio
async def test_create_book_success(repo, ol, sample_book, book_create_payload):
    repo.find_by_isbn.return_value = None
    repo.create.return_value = sample_book
    service = make_service(repo, ol)

    result = await service.create_book(BookCreate(**book_create_payload))

    assert result.title == sample_book.title
    repo.create.assert_awaited_once()
    ol.enrich.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_book_duplicate_isbn(repo, ol, sample_book, book_create_payload):
    repo.find_by_isbn.return_value = sample_book
    service = make_service(repo, ol)

    with pytest.raises(BookAlreadyExistsException):
        await service.create_book(BookCreate(**book_create_payload))
    repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_book_invalid_year(repo, ol, book_create_payload):
    payload = {**book_create_payload, "year": 999}
    service = make_service(repo, ol)
    # Pydantic перехватит year<1000 на уровне схемы, поэтому проверяем сервис напрямую
    with pytest.raises(InvalidYearException):
        service._validate_year(999)


@pytest.mark.asyncio
async def test_create_book_invalid_pages(repo, ol):
    service = make_service(repo, ol)
    with pytest.raises(InvalidPagesException):
        service._validate_pages(0)


@pytest.mark.asyncio
async def test_get_book_not_found(repo, ol):
    repo.get_by_id.return_value = None
    service = make_service(repo, ol)
    with pytest.raises(BookNotFoundException):
        await service.get_book(uuid4())


@pytest.mark.asyncio
async def test_get_book_success(repo, ol, sample_book):
    repo.get_by_id.return_value = sample_book
    service = make_service(repo, ol)
    result = await service.get_book(sample_book.book_id)
    assert result.book_id == sample_book.book_id


@pytest.mark.asyncio
async def test_update_book_not_found(repo, ol):
    repo.get_by_id.return_value = None
    service = make_service(repo, ol)
    with pytest.raises(BookNotFoundException):
        await service.update_book(uuid4(), BookUpdate(title="New"))


@pytest.mark.asyncio
async def test_update_book_success(repo, ol, sample_book):
    repo.get_by_id.return_value = sample_book
    repo.update.return_value = sample_book
    service = make_service(repo, ol)
    result = await service.update_book(sample_book.book_id, BookUpdate(title="New"))
    assert result.book_id == sample_book.book_id
    repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_book_not_found(repo, ol):
    repo.delete.return_value = False
    service = make_service(repo, ol)
    with pytest.raises(BookNotFoundException):
        await service.delete_book(uuid4())


@pytest.mark.asyncio
async def test_delete_book_success(repo, ol):
    repo.delete.return_value = True
    service = make_service(repo, ol)
    await service.delete_book(uuid4())
    repo.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_books(repo, ol, sample_book):
    repo.find_by_filters.return_value = [sample_book]
    repo.count_by_filters.return_value = 1
    service = make_service(repo, ol)
    books, total = await service.search_books(title="Clean")
    assert total == 1
    assert len(books) == 1


@pytest.mark.asyncio
async def test_enrich_failure_does_not_break_create(repo, ol, sample_book, book_create_payload):
    from src.library_catalog.domain.exceptions import OpenLibraryException

    repo.find_by_isbn.return_value = None
    repo.create.return_value = sample_book
    ol.enrich.side_effect = OpenLibraryException("down")
    service = make_service(repo, ol)

    result = await service.create_book(BookCreate(**book_create_payload))
    assert result.title == sample_book.title
    # extra передан как None при сбое обогащения
    assert repo.create.await_args.kwargs["extra"] is None
