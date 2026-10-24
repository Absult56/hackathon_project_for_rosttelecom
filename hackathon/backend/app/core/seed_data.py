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

    # 3. Загрузка сделок-бенчмарок из фикстур Data Engineer
    benchmarks = [BenchmarkDeal(**item) for item in payload.get("benchmarks", [])]
    db.add_all(benchmarks)

    db.commit()
    print("[+] Сидирование завершено: таблицы заполнены!")