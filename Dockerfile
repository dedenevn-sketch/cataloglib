# Используем официальный стабильный образ Python 3.12
FROM python:3.12-slim

# Устанавливаем системные утилиты для сборки некоторых Python-пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем конкретную стабильную версию Poetry
ENV POETRY_VERSION=1.8.3
RUN pip install "poetry==$POETRY_VERSION"

# Говорим Poetry не создавать виртуальное окружение внутри контейнера,
# так как сам контейнер уже является изолированной средой
RUN poetry config virtualenvs.create false

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* /app/

# Устанавливаем все зависимости через Poetry внутри контейнера
RUN poetry install --no-interaction --no-ansi

# Копируем весь остальной код проекта в контейнер
COPY . /app/

# Открываем порт 8000 для FastAPI
EXPOSE 8000

# Команда для запуска приложения с автоперезагрузкой при изменении кода
CMD ["uvicorn", "src.library_catalog.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]