"""
Модуль сервисов (Services) слоя Application.

Этот слой реализует сценарии использования (Use Cases) системы.
Сервисы отвечают за оркестрацию потока данных: они получают данные из
Presentation слоя, валидируют их через Domain сущности и передают
в Infrastructure через абстрактные интерфейсы.
"""
from src.domain.interfaces import IDocumentClassifier
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
