# PR: Role 2 — Data Engineer & Логика расчетов (Этапы 1–5)

**Ветка:** `feature/data-seed-fixtures`
**Коммит:** `4aa293b`
**Статус:** Готово к ревью и мержу в `main`

## Что сделано (Этапы 1–5)

### Этап 1 — Генератор датасета Ростовской области
`backend/app/logic/data_generation.py` (471 строк)

- Генератор ИНН с контрольной суммой ФНС для кодов региона 61xx. Все 200 ИНН проходят проверку.
- 8 якорных компаний с реальными названиями (Ростовэнерго, Агрокомплекс и др.). Все ИНН валидны по ФНС.
- 9 кластерных зон: 5 обычных + 4 белых пятна (Порт, Батайск, Новый Аксай, Таганрог-Пром).
- `generate_companies(200)`, `generate_invest_projects(30)`, `generate_benchmarks(20)`.
- `detect_and_mark_white_spots()` — маркировка `is_white_spot=true` для 4 зон.
- `export_data()` — запись в `initial_data.json` и CSV/JSON фикстуры.

### Этап 2 — Экспорт и фикстуры
- `backend/data/initial_data.json` — полный датасет.
- `backend/app/db/fixtures/companies.csv`, `invest_projects.csv`, `benchmarks.json`.

### Этап 3 — Seed pipeline
`backend/app/core/seed_data.py` — бенчмарки загружаются из `initial_data.json`.

### Этап 4 — Dual-format Deal Calculator
`backend/app/logic/calculator_service.py` — два формата запроса (фронтенд + бэкенд), KNN-бенчмарки, региональные коэффициенты.

### Этап 5 — API, схемы, сервисы, модели

## Файлы в PR (18 файлов)

| Файл | Назначение |
|------|------------|
| `backend/app/logic/data_generation.py` | Генератор датасета, ИНН, белые пятна, экспорт |
| `backend/app/logic/calculator_service.py` | Двухформатный калькулятор сделок |
| `backend/app/logic/white_spots.py` | Логика обнаружения белых пятен |
| `backend/app/core/seed_data.py` | Загрузка данных из initial_data.json в БД |
| `backend/app/core/database.py` | Настройка БД |
| `backend/data/initial_data.json` | Датасет (200 компаний, 30 проектов, 20 бенчмарок) |
| `backend/app/db/fixtures/companies.csv` | CSV фикстура компаний |
| `backend/app/db/fixtures/invest_projects.csv` | CSV фикстура проектов |
| `backend/app/db/fixtures/benchmarks.json` | JSON фикстура бенчмарок |
| `backend/app/models/__init__.py` | Инициализация моделей |
| `backend/app/models/company.py` | Модель Company |
| `backend/app/models/invest_project.py` | Модель InvestProject |
| `backend/app/models/benchmark.py` | Модель Benchmark |
| `backend/app/schemas/calculator.py` | Pydantic-схемы калькулятора |
| `backend/app/services/calculator.py` | Сервисный слой калькулятора |
| `backend/app/api/calculator.py` | API эндпоинт калькулятора |
| `backend/app/logic/__init__.py` | Инициализация пакета логики |
| `backend/main.py` | Точка входа FastAPI |

## Как проверить

### 1. Запуск сервера
```bash
cd backend
uvicorn app.main:app --reload
```

### 2. Тест калькулятора — фронтенд-формат
```bash
curl -X POST http://localhost:8000/calculator/calculate \
  -H "Content-Type: application/json" \
  -d '{"object_type":"industrial_warehouse","scale":"medium","work_types":["fiber_optics","cctv","access_control"],"region_code":"61"}'
```

### 3. Тест калькулятора — бэкенд-формат
```bash
curl -X POST http://localhost:8000/calculator/calculate \
  -H "Content-Type: application/json" \
  -d '{"scale_param":3500,"work_types":["fiber_optics","telephony","wifi"],"urgency_coeff":1.1,"region_coeff":1.0}'
```

### 4. Проверка генерации данных
```bash
python app/logic/data_generation.py
```
Все 200 ИНН проходят контрольную сумму ФНС.

## Ограничения

1. Ветка без общей истории с `main` — при мерже может потребоваться `--allow-unrelated-histories`.
2. Кластеры заданы вручную (без DBSCAN/K-Means) для интерпретируемости зон.

> **Авторизация калькулятора:** эндпоинт `POST /calculator/calculate` сделан публичным (убрана зависимость `get_current_user`), так как калькулятор — инструмент предпродажной оценки, не требующий аутентификации. Остальные эндпоинты (`/api/auth/*`, `/api/radar/*`, `/api/invest/*`) по-прежнему защищены auth middleware без изменений.
`api/calculator.py`, `schemas/calculator.py`, `services/calculator.py`, `models/*`, `core/database.py`, `main.py`.