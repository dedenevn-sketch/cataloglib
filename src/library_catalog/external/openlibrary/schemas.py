"""Pydantic-схемы ответов Open Library."""

from pydantic import BaseModel, ConfigDict, Field


class OpenLibrarySearchDoc(BaseModel):
    """Документ из поиска Open Library (/search.json -> docs[])."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    title: str
    author_name: list[str] | None = None
    cover_i: int | None = None
    subject: list[str] | None = None
    publisher: list[str] | None = None
    language: list[str] | None = None
    ratings_average: float | None = Field(None, alias="ratings_average")


class OpenLibrarySearchResponse(BaseModel):
    """Ответ эндпоинта /search.json."""

    model_config = ConfigDict(extra="ignore")

    numFound: int = 0
    docs: list[OpenLibrarySearchDoc] = []
