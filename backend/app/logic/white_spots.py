"""
Алгоритм выявления «Белых пятен» (White Spots Detection) и скоринга потенциала территорий.
Роль 2: Data Engineer & Логика расчетов (Этап 3).
"""

from typing import List, Dict, Any, Tuple
import math


def assign_grid_cluster(lat: float, lon: float, precision: int = 2) -> str:
    """
    Резервная гео-кластеризация через координатную сетку (округление lat/lon),
    если у компании не задан административный/промышленный район cluster_zone.
    """
    lat_grid = round(lat, precision)
    lon_grid = round(lon, precision)
    return f"GRID-{lat_grid:.2f}_{lon_grid:.2f}"


def calculate_zone_statistics(companies: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Агрегирует показатели бизнеса по каждому кластеру/району (cluster_zone):
    - total_companies: общее количество предприятий в зоне
    - rtk_clients: количество действующих клиентов Ростелекома
    - leads_count: количество потенциальных клиентов (лидов)
    - penetration_rate: доля покрытия Ростелекома в зоне (0..1)
    - total_revenue: совокупная выручка всех компаний зоны (млн руб.)
    - potential_revenue: выручка неохваченных компаний — лидов (млн руб.)
    - avg_growth: средняя динамика выручки в зоне (%)
    - opportunity_score: интегральный скоринг коммерческого потенциала зоны (0..100)
    - is_white_spot: флаг «Белого пятна»
    """
    zones: Dict[str, List[Dict[str, Any]]] = {}
    for comp in companies:
        zone_name = comp.get("cluster_zone") or assign_grid_cluster(
            float(comp.get("lat", 47.2225)),
            float(comp.get("lon", 39.7187))
        )
        zones.setdefault(zone_name, []).append(comp)

    raw_stats: Dict[str, Dict[str, Any]] = {}
    max_potential_rev = 1.0
    max_leads = 1

    for zone_name, items in zones.items():
        total_count = len(items)
        clients_count = sum(1 for c in items if c.get("is_rtk_client", False))
        leads_count = total_count - clients_count
        penetration = clients_count / total_count if total_count > 0 else 0.0

        total_rev = sum(float(c.get("revenue", 0.0)) for c in items)
        potential_rev = sum(
            float(c.get("revenue", 0.0))
            for c in items
            if not c.get("is_rtk_client", False)
        )
        avg_growth = (
            sum(float(c.get("revenue_growth", 0.0)) for c in items) / total_count
            if total_count > 0
            else 0.0
        )

        if potential_rev > max_potential_rev:
            max_potential_rev = potential_rev
        if leads_count > max_leads:
            max_leads = leads_count

        raw_stats[zone_name] = {
            "cluster_zone": zone_name,
            "total_companies": total_count,
            "rtk_clients": clients_count,
            "leads_count": leads_count,
            "penetration_rate": round(penetration, 4),
            "penetration_percent": round(penetration * 100, 2),
            "total_revenue": round(total_rev, 2),
            "potential_revenue": round(potential_rev, 2),
            "avg_growth": round(avg_growth, 2),
        }

    # Нормализация и расчет интегрального скоринга потенциала зоны (Zone Opportunity Score)
    # Формула:
    # Score = 100 * (0.45 * Norm(PotentialRevenue) + 0.25 * (1 - PenetrationRate)
    #                + 0.15 * Norm(AvgGrowth) + 0.15 * Norm(LeadsCount))
    for zone_name, st in raw_stats.items():
        norm_rev = st["potential_revenue"] / max_potential_rev if max_potential_rev > 0 else 0.0
        norm_uncovered = 1.0 - st["penetration_rate"]
        # Нормализуем средний рост от -10% до +25% в интервал [0, 1]
        norm_growth = max(0.0, min(1.0, (st["avg_growth"] + 10.0) / 35.0))
        norm_leads = st["leads_count"] / max_leads if max_leads > 0 else 0.0

        score = 100.0 * (
            0.45 * norm_rev
            + 0.25 * norm_uncovered
            + 0.15 * norm_growth
            + 0.15 * norm_leads
        )
        st["opportunity_score"] = round(score, 2)

        # Критерий «Белого пятна» (White Spot):
        # 1) Высокая суммарная выручка бизнеса в кластере (>= 300 млн руб.)
        # 2) Положительная средняя динамика выручки (> 0%)
        # 3) Отсутствие клиентов РТК (0 клиентов) или минимальное покрытие (<= 10%)
        is_ws = (
            st["potential_revenue"] >= 300.0
            and st["avg_growth"] > 0.0
            and (st["rtk_clients"] == 0 or st["penetration_rate"] <= 0.10)
        )
        st["is_white_spot"] = bool(is_ws)

    return raw_stats


def detect_and_mark_white_spots(
    companies: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """
    Принимает список компаний, рассчитывает статистику кластеров и проставляет
    каждой компании актуальный флаг `is_white_spot` (а также `white_spot` для совместимости).
    Возвращает обновленный список компаний и словарь статистики по кластерам.
    """
    zone_stats = calculate_zone_statistics(companies)
    enriched_companies: List[Dict[str, Any]] = []

    for comp in companies:
        item = dict(comp)
        zone_name = item.get("cluster_zone") or assign_grid_cluster(
            float(item.get("lat", 47.2225)),
            float(item.get("lon", 39.7187))
        )
        item["cluster_zone"] = zone_name
        zone_is_ws = zone_stats.get(zone_name, {}).get("is_white_spot", False)
        # Компания помечается как объект в «белом пятне», если она находится в зоне White Spot
        # и сама ещё не является клиентом Ростелекома
        is_comp_ws = bool(zone_is_ws and not item.get("is_rtk_client", False))
        item["is_white_spot"] = is_comp_ws
        enriched_companies.append(item)

    return enriched_companies, zone_stats
