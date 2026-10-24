# Контур коммерческой аналитики

React + TypeScript SPA для демонстрации трёх модулей Ростелекома: геоаналитики, инвестиционных проектов и калькулятора сделок.

## Запуск

```powershell
npm install
npm run dev
```

Вход: укажите любой email, запросите код и введите мастер-код `123456`. При доступном backend код также отображается в его консоли.

Клиент использует `/api/auth/request-code`, `/api/auth/verify-2fa`, `/api/radar/companies`, `/api/invest/projects`, `/api/calculator/calculate`, `/api/calculator/export-docx` и `/api/export/companies/csv`. Vite проксирует `/api` на `http://127.0.0.1:8000`. Для удалённого backend задайте его адрес в `.env.local` как `VITE_API_URL=https://<current-pinggy-host>/api` (пример есть в `.env.example`). Если API недоступно, приложение использует локальные демо-данные и генерирует CSV/DOCX в браузере.

Компании и инвестиционные проекты для автономной демонстрации находятся в `public/mocks/`; на радаре также генерируются дополнительные явно помеченные демо-компании для показа кластеризации.