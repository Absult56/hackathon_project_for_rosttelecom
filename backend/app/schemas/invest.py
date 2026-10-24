from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class InvestProjectOut(BaseModel):
    id: int
    title: str
    investor: str
    industry: str
    stage: str
    budget: float
    lat: float
    lon: float
    target_needs: List[str]
    event_date: str
    description: str

    class Config:
        from_attributes = True