import json
import os
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.invest_project import InvestProject
from app.models.benchmark import BenchmarkDeal

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../data/initial_data.json")

def seed_database(db: Session):
    """Инициализация БД тестовыми данными из JSON-файла Data Engineer."""
    # Если данные уже есть, повторно не заливаем
    if db.query(Company).first() is not None:
        print("[*] База данных уже содержит записи. Сидирование пропущено.")
        return

    if not os.path.exists(DATA_FILE_PATH):
        print(f"[!] Файл фикстур {DATA_FILE_PATH} не найден.")
        return

    print("[*] Загрузка фикстур в БД...")
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # 1. Загрузка компаний
    companies = [Company(**item) for item in payload.get("companies", [])]
    db.add_all(companies)

    # 2. Загрузка инвестпроектов
    projects = [InvestProject(**item) for item in payload.get("projects", [])]
    db.add_all(projects)

    # 3. Дефолтные ретро-сделки для калькулятора
    benchmarks = [
        BenchmarkDeal(title="Офис Альфа 500 кв.м", industry="Финансы", scale=500.0, final_price=1200000.0, margin=30.0),
        BenchmarkDeal(title="Складской комплекс 3000 кв.м", industry="Логистика", scale=3000.0, final_price=4800000.0, margin=25.5),
        BenchmarkDeal(title="Агроферма Вологда 1500 кв.м", industry="АПК", scale=1500.0, final_price=2300000.0, margin=22.0),
    ]
    db.add_all(benchmarks)

    db.commit()
    print("[+] Сидирование завершено: таблицы заполнены!")