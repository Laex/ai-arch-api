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
