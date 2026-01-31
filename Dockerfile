FROM python:3.11-slim

# Ставим рабочую директорию
WORKDIR /app

# Копируем требования из подпапки и устанавливаем их
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Создаем __init__.py на всякий случай
RUN touch backend/__init__.py

# Переходим в backend для запуска
WORKDIR /app/backend

# Запускаем сервер
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}