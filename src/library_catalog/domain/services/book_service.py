"""Бизнес-логика работы с книгами."""

import logging
from datetime import datetime
from uuid import UUID

from ...api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from ...data.repositories.book_repository import BookRepository
from ...external.openlibrary.client import OpenLibraryClient
from ..exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidPagesException,
    InvalidYearException,
    OpenLibraryException,
)
from ..mappers.book_mapper import to_show_book, to_show_books

logger = logging.getLogger(__name__)


class BookService:
    def __init__(
        self,
        book_repository: BookRepository,
        openlibrary_client: OpenLibraryClient,
    ):
        self.book_repo = book_repository
        self.ol_client = openlibrary_client

    async def create_book(self, book_data: BookCreate) -> ShowBook:
        self._validate_fields(year=book_data.year, pages=book_data.pages)

        if book_data.isbn:
            existing = await self.book_repo.find_by_isbn(book_data.isbn)
            if existing:
                raise BookAlreadyExistsException(book_data.isbn)

        extra = await self._enrich_book_data(book_data)

        book = await self.book_repo.create(
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
            genre=book_data.genre,
            pages=book_data.pages,
            isbn=book_data.isbn,
            description=book_data.description,
            extra=extra,
        )

        return to_show_book(book)

    async def get_book(self, book_id: UUID) -> ShowBook:
        book = await self.book_repo.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(book_id)
        return to_show_book(book)

    async def update_book(self, book_id: UUID, book_data: BookUpdate) -> ShowBook:
        existing = await self.book_repo.get_by_id(book_id)
        if existing is None:
            raise BookNotFoundException(book_id)
        self._validate_fields(year=book_data.year, pages=book_data.pages)
        updated = await self.book_repo.update_instance(
            existing,
            **book_data.model_dump(exclude_unset=True),
        )
        return to_show_book(updated)

    async def delete_book(self, book_id: UUID) -> None:
        deleted = await self.book_repo.delete(book_id)
        if not deleted:
            raise BookNotFoundException(book_id)

    async def search_books(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ShowBook], int]:
        books = await self.book_repo.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )
        total = await self.book_repo.count_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )
        return to_show_books(books), total

    def _validate_book_data(self, data: BookCreate) -> None:
        self._validate_year(data.year)
        self._validate_pages(data.pages)

    def _validate_year(self, year: int) -> None:
        current_year = datetime.now().year
        if year < 1000 or year > current_year:
            raise InvalidYearException(year)

    def _validate_pages(self, pages: int) -> None:
        if pages <= 0:
            raise InvalidPagesException(pages)

    async def _enrich_book_data(self, book_data: BookCreate) -> dict | None:
        try:
            extra = await self.ol_client.enrich(
                title=book_data.title,
                author=book_data.author,
                isbn=book_data.isbn,
            )
            return extra or None
        except OpenLibraryException:
            logger.warning(
                "Failed to enrich book data from Open Library (title=%s, author=%s)",
                book_data.title,
                book_data.author,
            )
            return None

    def _validate_fields(self, year: int | None, pages: int | None) -> None:
        if year is not None:
            self._validate_year(year)
        if pages is not None:
            self._validate_pages(pages)