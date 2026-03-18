"""
Модуль интерфейса командной строки (CLI) слоя Presentation.

Этот слой отвечает за взаимодействие с внешним миром (пользователем).
Его задачи:
1. Принять ввод от пользователя (аргументы командной строки).
2. Собрать приложение (Composition Root): инициализировать инфраструктуру и внедрить её в бизнес-логику.
3. Запустить сценарий использования (Use Case).
4. Вывести результат в понятном пользователю формате.
"""
import sys
from src.presentation.dependencies import get_model, get_service

def main():
    """
    Точка входа в приложение.
    
    Здесь происходит сборка зависимостей (Dependency Injection).
    Слой Presentation знает обо всех остальных слоях, чтобы соединить их вместе.
    """
    # --- 1. Инициализация (Composition Root) ---
    print("[CLI] Инициализация сервисов и загрузка модели...")
    classifier = get_model()
    service = get_service(classifier=classifier)
    
    # --- 2. Взаимодействие с пользователем ---
    # Получение данных из внешнего мира (аргументы CLI)
    input_text = "Hello World"
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        
    print(f"Running inference on: '{input_text}'")
    
    # --- 3. Запуск основного сценария использования ---
    # Для CLI используем фиктивное имя файла
    result = service.run(filename="cli_input.txt", raw_content=input_text)
    
    # --- 4. Вывод результата ---
    print(f"Result: {result.label} (Confidence: {result.confidence})")

if __name__ == "__main__":
    main()