# 📚 Library Catalog API

REST API для управления библиотечным каталогом на **FastAPI** с правильной
многослойной архитектурой (API → Domain → Data → External), async **SQLAlchemy 2.0**,
**PostgreSQL**, миграциями **Alembic** и обогащением данных из **Open Library**.

## Архитектура

```
src/library_catalog/
├── api/        # API Layer: роутеры, схемы, DI-контейнер
├── domain/     # Domain Layer: сервисы, бизнес-правила, исключения, мапперы
├── data/       # Data Layer: ORM-модели, репозитории (Repository Pattern)
├── external/   # External Layer: HTTP-клиент Open Library с retry-логикой
└── core/       # config, database, exceptions, logging
```

Принцип: бизнес-логика только в сервисах, SQL только в репозиториях,
роутеры тонкие, зависимости внедряются через `Depends`.

## Быстрый старт

```bash
docker compose up --build
docker compose exec web poetry run alembic upgrade head
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/api/v1/health/

## Эндпоинты

| Метод  | Путь                     | Описание                          |
|--------|--------------------------|-----------------------------------|
| POST   | `/api/v1/books/`         | Создать книгу (+ обогащение OL)   |
| GET    | `/api/v1/books/`         | Список книг (фильтры + пагинация) |
| GET    | `/api/v1/books/{id}`     | Получить книгу по ID              |
| PATCH  | `/api/v1/books/{id}`     | Частичное обновление              |
| DELETE | `/api/v1/books/{id}`     | Удалить книгу                     |
| GET    | `/api/v1/health/`        | Health check                      |

Фильтры списка: `title`, `author` (частичное совпадение), `genre`, `year`,
`available`; пагинация: `page`, `page_size` (1–100).

## Тесты

```bash
# Unit (сервис) + интеграционные (API через ASGITransport) — БД не нужна
pytest tests/unit/test_services tests/integration -q

# Тесты репозитория (нужна тестовая PostgreSQL)
export TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/library_test
pytest tests/unit/test_repositories -q
```

> Для импорта приложения требуется переменная `DATABASE_URL` (берётся из `.env`).

## Бизнес-правила

- Год издания: 1000 ≤ year ≤ текущий год.
- Количество страниц > 0.
- ISBN уникален (если указан), валидный формат (10 или 13 цифр).
- Обогащение из Open Library не прерывает создание книги при сбое API.
