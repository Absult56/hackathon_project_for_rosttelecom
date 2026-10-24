from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import Response
from app.services.export_service import render_kp_docx

from app.core.database import get_db
from app.models.invest_project import InvestProject
from app.models.company import Company
from app.models.benchmark import BenchmarkDeal
from app.schemas.calculator import CalculateRequest, CalculateResponse, BenchmarkDealOut
from app.services.calculator import compute_deal_estimate
from app.core.security import get_current_user

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
    target_industry = "IT"

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

    # Вызов модуля расчетов Data Engineer
    calc_result = compute_deal_estimate(
        scale_param=data.scale_param,
        work_types=data.work_types,
        urgency_coeff=data.urgency_coeff,
        region_coeff=data.region_coeff
    )

    # Запрос исторических бенчмарков из базы (похожие закрытые сделки)
    benchmarks_db = (
        db.query(BenchmarkDeal)
        .filter(BenchmarkDeal.industry.ilike(f"%{target_industry}%"))
        .limit(3)
        .all()
    )

    # Если точных совпадений по отрасли нет, берем любые для ориентира
    if not benchmarks_db:
        benchmarks_db = db.query(BenchmarkDeal).limit(2).all()

    benchmark_list = [
        BenchmarkDealOut(
            title=b.title,
            price=b.final_price,
            margin=b.margin
        )
        for b in benchmarks_db
    ]

    return CalculateResponse(
        cost_price=calc_result["cost_price"],
        min_price=calc_result["min_price"],
        optimal_price=calc_result["optimal_price"],
        margin_rub=calc_result["margin_rub"],
        margin_percent=calc_result["margin_percent"],
        benchmarks=benchmark_list
    )

@router.post(
    "/export-docx",
    summary="Автоматическая генерация коммерческого предложения (КП) в формате .docx"
)
def export_proposal_docx(
        data: CalculateRequest,
        db: Session = Depends(get_db),
):
    # Автоподтягивание данных по компании или инвестпроекту
    client_name = "Потенциальный партнер"
    inn = "7700000000"
    project_title = "Комплексная цифровизация объекта"

    if data.project_id:
        project = db.query(InvestProject).filter(InvestProject.id == data.project_id).first()
        if project:
            client_name = project.investor
            project_title = project.title

    if data.company_id:
        company = db.query(Company).filter(Company.id == data.company_id).first()
        if company:
            client_name = company.name
            inn = company.inn

    # Расчет сметы
    calc = compute_deal_estimate(
        scale_param=data.scale_param,
        work_types=data.work_types,
        urgency_coeff=data.urgency_coeff,
        region_coeff=data.region_coeff
    )

    docx_stream = render_kp_docx(
        client_name=client_name,
        inn=inn,
        project_title=project_title,
        cost_price=calc["cost_price"],
        optimal_price=calc["optimal_price"],
        min_price=calc["min_price"],
        margin_percent=calc["margin_percent"],
        work_types=data.work_types
    )

    doc_id = data.project_id or data.company_id or "deal"
    filename = f"KP_Rostelecom_{doc_id}.docx"

    return Response(
        content=docx_stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )