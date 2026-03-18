"""
Модуль API (Presentation Layer) на базе FastAPI.

Этот модуль отвечает за обработку HTTP-запросов. Он является точкой входа
для внешних систем (веб-фронтенд, мобильные приложения, другие сервисы).
Здесь происходит преобразование HTTP-запросов в вызовы бизнес-логики (Application Layer).
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from src.presentation.dependencies import get_model
from src.presentation.tasks import predict_task
from src.presentation.celery_app import celery_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    События жизненного цикла приложения (Lifespan Events).
    
    Этот менеджер контекста позволяет выполнять код:
    1. При запуске приложения (до начала обработки запросов) - блок до yield.
    2. При остановке приложения - блок после yield.
    
    Здесь мы используем это для предварительной загрузки модели в память,
    чтобы она скачалась из MLflow до того, как придет первый пользовательский запрос.
    """
    print("[Startup] Инициализация приложения...")
    try:
        # Предзагрузка модели в память, чтобы первый запрос не тормозил
        get_model()
    except Exception as e:
        print(f"[Startup Error] Ошибка инициализации: {e}")
    
    yield
    # --- 2. Shutdown (Очистка ресурсов) ---
    # Здесь можно закрыть соединения с БД или остановить фоновые задачи.
    print("[Shutdown] Остановка сервера...")

app = FastAPI(title="Document Classifier API", lifespan=lifespan)

# DTO (Data Transfer Object) для запроса
class DocumentRequest(BaseModel):
    """
    Модель данных для входящего JSON-запроса.
    FastAPI использует её для валидации входных данных.
    """
    filename: str
    content: str

class TaskResponse(BaseModel):
    task_id: str

@app.get("/")
def root():
    """
    Проверка работоспособности API (Health Check).
    Используется системами мониторинга (k8s probes) для проверки статуса сервиса.
    """
    return {"message": "API is running. Go to /docs to test the classifier."}

@app.get("/classify")
def classify_info():
    """
    Подсказка, если пользователь случайно открыл этот адрес в браузере (GET-запрос).
    Браузеры по умолчанию делают GET, а наш метод требует POST.
    """
    return {"message": "GET method not allowed. Please use POST request with JSON body to classify documents. Check /docs for details."}

@app.post("/classify", response_model=TaskResponse, status_code=202)
def classify_document(request: DocumentRequest):
    """
    Эндпоинт для классификации документа (Асинхронный).
    
    Принимает JSON с текстом документа, создает задачу в Celery и возвращает ID задачи.
    """
    # 1. Отправка задачи в очередь (Redis)
    task = predict_task.delay(
        filename=request.filename,
        content=request.content
    )
    
    # 2. Возврат ID задачи клиенту
    return {"task_id": task.id}

@app.get("/classify/result/{task_id}")
def get_task_result(task_id: str):
    """
    Эндпоинт для проверки статуса задачи и получения результата.
    """
    task_result = celery_app.AsyncResult(task_id)
    
    if task_result.ready():
        if task_result.successful():
            return {
                "task_id": task_id,
                "status": "SUCCESS",
                "result": task_result.get()
            }
        return {
            "task_id": task_id,
            "status": "FAILURE",
            "error": str(task_result.result)
        }
    
    return {"task_id": task_id, "status": task_result.status}