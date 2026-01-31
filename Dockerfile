FROM python:3.11-slim

# Ставим рабочую директорию
WORKDIR /app

# Копируем требования из подпапки и устанавливаем их
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

ENV PYTHONPATH=/app/backend

# Запускаем через путь к модулю
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]