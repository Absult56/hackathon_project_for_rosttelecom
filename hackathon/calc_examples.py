import os
import sys

sys.path.insert(0, 'C:\\Users\\Absult\\.cline\\data\\workspaces\\chat\\hackathon\\backend')

# ---------------------------------------------------------------------------
# 1. Чистая SQLite-база + сидирование фикстур
# ---------------------------------------------------------------------------
DB_PATH = 'C:\\Users\\Absult\\.cline\\data\\workspaces\\chat\\hackathon\\backend\\data.db'
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

from app.core.database import Base, engine, SessionLocal
from app.core.seed_data import seed_database
from app.models.benchmark import BenchmarkDeal
from app.models.company import Company
from app.models.invest_project import InvestProject
from app.logic.calculator_service import compute_deal_estimate, select_similar_benchmarks

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_database(db)

    company_count = db.query(Company).count()
    project_count = db.query(InvestProject).count()
    benchmark_count = db.query(BenchmarkDeal).count()
    print(f'[*] Сидирование БД: компаний={company_count}, проектов={project_count}, бенчмарок={benchmark_count}')

    all_benchmarks = db.query(BenchmarkDeal).all()
    print(f'[*] Загруженоベンчмарок из БД: {len(all_benchmarks)}')
finally:
    db.close()

print('=' * 70)

# ---------------------------------------------------------------------------
# 2. Формат фронтенда (object_type / scale / work_types)
# ---------------------------------------------------------------------------
result1 = compute_deal_estimate(
    object_type='industrial_warehouse',
    scale='medium',
    work_types=['fiber_optics', 'cctv', 'access_control'],
    region_code='61'
)

db = SessionLocal()
try:
    all_benchmarks = db.query(BenchmarkDeal).all()
    target_industry1 = result1.get('target_industry_hint') or 'Логистика'
    similar1 = select_similar_benchmarks(
        benchmarks=all_benchmarks,
        target_scale_sqm=result1.get('effective_scale_sqm', 3500.0),
        target_industry=target_industry1,
        top_k=3,
    )
finally:
    db.close()

print('=== ФРОНТЕНД-ФОРМАТ ===')
print('object_type: industrial_warehouse, scale: medium')
print('work_types: fiber_optics, cctv, access_control')
print('region_code: 61')
print('cost_price: {:,.2f} руб'.format(result1['cost_price']))
print('min_price: {:,.2f} руб'.format(result1['min_price']))
print('optimal_price: {:,.2f} руб'.format(result1['optimal_price']))
print('margin_percent: {}%'.format(result1['margin_percent']))
print('recommended_margin_percent: {}%'.format(result1['recommended_margin_percent']))
print('cost_structure: {}'.format(result1['cost_structure']))
print('effective_scale_sqm: {}'.format(result1['effective_scale_sqm']))
print('target_industry_hint: {}'.format(result1['target_industry_hint']))
print('similar_deals_count: {}'.format(len(similar1)))
print('benchmarks:')
for b in similar1:
    print('  - {}: {} кв.м, отрасль {}, {:,.0f} руб, маржа {}%'.format(
        b['title'], b['scale'], b['industry'], b['price'], b['margin']))

print()
print('=' * 70)
print()

# ---------------------------------------------------------------------------
# 3. Формат бэкенда (scale_param / work_types)
# ---------------------------------------------------------------------------
result2 = compute_deal_estimate(
    scale_param=3500,
    work_types=['fiber_optics', 'telephony', 'wifi'],
    urgency_coeff=1.1,
    region_coeff=1.0
)

db = SessionLocal()
try:
    all_benchmarks = db.query(BenchmarkDeal).all()
    # Во втором формате отрасль не задана (object_type absent) -> подбор только по масштабу
    target_industry2 = result2.get('target_industry_hint') or ''
    similar2 = select_similar_benchmarks(
        benchmarks=all_benchmarks,
        target_scale_sqm=result2.get('effective_scale_sqm', 3500.0),
        target_industry=target_industry2,
        top_k=3,
    )
finally:
    db.close()

print('=== БЭКЕНД-ФОРМАТ ===')
print('scale_param: 3500 кв.м')
print('work_types: fiber_optics, telephony, wifi')
print('urgency_coeff: 1.1, region_coeff: 1.0')
print('cost_price: {:,.2f} руб'.format(result2['cost_price']))
print('min_price: {:,.2f} руб'.format(result2['min_price']))
print('optimal_price: {:,.2f} руб'.format(result2['optimal_price']))
print('margin_percent: {}%'.format(result2['margin_percent']))
print('recommended_margin_percent: {}%'.format(result2['recommended_margin_percent']))
print('cost_structure: {}'.format(result2['cost_structure']))
print('effective_scale_sqm: {}'.format(result2['effective_scale_sqm']))
print('target_industry_hint: {}'.format(result2['target_industry_hint']))
print('similar_deals_count: {}'.format(len(similar2)))
print('benchmarks:')
for b in similar2:
    print('  - {}: {} кв.м, отрасль {}, {:,.0f} руб, маржа {}%'.format(
        b['title'], b['scale'], b['industry'], b['price'], b['margin']))