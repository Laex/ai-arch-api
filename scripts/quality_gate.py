import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def check_accuracy():
    print("Запуск Quality Gate: проверка базовой метрики модели...")
    
    # 1. Подготовка данных для тестирования (аналогичные обучающим)
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

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=100)),
        ('clf', LogisticRegression(C=1.0))
    ])
    pipeline.fit(X, y)
    
    accuracy = pipeline.score(X, y)
    print(f"Текущая метрика (accuracy): {accuracy:.2f}")
    
    if accuracy <= 0.90:
        print(f"[Error] Quality gate FAILED: accuracy {accuracy:.2f} не превышает порог 0.90")
        sys.exit(1)
    else:
        print("[Success] Quality gate PASSED!")

if __name__ == "__main__":
    check_accuracy()
