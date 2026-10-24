from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class BenchmarkDeal(Base):
    __tablename__ = "benchmark_deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    scale = Column(Float, nullable=False)
    final_price = Column(Float, nullable=False)
    margin = Column(Float, nullable=False)