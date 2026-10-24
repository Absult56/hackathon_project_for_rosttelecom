from sqlalchemy import Column, Integer, String, Float, Text
from app.core.database import Base

class InvestProject(Base):
    __tablename__ = "invest_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    investor = Column(String, nullable=False)
    industry = Column(String, index=True, nullable=False)
    stage = Column(String, index=True, nullable=False)  # проектирование, стройка, ввод
    budget = Column(Float, default=0.0)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    target_needs = Column(Text, nullable=False)         # Храним через запятую: "fiber_optics,cctv"
    event_date = Column(String, nullable=False)
    description = Column(Text, nullable=True)