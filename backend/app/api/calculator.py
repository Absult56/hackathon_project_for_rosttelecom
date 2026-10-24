from fastapi import APIRouter
from app.schemas.calculator import CalculateRequest, CalculateResponse

router = APIRouter(prefix="/calculator", tags=["Deal Calculator"])


@router.post("/calculate", response_model=CalculateResponse, summary="Расчет сметы и ценовой вилки")
def calculate_deal(data: CalculateRequest):
    # Моковый расчет логики DE (будет заменен во 2-й половине хакатона)
    base_cost = data.scale_param * 1500.0 * data.region_coeff * data.urgency_coeff
    work_multiplier = len(data.work_types) if data.work_types else 1.0

    cost_price = base_cost * (0.8 + 0.2 * work_multiplier)
    optimal_price = cost_price * 1.35
    min_price = cost_price * 1.15
    margin_rub = optimal_price - cost_price
    margin_percent = round((margin_rub / optimal_price) * 100, 2)

    return CalculateResponse(
        cost_price=round(cost_price, 2),
        min_price=round(min_price, 2),
        optimal_price=round(optimal_price, 2),
        margin_rub=round(margin_rub, 2),
        margin_percent=margin_percent,
        benchmarks=[
            {"title": "Аналогичный склад в Подольске", "price": 4200000.0, "margin": 28.5},
            {"title": "Агро-хаб Дмитров", "price": 3100000.0, "margin": 26.0}
        ]
    )