# Используем официальный образ Python
FROM python:3.12-slim

# Копируем все файлы проекта в контейнер
COPY . .

RUN pip install -r requirements.txt

# Команда для запуска FastAPI с uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
