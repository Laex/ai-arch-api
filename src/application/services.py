"""
Модуль сервисов (Services) слоя Application.

Этот слой реализует сценарии использования (Use Cases) системы.
Сервисы отвечают за оркестрацию потока данных: они получают данные из
Presentation слоя, валидируют их через Domain сущности и передают
в Infrastructure через абстрактные интерфейсы.
"""
from pathlib import Path
from src.domain.interfaces import IDocumentClassifier, IDataStorage
from src.domain.entities import DocumentText, DocCategory

class DocumentRoutingService:
    """
    Сервис (Use Case) для маршрутизации документов.
    """

    def __init__(self, classifier: IDocumentClassifier):
        """
        Инициализация сервиса с внедрением зависимостей.
        """
        self.classifier = classifier

    def preprocess(self, text: str) -> str:
        """
        Обрезает текст до 1000 символов для оптимизации.
        """
        return text[:1000]

    def run(self, filename: str, raw_content: str) -> DocCategory:
        """
        Выполнение бизнес-сценария классификации.
        """
        # 1. Предобработка
        clean_content = self.preprocess(raw_content)

        # 2. Создание сущности
        doc = DocumentText(filename=filename, content=clean_content)
        
        # 3. Вызов модели
        return self.classifier.classify(doc)

class DataSyncService:
    """
    Сервис (Use Case) для синхронизации локальных данных с облаком.
    
    Этот компонент отвечает за то, чтобы перед началом работы модели
    необходимые данные (веса, датасеты) гарантированно находились на диске.
    Он использует абстракцию IDataStorage, поэтому не знает, откуда именно
    качаются данные (S3, FTP, Google Drive).
    """
    
    def __init__(self, storage: IDataStorage):
        """
        Инициализация сервиса.
        
        Args:
            storage (IDataStorage): Объект, реализующий интерфейс хранилища.
                                    Сюда передается конкретная реализация (например, S3Storage),
                                    но сервис работает с ней только через методы интерфейса.
        """
        # Инверсия зависимостей: мы зависим от интерфейса, а не от реализации
        self.storage = storage

    def sync_dataset(self, remote_path: str, local_path: str) -> None:
        """
        Проверяет наличие локального файла и скачивает его при отсутствии.
        
        Это обеспечивает идемпотентность: повторный запуск не приведет к
        лишним скачиваниям, если данные уже на месте.
        """
        local_file = Path(local_path)
        
        if not local_file.exists():
            print(f"[Sync] Файл {local_path} не найден. Запрашиваю синхронизацию...")
            
            # Создаем родительские папки, если их нет (например, data/docs/)
            # exist_ok=True позволяет не падать с ошибкой, если папка уже есть
            local_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Скачиваем данные через абстрактное хранилище
            self.storage.download_file(remote_path, local_path)
        else:
            print(f"[Sync] Файл {local_path} уже существует. Пропускаю.")