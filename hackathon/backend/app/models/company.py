from sqlalchemy import Column, Integer, String, Float, Boolean
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    inn = Column(String, unique=True, index=True, nullable=False)
    industry = Column(String, index=True, nullable=False)
    revenue = Column(Float, default=0.0)
    revenue_growth = Column(Float, default=0.0)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    is_rtk_client = Column(Boolean, default=False)
    is_white_spot = Column(Boolean, default=False)
    cluster_zone = Column(String, nullable=True)