
# Используем официальный образ Python:3.10-slim
FROM python:3.10-slim

# Отключаем создание .pyc файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для сборки (например, build-essential и curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip install --upgrade pip

# Устанавливаем Poetry
RUN pip install poetry

# Настраиваем Poetry так, чтобы он устанавливал зависимости прямо в системное окружение, а не создавал виртуальное окружение
RUN poetry config virtualenvs.create false

# Копируем файлы управления зависимостями (pyproject.toml и, если он есть, poetry.lock)
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости через Poetry
RUN poetry install --no-interaction --no-ansi

# Копируем оставшиеся исходные файлы проекта
COPY . .

# Открываем порт (например, uvicorn по умолчанию слушает порт 8000)
EXPOSE 8000

# Указываем команду для запуска FastAPI-приложения через uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
