# Лабораторные работы №1-4: MLOps пайплайн и асинхронный инференс

Проект представляет собой архитектурный фундамент ИИ-системы (Классификатор документов), построенный на принципах **Clean Architecture**. 
Реализован полный цикл MLOps в миниатюре:
1. **ЛР №1**: Скелет приложения и разделение на слои.
2. **ЛР №2**: Управление данными (Data-as-Code) через DVC и MinIO.
3. **ЛР №3**: Обучение модели, конвертация в ONNX и реализация инференс-сервиса (Model-as-Code).
4. **ЛР №4**: Асинхронная обработка задач с очередью (Celery + Redis) и полная контейнеризация (Docker Compose).

## Стек технологий
* **Python 3.11+**
* **Poetry**: Управление зависимостями и виртуальным окружением.
* **FastAPI**: Веб-интерфейс API (Presentation Layer).
* **Celery**: Распределенная очередь задач.
* **Redis**: Брокер сообщений и хранилище результатов.
* **ONNX Runtime**: Высокопроизводительный движок для запуска моделей.
* **Scikit-learn**: Обучение ML-моделей.
* **Docker & Docker Compose**: Оркестрация сервисов (API, Worker, Broker, Storage).
* **DVC (Data Version Control)**: Управление версиями данных и моделей.
* **Boto3**: Работа с S3-хранилищем.

## Структура проекта
Проект организован в 4 слоя согласно Clean Architecture:

1. **`src/domain`** (Ядро системы)
   - Сущности (`DocumentText`, `DocCategory`) и интерфейсы.
   - **Правило:** Не имеет внешних зависимостей.

2. **`src/application`** (Бизнес-логика)
   - `DocumentRoutingService`: сценарий классификации документов.
   - `DataSyncService`: сценарий синхронизации данных и моделей с облаком.

3. **`src/infrastructure`** (Реализация)
   - `ONNXDocumentClassifier`: адаптер для запуска ONNX-моделей.
   - `S3Storage`: адаптер для работы с MinIO через `boto3`.

4. **`src/presentation`** (Взаимодействие)
   - `api.py`: Асинхронный REST API (отправляет задачи в Celery).
   - `celery_app.py`: Конфигурация приложения Celery.
   - `tasks.py`: Определение фоновых задач (инференс модели).

## Утилиты (Scripts)
В папке `scripts/` находятся вспомогательные скрипты для управления жизненным циклом проекта:
* **`init_minio.py`**: Инициализация объектного хранилища. Создает бакеты `datasets` и `models`, загружает демо-данные для проверки синхронизации.
* **`train_model.py`**: Пайплайн обучения. Загружает данные, обучает модель (TF-IDF + Logistic Regression), конвертирует её в формат ONNX и сохраняет в папку `models/`.

## Развертывание и запуск

### 1. Подготовка окружения
   ```bash
   poetry install
   ```

### 2. Запуск системы (Docker Compose)
   Запуск полного стека: API, Worker, Redis, MinIO.
   ```bash
   docker-compose up --build -d
   ```
   * **API**: http://localhost:8000
   Консоль управления: http://localhost:9001 (login: `minioadmin`, pass: `minioadmin`).

### 3. Инициализация и обучение модели
   Инициализация бакетов (`datasets`, `models`) и загрузка демо-данных:
   ```bash
   poetry run python scripts/init_minio.py
   ```

   Обучение модели (TF-IDF + Logistic Regression) и конвертация в ONNX:
   ```bash
   poetry run python scripts/train_model.py
   ```
   Скрипт создаст файл `models/classifier.onnx`.

### 4. Настройка DVC (Версионирование)
   Настройка удаленного хранилища для моделей (если еще не настроено):
   ```bash
   # Добавляем remote для бакета models
   poetry run dvc remote add -d models_storage s3://models
   poetry run dvc remote modify models_storage endpointurl http://localhost:9000
   poetry run dvc remote modify minio access_key_id minioadmin
   poetry run dvc remote modify minio secret_access_key minioadmin
   
   # Версионируем модель
   poetry run dvc add models/classifier.onnx
   poetry run dvc push -r models_storage
   ```

### 5. Тестирование API
   
   **1. Отправка задачи (POST):**
   ```bash
   curl -X 'POST' \
     'http://localhost:8000/classify' \
     -H 'Content-Type: application/json' \
     -d '{
     "filename": "contract_123.txt",
     "content": "Договор аренды помещения №45 от 12.01.2024. Стороны пришли к соглашению..."
   }'
   ```
   **Ответ:** `{"task_id": "..."}`
   
   **2. Получение результата (GET):**
   ```bash
   curl 'http://localhost:8000/classify/result/{task_id}'
   ```
   
   **3. Автоматический тест (Polling):**
   ```bash
   poetry run python scripts/test_async.py
   ```
   
   Документация Swagger: http://localhost:8000/docs

## Конфигурация
Параметры подключения можно переопределить через переменные окружения (или `.env` файл):
* `MINIO_ENDPOINT` (default: http://localhost:9000)
* `MINIO_ACCESS_KEY` (default: minioadmin)
* `MINIO_SECRET_KEY` (default: minioadmin)
* `MINIO_BUCKET` (default: datasets)
