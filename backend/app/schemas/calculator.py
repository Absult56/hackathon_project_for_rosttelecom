from pydantic import BaseModel
from typing import List, Optional

class CalculateRequest(BaseModel):
    project_id: Optional[int] = None
    company_id: Optional[int] = None
    scale_param: float
    work_types: List[str]
    urgency_coeff: float = 1.0
    region_coeff: float = 1.0

class BenchmarkDealOut(BaseModel):
    title: str
    price: float
    margin: float

class CalculateResponse(BaseModel):
    cost_price: float
    min_price: float
    optimal_price: float
    margin_rub: float
    margin_percent: float
    benchmarks: List[BenchmarkDealOut]