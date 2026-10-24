from pydantic import BaseModel
from typing import List, Optional

class CompanyOut(BaseModel):
    id: int
    name: str
    inn: str
    industry: str
    revenue: float
    revenue_growth: float
    lat: float
    lon: float
    address: str
    is_rtk_client: bool
    is_white_spot: bool
    cluster_zone: str

    class Config:
        from_attributes = True

class RadarAnalyticsOut(BaseModel):
    total_companies: int
    rtk_clients_count: int
    white_spots_count: int
    penetration_rate: float
    revenue_by_industry: dict[str, float]