import csv
import io
import os
from datetime import datetime
from typing import List
from docxtpl import DocxTemplate

from app.models.company import Company
from app.models.invest_project import InvestProject
from app.services.template_generator import ensure_kp_template_exists, TEMPLATE_PATH


def generate_companies_csv(companies: List[Company]) -> bytes:
    """Генерация CSV по компаниям с кодировкой UTF-8-SIG (BOM для русского Excel)."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    # Заголовки (RFC-4180 совместимый формат для CRM)
    writer.writerow([
        "ID", "Название компании", "ИНН", "Отрасль",
            "Оценочная выручка (млн ₽)", "Рост (%)", "Белое пятно", "Адрес", "Широта", "Долгота"
    ])

    for c in companies:
        writer.writerow([
            c.id, c.name, c.inn, c.industry,
            c.revenue, c.revenue_growth,
            "Да" if c.is_white_spot else "Нет",
            c.address, c.lat, c.lon
        ])

    # utf-8-sig добавляет байты \xef\xbb\xbf, благодаря чему Excel сразу открывает русский язык без кракозябр
    return output.getvalue().encode("utf-8-sig")


def generate_projects_csv(projects: List[InvestProject]) -> bytes:
    """Генерация CSV по инвестпроектам (закрывает критерий 'Экспорт из любого модуля')."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

    writer.writerow([
        "ID", "Название проекта", "Инвестор", "Отрасль",
        "Стадия", "Бюджет (млн ₽)", "Потребности ИТ", "Дата события", "Широта", "Долгота"
    ])

    for p in projects:
        writer.writerow([
            p.id, p.title, p.investor, p.industry,
            p.stage, p.budget, p.target_needs, p.event_date,
            p.lat, p.lon
        ])

    return output.getvalue().encode("utf-8-sig")


def render_kp_docx(
        client_name: str,
        inn: str,
        project_title: str,
        cost_price: float,
        optimal_price: float,
        min_price: float,
        margin_percent: float,
        work_types: List[str]
) -> io.BytesIO:
    """Генерация персонализированного файла Word на основе шаблона."""
    ensure_kp_template_exists()
    doc = DocxTemplate(TEMPLATE_PATH)

    items = [
        {"name": f"Цифровой сервис: {wt}", "scale": "1 компл.",
         "price": f"{round(optimal_price / max(len(work_types), 1), 2):,}"}
        for wt in work_types
    ]

    context = {
        "date": datetime.now().strftime("%d.%m.%Y"),
        "client_name": client_name,
        "inn": inn,
        "project_title": project_title,
        "cost_price": f"{cost_price:,.2f}",
        "optimal_price": f"{optimal_price:,.2f}",
        "min_price": f"{min_price:,.2f}",
        "margin_percent": margin_percent,
        "items": items
    }

    doc.render(context)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream