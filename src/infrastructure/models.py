"""
Модуль реализации моделей (Infrastructure) слоя.

Этот слой содержит конкретные реализации интерфейсов, определенных в слое Domain.
Здесь находится код, который взаимодействует с внешними библиотеками (например,
TensorFlow, PyTorch, Scikit-learn) или имитирует их работу (Mock).
"""
from src.domain.interfaces import IDocumentClassifier
from src.domain.entities import DocumentText, DocCategory

class KeywordClassifier(IDocumentClassifier):
    """
    Реализация классификатора на основе ключевых слов (Infrastructure).
    """

    def classify(self, doc: DocumentText) -> DocCategory:
        """
        Простая эвристика для определения типа документа.
        """
        text = doc.content.lower()
        
        if "счет" in text or "оплата" in text:
            return DocCategory(label="Invoice", confidence=0.95)
        elif "паспорт" in text:
            return DocCategory(label="Identity", confidence=0.99)
        else:
            return DocCategory(label="Other", confidence=0.50)