"""
Модуль интерфейса командной строки (CLI) слоя Presentation.

Этот слой отвечает за взаимодействие с внешним миром (пользователем).
Его задачи:
1. Принять ввод от пользователя (аргументы командной строки).
2. Собрать приложение (Composition Root): инициализировать инфраструктуру и внедрить её в бизнес-логику.
3. Запустить сценарий использования (Use Case).
4. Вывести результат в понятном пользователю формате.
"""
import sys
import os
from src.infrastructure.models import KeywordClassifier
from src.infrastructure.storage import S3Storage
from src.application.services import DocumentRoutingService, DataSyncService

def main():
    """
    Точка входа в приложение.
    
    Здесь происходит сборка зависимостей (Dependency Injection).
    Слой Presentation знает обо всех остальных слоях, чтобы соединить их вместе.
    """
    # --- 0. Конфигурация (обычно берется из .env) ---
    s3_config = {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        "bucket": os.getenv("MINIO_BUCKET", "datasets")
    }

    # --- 1. Инициализация инфраструктуры (Composition Root) ---
    
    # 1.1 Инициализация хранилища
    storage = S3Storage(**s3_config)
    
    # 1.2 Инициализация модели
    # Здесь мы выбираем конкретную реализацию модели.
    classifier = KeywordClassifier()
    
    # --- 2. Инициализация бизнес-логики (Dependency Injection) ---
    
    # 2.1 Сервис синхронизации данных
    sync_service = DataSyncService(storage=storage)
    
    # 2.2 Сервис маршрутизации документов
    # Сервис получает готовую модель, не зная, как она устроена внутри.
    service = DocumentRoutingService(classifier=classifier)
    
    # --- 3. Подготовка данных (Синхронизация) ---
    # Скачиваем файл, необходимый для демонстрации (если его нет локально)
    # Примечание: В MinIO файл должен лежать по пути 'demo/test_invoice.txt'
    try:
        sync_service.sync_dataset(
            remote_path="demo/test_invoice.txt", 
            local_path="data/docs/invoices/test_invoice.txt"
        )
    except Exception as e:
        print(f"[Warning] Не удалось синхронизировать данные: {e}")
        print("Продолжаем работу с локальными файлами...")

    # --- 4. Взаимодействие с пользователем ---
    # Получение данных из внешнего мира (аргументы CLI)
    input_text = "Hello World"
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        
    print(f"Running inference on: '{input_text}'")
    
    # --- 5. Запуск основного сценария использования ---
    # Для CLI используем фиктивное имя файла
    result = service.run(filename="cli_input.txt", raw_content=input_text)
    
    # --- 6. Вывод результата ---
    print(f"Result: {result.label} (Confidence: {result.confidence})")

if __name__ == "__main__":
    main()