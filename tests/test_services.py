"""
Модуль модульного тестирования (Unit Testing) слоя Application.

Здесь мы проверяем бизнес-логику изолированно от внешних зависимостей (баз данных, нейросетей).
Для этого используются Mock-объекты, которые имитируют поведение реальных компонентов.
"""
from unittest.mock import Mock
from src.domain.entities import DocumentText, DocCategory
from src.domain.interfaces import IDocumentClassifier
from src.application.services import DocumentRoutingService

def test_document_routing_service_logic():
    """
    Тест проверяет корректность работы Use Case (DocumentRoutingService).
    
    Сценарий:
    1. На вход подается длинная строка.
    2. Сервис должен обрезать строку до 1000 символов.
    3. Сервис должен сформировать правильную сущность DocumentText.
    4. Сервис должен вызвать модель и вернуть её результат.
    """
    # --- 1. Arrange (Подготовка окружения) ---
    mock_classifier = Mock(spec=IDocumentClassifier)
    
    expected_result = DocCategory(label="Invoice", confidence=0.99)
    mock_classifier.classify.return_value = expected_result
    
    service = DocumentRoutingService(classifier=mock_classifier)
    
    # --- 2. Act (Выполнение действия) ---
    # Генерируем строку длиной 1005 символов
    long_input = "a" * 1005
    filename = "test.txt"
    result = service.run(filename, long_input)
    
    # --- 3. Assert (Проверка результатов) ---
    assert result == expected_result
    
    mock_classifier.classify.assert_called_once()
    
    call_args = mock_classifier.classify.call_args
    passed_doc = call_args[0][0]
    
    assert isinstance(passed_doc, DocumentText)
    assert passed_doc.filename == filename
    
    # Проверяем логику preprocess (обрезка до 1000 символов)
    assert len(passed_doc.content) == 1000
    assert passed_doc.content == "a" * 1000
