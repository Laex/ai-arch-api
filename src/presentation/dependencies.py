import os
import mlflow
from functools import lru_cache
from fastapi import Depends
from src.infrastructure.onnx_model import ONNXDocumentClassifier
from src.application.services import DocumentRoutingService

# Подключение к MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

@lru_cache(maxsize=1)
def get_model():
    """
    Загружает модель в память (Singleton).
    Используется lru_cache, чтобы не создавать объект модели заново на каждый запрос.
    """
    model_name = "document_classifier"
    model_alias = "production"
    model_uri = f"models:/{model_name}@{model_alias}"
    
    print(f"[Model] Загрузка модели из MLflow Registry ({model_uri})...")
    try:
        # MLflow автоматически найдет версию модели с указанным псевдонимом (alias) и скачает её
        model_dir = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)
        model_path = os.path.join(model_dir, "model.onnx")
    except Exception as e:
        print(f"[Model] Ошибка MLflow: {e}. Загрузка локальной копии...")
        model_path = "models/classifier.onnx"
        
    return ONNXDocumentClassifier(model_path)

def get_service(classifier: ONNXDocumentClassifier = Depends(get_model)) -> DocumentRoutingService:
    """
    DI-провайдер для сервиса бизнес-логики.
    FastAPI автоматически внедрит сюда результат get_model.
    """
    # Здесь происходит сборка (Composition Root) для каждого запроса,
    # но тяжелый объект модели (classifier) создается только один раз благодаря lru_cache
    return DocumentRoutingService(classifier=classifier)
