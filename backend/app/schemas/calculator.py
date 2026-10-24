from pydantic import BaseModel
from typing import List, Optional, Dict

class CalculateRequest(BaseModel):
    project_id: Optional[int] = None
    company_id: Optional[int] = None
    scale_param: Optional[float] = None
    work_types: Optional[List[str]] = None
    urgency_coeff: float = 1.0
    region_coeff: float = 1.0
    # Поля для совместимости с мастером КП фронтенда и ТЗ:
    object_type: Optional[str] = None
    scale: Optional[str] = None
    work_type: Optional[List[str]] = None
    duration_months: Optional[int] = None
    region_code: Optional[str] = None

class BenchmarkDealOut(BaseModel):
    title: str
    price: float
    margin: float

class CostStructureOut(BaseModel):
    equipment: float
    installation: float
    software_licenses: float

class CalculateResponse(BaseModel):
    cost_price: float
    min_price: float
    optimal_price: float
    margin_rub: float
    margin_percent: float
    recommended_margin_percent: float
    cost_structure: CostStructureOut
    similar_deals_count: int
    benchmarks: List[BenchmarkDealOut]