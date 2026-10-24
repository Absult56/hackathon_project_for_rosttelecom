# Контур коммерческой аналитики

React + TypeScript SPA для демонстрации трёх модулей Ростелекома: геоаналитики, инвестиционных проектов и калькулятора сделок.

## Запуск

```powershell
npm install
npm run dev
```

Демо-вход: `admin` / `rtk_password` / `123456`.

При доступном FastAPI клиент использует `/api/auth/login-2fa`, `/api/radar/companies`, `/api/invest/projects`, `/api/calculator/calculate`, `/api/calculator/generate-doc` и `/api/export/companies-csv`. Vite проксирует `/api` на `http://127.0.0.1:8000`. Если API недоступно, приложение использует локальные демо-данные и генерирует CSV/DOCX в браузере.

Компании и инвестиционные проекты для автономной демонстрации находятся в `public/mocks/`; на радаре также генерируются дополнительные явно помеченные демо-компании для показа кластеризации.