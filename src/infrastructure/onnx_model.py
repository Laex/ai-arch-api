"""
Модуль реализации модели на базе ONNX Runtime (Infrastructure).
"""
import numpy as np
import onnxruntime as ort
from src.domain.interfaces import IDocumentClassifier
from src.domain.entities import DocumentText, DocCategory

class ONNXDocumentClassifier(IDocumentClassifier):
    """
    Реализация классификатора документов, использующая модель в формате ONNX.
    """

    def __init__(self, model_path: str):
        """
        Инициализация сессии ONNX Runtime.
        
        Args:
            model_path (str): Путь к файлу модели (.onnx).
        """
        # Загружаем модель и создаем сессию инференса
        self.session = ort.InferenceSession(model_path)
        
        # Получаем имена входных и выходных узлов графа
        self.input_name = self.session.get_inputs()[0].name
        # Обычно [0] - это label, [1] - probabilities
        self.output_names = [output.name for output in self.session.get_outputs()]

    def classify(self, doc: DocumentText) -> DocCategory:
        """
        Классификация документа с помощью ONNX модели.
        """
        # Подготовка данных: модель ожидает 2D массив строк [[text]]
        # Согласно скрипту обучения: StringTensorType([None, 1])
        input_data = np.array([[doc.content]])

        # Выполнение инференса
        results = self.session.run(self.output_names, {self.input_name: input_data})
        
        predicted_label = results[0][0]
        probabilities = results[1][0]
        
        # Извлекаем уверенность для предсказанного класса
        confidence = probabilities.get(predicted_label, 0.0)

        return DocCategory(label=predicted_label, confidence=float(confidence))
