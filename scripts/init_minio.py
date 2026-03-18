import boto3
import os
from botocore.exceptions import ClientError

def init_minio():
    """
    Инициализирует бакеты MinIO и загружает тестовые данные.
    
    Этот скрипт подготавливает инфраструктуру хранения данных для работы приложения.
    Он создает необходимые бакеты (папки верхнего уровня в S3) и загружает
    демонстрационный файл, чтобы API могло проверить синхронизацию при первом запуске.
    """
    # Настройки подключения.
    # Мы используем переменные окружения для гибкости (12 Factor App),
    # но предоставляем значения по умолчанию для локальной разработки (Docker Compose).
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"), # Адрес локального MinIO
        aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),     # Логин
        aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin")  # Пароль
    )
    
    # Список бакетов, которые должны существовать в системе:
    # 1. datasets - для хранения сырых данных и датасетов.
    # 2. models - для хранения версионированных ML-моделей (ONNX).
    buckets = [os.getenv("MINIO_BUCKET", "datasets"), "models"]
    
    print(f"Подключение к MinIO по адресу {s3.meta.endpoint_url}...")

    # Проходим по всем бакетам и создаем их, если они не существуют
    for bucket_name in buckets:
        try:
            # head_bucket - дешевая операция проверки существования и прав доступа
            s3.head_bucket(Bucket=bucket_name)
            print(f"Бакет '{bucket_name}' уже существует.")
        except ClientError:
            # Если бакет не найден (404), создаем его
            print(f"Создание бакета '{bucket_name}'...")
            s3.create_bucket(Bucket=bucket_name)

    # Загрузка демо-данных для проверки работы DataSyncService
    # Это позволяет запустить API сразу после инициализации, не настраивая DVC вручную.
    bucket = buckets[0]
    key = "demo/test_invoice.txt" # Путь внутри бакета (S3 Key)
    content = "Тестовый счет для проверки синхронизации API. Сумма: 1000 руб."
    
    print(f"Загрузка файла '{key}' в бакет '{bucket}'...")
    # put_object загружает данные напрямую из строки или байтов
    s3.put_object(Bucket=bucket, Key=key, Body=content)
    print("Инициализация MinIO завершена.")

if __name__ == "__main__":
    init_minio()