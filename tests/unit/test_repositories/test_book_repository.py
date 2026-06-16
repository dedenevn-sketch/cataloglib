"""Интеграционные тесты BookRepository.

Требуют доступную тестовую PostgreSQL. Задайте TEST_DATABASE_URL, например:
    TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/library_test
Если переменная не задана — тесты пропускаются.
"""

import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.library_catalog.core.database import Base
from src.library_catalog.data.models.book import Book  # noqa: F401
from src.library_catalog.data.repositories.book_repository import BookRepository

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="TEST_DATABASE_URL не задан — пропускаем интеграционные тесты репозитория",
)


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=None)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def repo(session):
    return BookRepository(session)


@pytest.mark.asyncio
async def test_create_and_get(repo):
    book = await repo.create(
        title="Clean Code", author="Robert Martin", year=2008,
        genre="Programming", pages=464, isbn="9780132350884",
        description=None, extra=None,
    )
    fetched = await repo.get_by_id(book.book_id)
    assert fetched is not None
    assert fetched.title == "Clean Code"


@pytest.mark.asyncio
async def test_find_by_isbn(repo):
    await repo.create(
        title="A", author="B", year=2000, genre="G", pages=10,
        isbn="1112223334445", description=None, extra=None,
    )
    found = await repo.find_by_isbn("1112223334445")
    assert found is not None


@pytest.mark.asyncio
async def test_filters_and_count(repo):
    await repo.create(title="Python", author="X", year=2020, genre="Tech",
                      pages=100, isbn=None, description=None, extra=None)
    await repo.create(title="Java", author="Y", year=2019, genre="Tech",
                      pages=200, isbn=None, description=None, extra=None)
    results = await repo.find_by_filters(title="Py")
    total = await repo.count_by_filters(title="Py")
    assert total == 1
    assert results[0].title == "Python"


@pytest.mark.asyncio
async def test_update_and_delete(repo):
    book = await repo.create(title="Old", author="A", year=2000, genre="G",
                             pages=10, isbn=None, description=None, extra=None)
    updated = await repo.update(book.book_id, title="New")
    assert updated.title == "New"
    assert await repo.delete(book.book_id) is True
    assert await repo.get_by_id(book.book_id) is None
