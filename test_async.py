import time
import sys
import httpx  # Используем httpx, так как он есть в dev-зависимостях

# Адрес API (убедитесь, что порт совпадает с docker-compose)
API_URL = "http://localhost:8000"

def main():
    print("=== Тестирование асинхронного API классификации ===")
    
    # 1. Подготовка данных
    payload = {
        "filename": "test_doc.txt",
        "content": "Счет на оплату №123. Прошу оплатить услуги по договору..."
    }
    print(f"[Client] Отправляем документ: {payload['content'][:30]}...")

    try:
        # 2. Отправка задачи (POST)
        # Используем таймаут, так как первый запрос может быть долгим из-за прогрева
        response = httpx.post(f"{API_URL}/classify", json=payload, timeout=10.0)
        response.raise_for_status()
        
        data = response.json()
        task_id = data.get("task_id")
        
        if not task_id:
            print("[Error] Не удалось получить task_id")
            sys.exit(1)
            
        print(f"[Client] Задача принята. Task ID: {task_id}")
        
        # 3. Ожидание результата (Polling)
        start_time = time.time()
        while True:
            # Делаем паузу перед проверкой, чтобы не спамить запросами
            time.sleep(1)
            
            # Проверка статуса (GET)
            result_resp = httpx.get(f"{API_URL}/classify/result/{task_id}")
            result_data = result_resp.json()
            
            status = result_data.get("status")
            elapsed = time.time() - start_time
            print(f"[Client] Статус задачи: {status} ({elapsed:.1f}s)")
            
            if status == "SUCCESS":
                print("\n[Client] ✅ Успех! Результат:")
                print(result_data["result"])
                break
            elif status == "FAILURE":
                print("\n[Client] ❌ Ошибка обработки:")
                print(result_data.get("error"))
                break
                
    except Exception as e:
        print(f"\n[Error] Произошла ошибка при выполнении запроса: {e}")

if __name__ == "__main__":
    main()
