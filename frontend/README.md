# Контур коммерческой аналитики

React + TypeScript SPA для демонстрации трёх модулей Ростелекома: геоаналитики, инвестиционных проектов и калькулятора сделок.

## Запуск

```powershell
npm install
npm run dev
```

Чтобы запускать backend на новой Ростовской фактуре и сохранить старую SQLite-базу, из корня проекта выполните:

```powershell
$env:DATABASE_URL = 'sqlite:///./backend/rostov_region.db'
python -m uvicorn app.main:app --app-dir backend --reload
```

Вход: укажите любой email, запросите код и введите мастер-код `123456`. При доступном backend код также отображается в его консоли.

Клиент использует `/api/auth/request-code`, `/api/auth/verify-2fa`, `/api/radar/companies`, `/api/invest/projects`, `/api/calculator/calculate`, `/api/calculator/export-docx` и `/api/export/companies/csv`. Vite проксирует `/api` на `http://127.0.0.1:8000`. Для удалённого backend задайте его адрес в `.env.local` как `VITE_API_URL=https://<current-pinggy-host>/api` (пример есть в `.env.example`). Если API недоступно, приложение использует локальные демо-данные и генерирует CSV/DOCX в браузере.

Ростовские fixtures из последнего обновления `main` находятся в `backend/data/regional_initial_data.json`: 200 компаний и 30 проектов. В приложении видны только записи с координатами внутри Ростовской области; если backend отдаёт другой регион, используется помеченный демо-набор, а не перенос чужих координат на ростовскую карту.