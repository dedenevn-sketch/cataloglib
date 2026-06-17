"""Репозиторий для работы с книгами."""

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from ...utils.helpers import clean_isbn
from ..models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """CRUD и поиск книг."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    def _apply_filters(
        self,
        stmt: Select,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> Select:
        """Применить фильтры к запросу, пропуская None-значения."""
        if title is not None:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))
        if author is not None:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))
        if genre is not None:
            stmt = stmt.where(Book.genre.ilike(f"%{genre}%"))
        if year is not None:
            stmt = stmt.where(Book.year == year)
        if available is not None:
            stmt = stmt.where(Book.available == available)
        return stmt

    async def find_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]:
        """Поиск книг с фильтрацией и пагинацией."""
        stmt = select(Book)
        stmt = self._apply_filters(stmt, title, author, genre, year, available)
        stmt = stmt.order_by(Book.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Найти книгу по ISBN."""
        stmt = select(Book).where(Book.isbn == clean_isbn(isbn))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_filters(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
    ) -> int:
        """Подсчитать количество книг по тем же фильтрам (для пагинации)."""
        stmt = select(func.count()).select_from(Book)
        stmt = self._apply_filters(stmt, title, author, genre, year, available)
        result = await self.session.execute(stmt)
        return result.scalar_one()


    async def update_instance(self, instance: Book, **kwargs) -> Book:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance