"""Небольшие вспомогательные функции."""


def clean_isbn(isbn: str | None) -> str | None:
    """Убрать дефисы и пробелы из ISBN."""
    if isbn is None:
        return None
    return isbn.replace("-", "").replace(" ", "").strip()
