"""
Модуль сущностей (Entities) слоя Domain.

Этот файл содержит Pydantic-модели, описывающие основные структуры данных системы.
Они обеспечивают строгую типизацию и служат единым контрактом для обмена
данными между слоями Application, Infrastructure и Presentation.
"""
from pydantic import BaseModel as PydanticBaseModel

class DocumentText(PydanticBaseModel):
    """
    Сущность (Entity) текста документа.
    
    Описывает документ, который необходимо классифицировать.
    """
    filename: str
    content: str

class DocCategory(PydanticBaseModel):
    """
    Сущность (Entity) категории документа.
    """
    label: str       # Категория (Invoice, Identity, Other)
    confidence: float