# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем необходимые системные библиотеки для psycopg2 (если они требуются)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


ENV DB_HOST=localhost
ENV DB_PORT=5439
ENV DB_USER=postgres
ENV DB_PASS=123456
ENV DB_NAME=postgres
# Копируем все файлы проекта в контейнер
COPY . /deploy

# Устанавливаем рабочую директорию в папку /deploy/app
WORKDIR /deploy/app

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r /deploy/requirements.txt

# Устанавливаем переменную окружения для порта (по умолчанию 8000)
ENV PORT 8000

# Команда для запуска FastAPI с uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
