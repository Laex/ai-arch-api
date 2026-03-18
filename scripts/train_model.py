import os
import mlflow
import mlflow.onnx
from mlflow.tracking import MlflowClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import StringTensorType

# Настройка подключения к MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("Document Classification")

def train():
    # Оборачиваем логику в запуск MLflow
    with mlflow.start_run() as run:
        # 1. Подготовка данных
        X = [
            "Счет на оплату услуг №123", 
            "Оплата по договору", 
            "Сумма к оплате 500р", 
            "Выставить счет фактуру",
            "Договор аренды помещения", 
            "Соглашение о конфиденциальности", 
            "Подписи сторон",
            "Дополнительное соглашение к договору"
        ]
        y = ["invoice", "invoice", "invoice", "invoice", "contract", "contract", "contract", "contract"]

        # 2. Создание и обучение пайплайна
        params = {"tfidf__max_features": 100, "clf__C": 1.0}
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=params["tfidf__max_features"])),
            ('clf', LogisticRegression(C=params["clf__C"]))
        ])

        print("Обучение модели...")
        pipeline.fit(X, y)

        # Логируем параметры и метрики в MLflow
        mlflow.log_params(params)
        accuracy = pipeline.score(X, y)
        mlflow.log_metric("accuracy", accuracy)

        # Тестовое предсказание
        test_text = "Прошу оплатить счет"
        print(f"Тест: '{test_text}' -> {pipeline.predict([test_text])[0]}")

        # 3. Конвертация в ONNX
        initial_type = [('input_text', StringTensorType([None, 1]))]
        print("Конвертация в ONNX...")
        onnx_model = convert_sklearn(pipeline, initial_types=initial_type)

        # 4. Сохранение (логирование) модели в MLflow Model Registry
        print("Логирование модели в MLflow...")
        model_info = mlflow.onnx.log_model(
            onnx_model,
            artifact_path="model",
            registered_model_name="document_classifier"
        )

        # 5. Автоматическое назначение алиаса production
        print("Назначение алиаса 'production'...")
        client = MlflowClient()
        client.set_registered_model_alias(
            name="document_classifier",
            alias="production",
            version=model_info.registered_model_version
        )
        print(f"Алиас 'production' успешно назначен версии {model_info.registered_model_version}!")

        print(f"Обучение завершено. Модель залогирована в MLflow! Run ID: {run.info.run_id}")

if __name__ == "__main__":
    train()
