from src.presentation.celery_app import celery_app
from src.presentation.dependencies import get_service, get_model

@celery_app.task(name="predict_task")
def predict_task(filename: str, content: str):
    """
    Асинхронная задача Celery для классификации документа.
    
    Args:
        filename (str): Имя файла.
        content (str): Текст документа.
    """
    # 1. Получаем модель и сервис.
    # Вне контекста FastAPI (Depends) мы должны явно разрешить зависимости.
    # get_model() вернет закешированный синглтон модели.
    classifier = get_model()
    service = get_service(classifier=classifier)
    
    # 2. Выполняем бизнес-логику (инференс)
    result = service.run(filename=filename, raw_content=content)
    
    # 3. Возвращаем результат.
    # Сериализуем Pydantic-модель в словарь, чтобы Celery мог передать его через Redis.
    return result.model_dump()
