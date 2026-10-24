from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.invest_project import InvestProject
from app.models.company import Company
from app.models.benchmark import BenchmarkDeal
from app.schemas.calculator import CalculateRequest, CalculateResponse, BenchmarkDealOut, CostStructureOut
from app.services.calculator import compute_deal_estimate, select_similar_benchmarks
router = APIRouter(prefix="/calculator", tags=["Deal Calculator"])

@router.post(
    "/calculate",
    response_model=CalculateResponse,
    summary="Сквозной расчет сметы по проекту/компании с бенчмарками"
)
def calculate_deal(
    data: CalculateRequest,
    db: Session = Depends(get_db),
):
    target_industry = ""

    # Сквозная логика: если передан project_id, валидируем его наличие в БД
    if data.project_id:
        project = db.query(InvestProject).filter(InvestProject.id == data.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Проект с ID {data.project_id} не найден в базе данных"
            )
        target_industry = project.industry

    # Если передан company_id, берем отрасль компании
    elif data.company_id:
        company = db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Компания с ID {data.company_id} не найдена в базе данных"
            )
        target_industry = company.industry

    effective_works = data.work_types if data.work_types is not None else (data.work_type or ["fiber_optics", "cctv"])

    # Вызов модуля расчетов Data Engineer
    calc_result = compute_deal_estimate(
        scale_param=data.scale_param,
        work_types=effective_works,
        urgency_coeff=data.urgency_coeff,
        region_coeff=data.region_coeff,
        object_type=data.object_type,
        scale=data.scale,
        duration_months=data.duration_months,
        region_code=data.region_code,
    )

    if not target_industry:
        target_industry = calc_result.get("target_industry_hint") or "Логистика"

    # Подбор ближайших исторических бенчмарков из базы (KNN по масштабу и отрасли)
    all_benchmarks = db.query(BenchmarkDeal).all()
    similar_deals = select_similar_benchmarks(
        benchmarks=all_benchmarks,
        target_scale_sqm=calc_result.get("effective_scale_sqm", 2500.0),
        target_industry=target_industry,
        top_k=3,
    )

    benchmark_list = [
        BenchmarkDealOut(
            title=b["title"],
            price=b["price"],
            margin=b["margin"]
        )
        for b in similar_deals
    ]

    return CalculateResponse(
        cost_price=calc_result["cost_price"],
        min_price=calc_result["min_price"],
        optimal_price=calc_result["optimal_price"],
        margin_rub=calc_result["margin_rub"],
        margin_percent=calc_result["margin_percent"],
        recommended_margin_percent=calc_result["recommended_margin_percent"],
        cost_structure=CostStructureOut(**calc_result["cost_structure"]),
        similar_deals_count=len(similar_deals),
        benchmarks=benchmark_list,
        difficulty=calc_result.get("difficulty", "medium"),
        difficulty_coeff=calc_result.get("difficulty_coeff", 1.0),
    )