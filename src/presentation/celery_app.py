import os
from celery import Celery

# Адрес Redis берем из переменных окружения.
# Значение по умолчанию подходит для локального запуска,
# в Docker Compose оно будет переопределено на 'redis://broker:6379/0'
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "document_classifier",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.presentation.tasks"]  # Указываем модуль, где будут лежать задачи
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
