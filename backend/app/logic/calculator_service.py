"""
Модуль «Калькулятор сделок» (Deal Calculator Service).
Роль 2: Data Engineer & Логика расчетов (Этап 4).
"""

from typing import List, Dict, Any, Optional

# Удельные расценки на единицу масштаба (за 1 кв.м / усл. ед.) для прямой формулы бэкенда
WORK_TYPE_UNIT_COSTS: Dict[str, float] = {
    "fiber_optics": 1200.0,    # Прокладка ВОЛС
    "optics": 1200.0,          # Оптическая сеть (алиас фронтенда)
    "optics_cable": 1200.0,    # Оптический кабель (алиас ТЗ)
    "cctv": 850.0,             # Интеллектуальное видеонаблюдение
    "data_center": 3500.0,     # Серверная стойка / ЦОД
    "server": 3200.0,          # Серверная и СХД (алиас фронтенда)
    "telephony": 450.0,        # IP-телефония и корпоративная связь
    "access_control": 600.0,   # СКУД и контроль доступа
    "wifi": 550.0,             # Беспроводная сеть Wi-Fi и СКС
    "it_infra": 950.0,         # ИТ-инфраструктура
    "asutp": 1800.0,           # Промышленная автоматизация АСУ ТП
}

# Базовые стоимости пакетов оборудования (в руб.) и доли структуры затрат (Оборудование / СМР / Лицензии ПО)
WORK_PACKAGE_SPECS: Dict[str, Dict[str, float]] = {
    "fiber_optics":   {"base_cost": 520_000.0, "eq_share": 0.50, "inst_share": 0.38, "sw_share": 0.12},
    "optics":         {"base_cost": 520_000.0, "eq_share": 0.50, "inst_share": 0.38, "sw_share": 0.12},
    "optics_cable":   {"base_cost": 520_000.0, "eq_share": 0.50, "inst_share": 0.38, "sw_share": 0.12},
    "wifi":           {"base_cost": 340_000.0, "eq_share": 0.58, "inst_share": 0.27, "sw_share": 0.15},
    "it_infra":       {"base_cost": 480_000.0, "eq_share": 0.56, "inst_share": 0.26, "sw_share": 0.18},
    "cctv":           {"base_cost": 680_000.0, "eq_share": 0.54, "inst_share": 0.26, "sw_share": 0.20},
    "data_center":    {"base_cost": 890_000.0, "eq_share": 0.62, "inst_share": 0.18, "sw_share": 0.20},
    "server":         {"base_cost": 890_000.0, "eq_share": 0.62, "inst_share": 0.18, "sw_share": 0.20},
    "telephony":      {"base_cost": 260_000.0, "eq_share": 0.48, "inst_share": 0.24, "sw_share": 0.28},
    "access_control": {"base_cost": 410_000.0, "eq_share": 0.52, "inst_share": 0.30, "sw_share": 0.18},
    "asutp":          {"base_cost": 950_000.0, "eq_share": 0.50, "inst_share": 0.25, "sw_share": 0.25},
}

# Коэффициенты сложности по типу объекта
OBJECT_TYPE_FACTORS: Dict[str, float] = {
    "industrial_warehouse": 1.18,
    "industrial_facility": 1.35,
    "office_center": 0.92,
    "agro_complex": 1.25,
    "energy_facility": 1.40,
}

# Маппинг типа объекта в отрасль (для точного поиска сделок-аналогов)
OBJECT_TYPE_TO_INDUSTRY: Dict[str, str] = {
    "industrial_warehouse": "Логистика",
    "industrial_facility": "Производство",
    "office_center": "IT",
    "agro_complex": "АПК",
    "energy_facility": "ТЭК",
}

SCALE_CATEGORY_FACTORS: Dict[str, float] = {
    "small": 0.78,
    "medium": 1.00,
    "large": 1.42,
}

SCALE_CATEGORY_TO_SQM: Dict[str, float] = {
    "small": 1200.0,
    "medium": 3500.0,
    "large": 8500.0,
}

REGION_COEFFS: Dict[str, float] = {
    "61": 1.00,  # Ростовская область
    "23": 1.04,  # Краснodarский край
    "26": 1.02,  # Ставропольский край
    "34": 1.01,  # Волгоградская область
    "36": 1.00,  # Воронежская область
    "77": 1.22,  # Москва
    "78": 1.15,  # Санкт-Петербург
}

# Коэффициенты сложности по уровню сложности проекта
DIFFICULTY_COEFFS: Dict[str, float] = {
    "Basic": 1.0,
    "Advanced": 1.3,
    "Expert": 1.6,
}


def resolve_scale_sqm(scale_param: Optional[float], scale_category: Optional[str]) -> float:
    """Переводит входной параметр масштаба в площадь (кв.м)."""
    if scale_param is not None and scale_param > 0:
        return float(scale_param)
    if scale_category and scale_category in SCALE_CATEGORY_TO_SQM:
        return SCALE_CATEGORY_TO_SQM[scale_category]
    return 2500.0


def compute_deal_estimate(
    scale_param: Optional[float] = None,
    work_types: Optional[List[str]] = None,
    urgency_coeff: float = 1.0,
    region_coeff: float = 1.0,
    object_type: Optional[str] = None,
    scale: Optional[str] = None,
    duration_months: Optional[int] = None,
    region_code: Optional[str] = None,
    difficulty: str = "Basic",
) -> Dict[str, Any]:
    """
    Универсальное математическое ядро расчета сметы и ценовой вилки Ростелекома.
    Поддерживает как прямые числовые параметры (scale_param, work_types, urgency_coeff, region_coeff),
    так и категориальные параметры мастера КП (object_type, scale, duration_months, region_code).
    """
    selected_works = work_types or ["fiber_optics", "cctv"]

    # 1. Коэффициент срочности: если срок сжатый (<= 2 мес.), надбавка +15%
    effective_urgency = float(urgency_coeff) if urgency_coeff else 1.0
    if duration_months is not None and effective_urgency == 1.0:
        if duration_months <= 2:
            effective_urgency = 1.15
        elif duration_months > 6:
            effective_urgency = 0.96

    # 2. Региональный коэффициент
    effective_region = float(region_coeff) if region_coeff else 1.0
    if region_code and effective_region == 1.0:
        effective_region = REGION_COEFFS.get(str(region_code), 1.0)

    # 3. Коэффициент типа объекта
    obj_factor = OBJECT_TYPE_FACTORS.get(object_type or "", 1.0)

    # 4. Доли структуры затрат (Оборудование / СМР / Лицензии ПО)
    eq_share_sum = 0.0
    inst_share_sum = 0.0
    for wt in selected_works:
        spec = WORK_PACKAGE_SPECS.get(wt, {"eq_share": 0.54, "inst_share": 0.29, "sw_share": 0.17})
        eq_share_sum += spec["eq_share"]
        inst_share_sum += spec["inst_share"]

    n_works = max(1, len(selected_works))
    eq_ratio = eq_share_sum / n_works
    inst_ratio = inst_share_sum / n_works

    # 5. Расчет себестоимости
    if scale_param is not None and scale_param > 0:
        unit_rate = (
            sum(WORK_TYPE_UNIT_COSTS.get(wt, 1000.0) for wt in selected_works) / n_works
            if selected_works
            else 1000.0
        )
        cost_price = float(scale_param) * unit_rate * obj_factor * effective_region * effective_urgency
    else:
        scale_factor = SCALE_CATEGORY_FACTORS.get(scale or "medium", 1.0)
        packages_base = sum(
            WORK_PACKAGE_SPECS.get(wt, {"base_cost": 450_000.0})["base_cost"]
            for wt in selected_works
        )
        engineering_base = 420_000.0
        cost_price = (packages_base + engineering_base) * obj_factor * scale_factor * effective_region * effective_urgency

    # 6. Ценовая вилка Ростелекома
    min_price = round(cost_price * 1.15, 2)
    optimal_price = round(cost_price * 1.35, 2)

    margin_rub = round(optimal_price - cost_price, 2)
    margin_percent = round((margin_rub / optimal_price) * 100.0, 2) if optimal_price > 0 else 25.93

    equipment_cost = round(optimal_price * eq_ratio, 2)
    installation_cost = round(optimal_price * inst_ratio, 2)
    software_cost = round(optimal_price - equipment_cost - installation_cost, 2)

    # 7. PIR/PNR/шеф-монтаж расчеты (на основе стоимости оборудования)
    equipment_base = round(cost_price * eq_ratio, 2)  # Базовая стоимость оборудования
    pir_percent = 10.0  # Планируемый интернет-ресурс (10%)
    pnr_percent = 15.0  # Планируемые réseau-розетки (15%)
    shef_montaz_percent = 5.0  # Шеф-монтаж (5%)
    
    pir_cost = round(equipment_base * pir_percent / 100, 2)
    pnr_cost = round(equipment_base * pnr_percent / 100, 2)
    shef_montaz_cost = round(equipment_base * shef_montaz_percent / 100, 2)

    # Применение коэффициента сложности
    difficulty_coeff = DIFFICULTY_COEFFS.get(difficulty, 1.0)
    adjusted_cost_price = round(cost_price * difficulty_coeff, 2)
    adjusted_optimal_price = round(optimal_price * difficulty_coeff, 2)
    adjusted_margin_rub = round(adjusted_optimal_price - adjusted_cost_price, 2)
    adjusted_margin_percent = round((adjusted_margin_rub / adjusted_optimal_price) * 100.0, 2) if adjusted_optimal_price > 0 else 25.93

    return {
        "cost_price": adjusted_cost_price,
        "min_price": round(adjusted_cost_price * 1.15, 2),
        "optimal_price": adjusted_optimal_price,
        "margin_rub": adjusted_margin_rub,
        "margin_percent": adjusted_margin_percent,
        "recommended_margin_percent": adjusted_margin_percent,
        "cost_structure": {
            "equipment": equipment_cost,
            "installation": installation_cost,
            "software_licenses": software_cost,
            "pir": pir_cost,
            "pnr": pnr_cost,
            "shef_montazh": shef_montaz_cost,
        },
        "effective_scale_sqm": resolve_scale_sqm(scale_param, scale),
        "target_industry_hint": OBJECT_TYPE_TO_INDUSTRY.get(object_type or "", ""),
        "difficulty": difficulty,
        "difficulty_coeff": difficulty_coeff,
    }


def select_similar_benchmarks(
    benchmarks: List[Any],
    target_scale_sqm: float,
    target_industry: Optional[str] = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Находит в базе `top_k` самых близких проектов-аналогов (benchmark_deals)
    по комбинации отраслевого совпадения и близости масштаба (KNN-подход).
    """
    if not benchmarks:
        return []

    scored_items = []
    target_ind_norm = (target_industry or "").strip().lower()

    for b in benchmarks:
        if isinstance(b, dict):
            title = b.get("title", "Типовой проект РТК")
            industry = str(b.get("industry", ""))
            scale_val = float(b.get("scale", 1000.0))
            price_val = float(b.get("final_price", b.get("price", 1500000.0)))
            margin_val = float(b.get("margin", 25.0))
        else:
            title = getattr(b, "title", "Типовой проект РТК")
            industry = str(getattr(b, "industry", ""))
            scale_val = float(getattr(b, "scale", 1000.0))
            price_val = float(getattr(b, "final_price", 1500000.0))
            margin_val = float(getattr(b, "margin", 25.0))

        denom = max(target_scale_sqm, scale_val, 100.0)
        scale_distance = abs(scale_val - target_scale_sqm) / denom
        ind_match = 0.0 if (target_ind_norm and target_ind_norm in industry.lower()) else 0.35
        total_distance = scale_distance + ind_match

        scored_items.append((
            total_distance,
            {
                "title": title,
                "industry": industry,
                "scale": scale_val,
                "price": round(price_val, 2),
                "margin": round(margin_val, 2),
            },
        ))

    scored_items.sort(key=lambda x: x[0])
    return [item[1] for item in scored_items[:top_k]]
