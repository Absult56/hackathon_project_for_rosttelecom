from typing import List, Dict, Any

# Базовые коэффициенты стоимости типовых работ (передаются Data Engineer)
WORK_TYPE_COSTS = {
    "fiber_optics": 1200.0,  # Прокладка ВОЛС (за метр/единицу)
    "cctv": 850.0,  # Интеллектуальное видеонаблюдение
    "data_center": 3500.0,  # Серверная стойка / ЦОД
    "telephony": 450.0,  # IP-телефония
    "access_control": 600.0  # СКУД
}


def compute_deal_estimate(
        scale_param: float,
        work_types: List[str],
        urgency_coeff: float = 1.0,
        region_coeff: float = 1.0
) -> Dict[str, float]:
    """
    Математическое ядро расчета сметы и ценовой вилки (Зона синхронизации с Ролью 2 DE/ML).
    """
    # 1. Считаем базовую стоимость по типам работ
    if not work_types:
        unit_rate = 1000.0
    else:
        unit_rate = sum(WORK_TYPE_COSTS.get(wt, 1000.0) for wt in work_types) / len(work_types)

    # 2. Себестоимость с учетом масштаба, региона и срочности
    cost_price = scale_param * unit_rate * region_coeff * urgency_coeff

    # 3. Ценовая вилка Ростелекома
    min_price = cost_price * 1.15  # Минимальная цена (+15% минимальная маржа)
    optimal_price = cost_price * 1.35  # Оптимальная коммерческая цена (+35%)

    margin_rub = optimal_price - cost_price
    margin_percent = round((margin_rub / optimal_price) * 100, 2)

    return {
        "cost_price": round(cost_price, 2),
        "min_price": round(min_price, 2),
        "optimal_price": round(optimal_price, 2),
        "margin_rub": round(margin_rub, 2),
        "margin_percent": margin_percent
    }