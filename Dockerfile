# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем необходимые системные библиотеки для psycopg2 (если они требуются)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменные окружения для базы данных
ENV DB_HOST=localhost \
    DB_PORT=5439 \
    DB_USER=postgres \
    DB_PASS=123456 \
    DB_NAME=postgres

# Копируем все файлы проекта в контейнер
COPY . /deploy

# Устанавливаем рабочую директорию в папку /deploy/app
WORKDIR /deploy/app

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r /deploy/requirements.txt

# Команда для запуска FastAPI
