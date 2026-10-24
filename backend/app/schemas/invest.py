from pydantic import BaseModel, field_validator
from typing import List, Union

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

    @field_validator("target_needs", mode="before")
    def parse_target_needs(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    class Config:
        from_attributes = True