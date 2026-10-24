from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, radar, invest, calculator
from app.core.database import Base, engine, SessionLocal
from app.core.seed_data import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте приложения: создаем таблицы и заливаем фикстуры
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Действия при завершении приложения (если понадобятся)

app = FastAPI(
    title="Rostelecom B2B Geo-Intelligence API",
    description="Хакатон-сервис: Радар присутствия, Инвест-навигатор и Калькулятор сделок с 2FA",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router, prefix="/api")
app.include_router(radar.router, prefix="/api")
app.include_router(invest.router, prefix="/api")
app.include_router(calculator.router, prefix="/api")

@app.get("/", tags=["Healthcheck"])
def root():
    return {"status": "healthy", "docs": "/docs"}