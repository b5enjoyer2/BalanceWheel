# Используем официальный образ Python
FROM python:3.12-slim

# Копируем все файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости из requirements.txt
RUN pip install -r requirements.txt

# Устанавливаем переменную окружения для порта (по умолчанию 8000)
ENV PORT 8000

# Команда для запуска FastAPI с uvicorn, используя переменную окружения PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
