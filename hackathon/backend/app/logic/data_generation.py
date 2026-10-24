"""
Генератор и пайплайн подготовки репрезентативных датасетов ПАО «Ростелеком» (Ростовская область).
Роль 2: Data Engineer & Логика расчетов (Этапы 1, 2, 3, 5, 6).
"""

import csv
import json
import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from app.logic.white_spots import detect_and_mark_white_spots


# ---------------------------------------------------------------------------
# ИНН-генератор (Ростовская область — код ФНС 61)
# ---------------------------------------------------------------------------

ROSTOV_IFNS_CODES = ["6161", "6163", "6164", "6166", "6167", "6168"]


def _inn_checksum(base9: str) -> int:
    weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    return sum(int(d) * w for d, w in zip(base9, weights)) % 11 % 10


def generate_valid_inn(ifns_code: str, serial: int) -> str:
    """Генерирует валидный 10-значный ИНН юрлица Ростовской области."""
    base9 = f"{ifns_code}{serial:05d}"[:9]
    return f"{base9}{_inn_checksum(base9)}"


# ---------------------------------------------------------------------------
# Справочник кластеров/районов Ростовской агломерации
# ---------------------------------------------------------------------------

CLUSTER_ZONES_SPEC: List[Dict[str, Any]] = [
    {
        "zone": "Центр",
        "ifns": "6163",
        "center_lat": 47.2270,
        "center_lon": 39.7185,
        "spread_lat": 0.011,
        "spread_lon": 0.022,
        "client_prob": 0.50,
        "city": "г. Ростов-на-Дону",
        "streets": [
            "ул. Большая Садовая", "ул. Красноармейская", "пр-т Буденновский",
            "пр-т Ворошиловский", "ул. Текучёва", "ул. Максима Горького", "ул. Пушкинская",
        ],
    },
    {
        "zone": "Север",
        "ifns": "6161",
        "center_lat": 47.2880,
        "center_lon": 39.7140,
        "spread_lat": 0.016,
        "spread_lon": 0.024,
        "client_prob": 0.48,
        "city": "г. Ростов-на-Дону",
        "streets": [
            "пр-т Космонавтов", "ул. Вавилова", "ул. Орбитальная",
            "ул. Королёва", "б-р Комарова", "ул. Особенная",
        ],
    },
    {
        "zone": "Запад",
        "ifns": "6168",
        "center_lat": 47.2320,
        "center_lon": 39.6220,
        "spread_lat": 0.018,
        "spread_lon": 0.024,
        "client_prob": 0.48,
        "city": "г. Ростов-на-Дону",
        "streets": [
            "ул. Малиновского", "ул. Доватора", "ул. Таганрогская",
            "пр-т Стачки", "ул. Пескова", "ул. 1-я Машиностроительная",
        ],
    },
    {
        "zone": "Восток",
        "ifns": "6166",
        "center_lat": 47.2580,
        "center_lon": 39.7780,
        "spread_lat": 0.015,
        "spread_lon": 0.022,
        "client_prob": 0.48,
        "city": "г. Ростов-на-Дону",
        "streets": [
            "пр-т Шолохова", "ул. Менжинского", "ул. Троллейбусная",
            "ул. 50-летия Ростсельмаша", "ул. Вятская", "ул. Страны Советов",
        ],
    },
    {
        "zone": "Юг",
        "ifns": "6164",
        "center_lat": 47.1850,
        "center_lon": 39.7150,
        "spread_lat": 0.010,
        "spread_lon": 0.020,
        "client_prob": 0.46,
        "city": "г. Ростов-на-Дону",
        "streets": [
            "ул. 1-я Луговая", "ул. 2-я Луговая", "ул. Пойменная",
            "Восточное шоссе", "ул. Шоссейная",
        ],
    },
    # --- «БЕЛЫЕ ПЯТНА» (0 % покрытия РТК) ---
    {
        "zone": "Порт",
        "ifns": "6167",
        "center_lat": 47.2110,
        "center_lon": 39.7820,
        "spread_lat": 0.009,
        "spread_lon": 0.018,
        "client_prob": 0.0,
        "city": "г. Ростов-на-Дону (Промзона Заречная / Порт)",
        "streets": [
            "ул. Береговая", "ул. Портовая", "ул. 1-я Линия",
            "ул. Чемордачка", "Левобережная промзона",
        ],
    },
    {
        "zone": "Батайск",
        "ifns": "6141",
        "center_lat": 47.1360,
        "center_lon": 39.7480,
        "spread_lat": 0.014,
        "spread_lon": 0.022,
        "client_prob": 0.0,
        "city": "г. Батайск",
        "streets": [
            "ул. Промышленная", "ул. Производственная", "ул. Энгельса",
            "ул. Фермерская", "Самарское шоссе", "ул. Коммунальная",
        ],
    },
    {
        "zone": "Новый Аксай",
        "ifns": "6102",
        "center_lat": 47.2740,
        "center_lon": 39.8650,
        "spread_lat": 0.015,
        "spread_lon": 0.024,
        "client_prob": 0.0,
        "city": "г. Аксай",
        "streets": [
            "пр-т Аксайский", "ул. Новочеркасское шоссе", "ул. Промышленная",
            "ул. Заречная", "ул. Западная", "Индустриальный парк М-4",
        ],
    },
    {
        "zone": "Таганрог-Пром",
        "ifns": "6154",
        "center_lat": 47.2390,
        "center_lon": 38.8950,
        "spread_lat": 0.014,
        "spread_lon": 0.020,
        "client_prob": 0.0,
        "city": "г. Таганрог",
        "streets": [
            "Поляковское шоссе", "ул. Инструментальная", "ул. Котлостроительная",
            "ул. Чехова", "ул. Николаевское шоссе",
        ],
    },
]

WHITE_SPOT_ZONES = {"Порт", "Батайск", "Новый Аксай", "Таганрог-Пром"}


# ---------------------------------------------------------------------------
# Якорные компании (известные крупные игроки Ростовской области)
# ---------------------------------------------------------------------------

ANCHOR_COMPANIES: List[Dict[str, Any]] = [
    {
        "name": "ПАО «Ростовэнерго»",
        "industry": "ТЭК",
        "revenue": 450.0,
        "revenue_growth": 5.5,
        "zone": "Восток",
        "is_rtk_client": True,
    },
    {
        "name": "ООО «Агрокомплекс»",
        "industry": "АПК",
        "revenue": 380.0,
        "revenue_growth": 8.2,
        "zone": "Юг",
        "is_rtk_client": True,
    },
    {
        "name": "ООО «Ростовский морской порт»",
        "industry": "Логистика",
        "revenue": 320.0,
        "revenue_growth": 6.0,
        "zone": "Порт",
        "is_rtk_client": False,
    },
    {
        "name": "ООО «Батайскпром»",
        "industry": "Производство",
        "revenue": 290.0,
        "revenue_growth": 4.1,
        "zone": "Батайск",
        "is_rtk_client": False,
    },
    {
        "name": "ООО «Аксай-агро»",
        "industry": "АПК",
        "revenue": 310.0,
        "revenue_growth": 7.5,
        "zone": "Новый Аксай",
        "is_rtk_client": False,
    },
    {
        "name": "ЗАО «Таганрогский 발전ный завод»",
        "industry": "ТЭК",
        "revenue": 270.0,
        "revenue_growth": 3.8,
        "zone": "Таганрог-Пром",
        "is_rtk_client": False,
    },
    {
        "name": "ООО «Центр-it»",
        "industry": "IT",
        "revenue": 240.0,
        "revenue_growth": 12.0,
        "zone": "Центр",
        "is_rtk_client": True,
    },
    {
        "name": "ООО «Северная торговля»",
        "industry": "Торговля",
        "revenue": 210.0,
        "revenue_growth": 5.0,
        "zone": "Север",
        "is_rtk_client": True,
    },
]

INDUSTRIES = ["ТЭК", "АПК", "Логистика", "Производство", "IT", "Торговля"]
STAGES = ["planning", "construction", "launching"]
TARGET_NEEDS = ["it_infra", "cctv", "asutp", "telephony", "access_control", "wifi"]
WORK_TYPES = ["fiber_optics", "cctv", "it_infra", "asutp", "telephony", "access_control", "wifi"]
OBJECT_TYPES = ["industrial_warehouse", "industrial_facility", "office_center", "agro_complex", "energy_facility"]


# ---------------------------------------------------------------------------
# Генерация компаний (~200 шт.)
# ---------------------------------------------------------------------------

def _random_company(i: int, anchor: Dict[str, Any] | None = None) -> Dict[str, Any]:
    if anchor is not None:
        zone_spec = next(z for z in CLUSTER_ZONES_SPEC if z["zone"] == anchor["zone"])
        lat = round(zone_spec["center_lat"] + random.uniform(-zone_spec["spread_lat"], zone_spec["spread_lat"]), 6)
        lon = round(zone_spec["center_lon"] + random.uniform(-zone_spec["spread_lon"], zone_spec["spread_lon"]), 6)
        street = random.choice(zone_spec["streets"])
        house = random.randint(1, 150)
        return {
            "id": i,
            "name": anchor["name"],
            "inn": generate_valid_inn(zone_spec["ifns"], i),
            "industry": anchor["industry"],
            "revenue": anchor["revenue"],
            "revenue_growth": anchor["revenue_growth"],
            "lat": lat,
            "lon": lon,
            "address": f"{street}, д. {house}, {zone_spec['city']}",
            "cluster_zone": anchor["zone"],
            "is_rtk_client": anchor["is_rtk_client"],
        }

    zone = random.choice(CLUSTER_ZONES_SPEC)
    lat = round(zone["center_lat"] + random.uniform(-zone["spread_lat"], zone["spread_lat"]), 6)
    lon = round(zone["center_lon"] + random.uniform(-zone["spread_lon"], zone["spread_lon"]), 6)
    street = random.choice(zone["streets"])
    house = random.randint(1, 150)
    is_client = random.random() < zone["client_prob"]
    industry = random.choice(INDUSTRIES)
    revenue = round(random.uniform(5, 500), 2)
    growth = round(random.uniform(-5, 25), 2)

    return {
        "id": i,
        "name": f"ООО «{industry}Ресурс {i}»",
        "inn": generate_valid_inn(zone["ifns"], i),
        "industry": industry,
        "revenue": revenue,
        "revenue_growth": growth,
        "lat": lat,
        "lon": lon,
        "address": f"{street}, д. {house}, {zone['city']}",
        "cluster_zone": zone["zone"],
        "is_rtk_client": is_client,
    }


def generate_companies(n: int = 200) -> List[Dict[str, Any]]:
    """Генерирует список компаний с якорными игроками и случайными предприятиями."""
    random.seed(42)
    companies: List[Dict[str, Any]] = []

    for idx, anchor in enumerate(ANCHOR_COMPANIES, start=1):
        companies.append(_random_company(idx, anchor))

    next_id = len(ANCHOR_COMPANIES) + 1
    for i in range(next_id, n + 1):
        companies.append(_random_company(i))

    # Принудительно делаем «белые пятна» действительно без клиентов РТК
    for c in companies:
        if c["cluster_zone"] in WHITE_SPOT_ZONES:
            c["is_rtk_client"] = False

    # Помечаем белые пятна
    companies, _ = detect_and_mark_white_spots(companies)
    return companies


# ---------------------------------------------------------------------------
# Генерация инвестиционных проектов (30 шт.)
# ---------------------------------------------------------------------------

def generate_invest_projects(n: int = 30) -> List[Dict[str, Any]]:
    """Генерирует инвестиционные проекты со стадиями, потребностями и датами событий."""
    random.seed(43)
    projects: List[Dict[str, Any]] = []
    start_date = datetime(2026, 11, 1)
    end_date = datetime(2027, 9, 30)
    delta_days = (end_date - start_date).days

    for i in range(1, n + 1):
        industry = random.choice(INDUSTRIES)
        stage = random.choice(STAGES)
        needs = random.sample(TARGET_NEEDS, k=random.randint(1, 3))
        event_date = start_date + timedelta(days=random.randint(0, delta_days))
        zone = random.choice(CLUSTER_ZONES_SPEC)
        lat = round(zone["center_lat"] + random.uniform(-zone["spread_lat"], zone["spread_lat"]), 6)
        lon = round(zone["center_lon"] + random.uniform(-zone["spread_lon"], zone["spread_lon"]), 6)

        projects.append({
            "id": i,
            "title": f"Инвестпроект {industry} #{i}",
            "investor": f"Инвестор {i}",
            "industry": industry,
            "stage": stage,
            "budget": round(random.uniform(50, 5000), 2),
            "lat": lat,
            "lon": lon,
            "target_needs": json.dumps(needs, ensure_ascii=False),
            "event_date": event_date.strftime("%Y-%m-%d"),
            "description": f"Инвестиционный проект в отрасли {industry}, стадия {stage}",
        })

    return projects


# ---------------------------------------------------------------------------
# Генерация сделок-бенчмарок (20 шт.)
# ---------------------------------------------------------------------------

BENCHMARK_TEMPLATES: List[Dict[str, Any]] = [
    {"title": "Офисный центр «Альфа» 500 кв.м", "industry": "IT", "scale": 500.0, "price": 1200000.0, "margin": 30.0},
    {"title": "Складской комплекс «Логос» 3000 кв.м", "industry": "Логистика", "scale": 3000.0, "price": 4800000.0, "margin": 25.5},
    {"title": "Агроферма «Зеленое поле» 1500 кв.м", "industry": "АПК", "scale": 1500.0, "price": 2300000.0, "margin": 22.0},
    {"title": "ТЭК-подстанция «Энерго-1» 800 кв.м", "industry": "ТЭК", "scale": 800.0, "price": 3100000.0, "margin": 28.0},
    {"title": "Завод «Металлоидея» 5000 кв.м", "industry": "Производство", "scale": 5000.0, "price": 9500000.0, "margin": 24.0},
    {"title": "Торговый центр «Галактика» 4000 кв.м", "industry": "Торговля", "scale": 4000.0, "price": 6200000.0, "margin": 26.5},
    {"title": "IT-хаб «Цифровой дом» 2500 кв.м", "industry": "IT", "scale": 2500.0, "price": 3900000.0, "margin": 27.0},
    {"title": "Логистический узел «Транзит» 6000 кв.м", "industry": "Логистика", "scale": 6000.0, "price": 8800000.0, "margin": 23.5},
    {"title": "Агрокомплекс «Урожай» 2000 кв.м", "industry": "АПК", "scale": 2000.0, "price": 2900000.0, "margin": 21.0},
    {"title": "Энергоузел «Ростов-ТЭЦ» 7000 кв.м", "industry": "ТЭК", "scale": 7000.0, "price": 11200000.0, "margin": 25.0},
    {"title": "Промзона «Западная» 3500 кв.м", "industry": "Производство", "scale": 3500.0, "price": 5400000.0, "margin": 24.5},
    {"title": "Торговый павильон «Рынок» 800 кв.м", "industry": "Торговля", "scale": 800.0, "price": 1400000.0, "margin": 29.0},
    {"title": "Центр обработки данных «Облако» 1200 кв.м", "industry": "IT", "scale": 1200.0, "price": 4600000.0, "margin": 27.5},
    {"title": "Склад «Холод» 2200 кв.м", "industry": "Логистика", "scale": 2200.0, "price": 3800000.0, "margin": 23.0},
    {"title": "Тепличный комплекс «Весна» 1800 кв.м", "industry": "АПК", "scale": 1800.0, "price": 2600000.0, "margin": 20.5},
    {"title": "Электростанция «Энергия» 4500 кв.м", "industry": "ТЭК", "scale": 4500.0, "price": 7800000.0, "margin": 26.0},
    {"title": "Завод «Автокомпонент» 5500 кв.м", "industry": "Производство", "scale": 5500.0, "price": 10200000.0, "margin": 24.0},
    {"title": "Магазин «Супермаркет» 1200 кв.м", "industry": "Торговля", "scale": 1200.0, "price": 2100000.0, "margin": 28.0},
    {"title": "IT-центр «Техносерв» 1600 кв.м", "industry": "IT", "scale": 1600.0, "price": 3200000.0, "margin": 26.0},
    {"title": "Логистика «Портовый» 2800 кв.м", "industry": "Логистика", "scale": 2800.0, "price": 4500000.0, "margin": 25.0},
]


def generate_benchmarks(n: int = 20) -> List[Dict[str, Any]]:
    """Генерирует сделки-бенчмарки с ценами и маржами по отраслям и масштабам."""
    random.seed(44)
    benchmarks: List[Dict[str, Any]] = []
    for i in range(1, n + 1):
        template = BENCHMARK_TEMPLATES[(i - 1) % len(BENCHMARK_TEMPLATES)].copy()
        template["id"] = i
        template["final_price"] = template.pop("price")
        benchmarks.append(template)
    return benchmarks


# ---------------------------------------------------------------------------
# Экспорт в initial_data.json и фикстуры
# ---------------------------------------------------------------------------

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
FIXTURES_DIR = os.path.join(BACKEND_DIR, "app", "db", "fixtures")


def export_data(
    companies: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    benchmarks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Экспортирует сгенерированные данные в initial_data.json и CSV/JSON фикстуры."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FIXTURES_DIR, exist_ok=True)

    # 1. initial_data.json
    payload = {
        "companies": companies,
        "projects": projects,
        "benchmarks": benchmarks,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_companies": len(companies),
        "total_projects": len(projects),
        "total_benchmarks": len(benchmarks),
        "white_spot_zones": sorted(list(WHITE_SPOT_ZONES)),
    }
    json_path = os.path.join(DATA_DIR, "initial_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[+] Экспортировано: {json_path} ({len(companies)} компаний, {len(projects)} проектов, {len(benchmarks)} бенчмарок)")

    # 2. CSV фикстуры (компании)
    companies_csv = os.path.join(FIXTURES_DIR, "companies.csv")
    with open(companies_csv, "w", encoding="utf-8", newline="") as f:
        if companies:
            writer = csv.DictWriter(f, fieldnames=list(companies[0].keys()))
            writer.writeheader()
            writer.writerows(companies)
    print(f"[+] Экспортировано: {companies_csv}")

    # 3. CSV фикстуры (проекты)
    projects_csv = os.path.join(FIXTURES_DIR, "invest_projects.csv")
    with open(projects_csv, "w", encoding="utf-8", newline="") as f:
        if projects:
            writer = csv.DictWriter(f, fieldnames=list(projects[0].keys()))
            writer.writeheader()
            writer.writerows(projects)
    print(f"[+] Экспортировано: {projects_csv}")

    # 4. JSON фикстуры (бенчмарки)
    benchmarks_json = os.path.join(FIXTURES_DIR, "benchmarks.json")
    with open(benchmarks_json, "w", encoding="utf-8") as f:
        json.dump(benchmarks, f, ensure_ascii=False, indent=2)
    print(f"[+] Экспортировано: {benchmarks_json}")

    return payload


if __name__ == "__main__":
    companies = generate_companies(200)
    projects = generate_invest_projects(30)
    benchmarks = generate_benchmarks(20)

    ws_count = sum(1 for c in companies if c.get("is_white_spot"))
    ws_zones = set(c.get("cluster_zone", "") for c in companies if c.get("is_white_spot"))
    print(f"\n[*] Белых пятен: {ws_count} компаний в зонах: {sorted(ws_zones)}")
    print(f"[*] Клиентов РТК: {sum(1 for c in companies if c.get('is_rtk_client'))} из {len(companies)}")

    export_data(companies, projects, benchmarks)
    print("\n[+] Генерация данных завершена успешно!")
