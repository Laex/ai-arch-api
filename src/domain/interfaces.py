"""
Модуль интерфейсов (Interfaces) слоя Domain.

Этот файл определяет абстрактные базовые классы, которые задают контракт
поведения для компонентов системы. Слой Application зависит от этих интерфейсов,
а слой Infrastructure реализует их (принцип инверсии зависимостей).
"""
from abc import ABC, abstractmethod
from src.domain.entities import DocumentText, DocCategory

class IDocumentClassifier(ABC):
    """
    Абстрактный интерфейс классификатора документов.
    """
    
    @abstractmethod
    def classify(self, doc: DocumentText) -> DocCategory:
        """
        Классифицировать документ.
        """
        pass

class IDataStorage(ABC):
    """
    Абстрактный интерфейс для работы с объектным хранилищем.
    """
    
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> None:
        """Скачать файл из облака в локальную файловую систему."""
        pass

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> None:
        """Загрузить локальный файл в облако."""
        pass