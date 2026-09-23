import os
from typing import Dict, List
from datetime import datetime

# Генерація PDF-файлу з аналітичним звітом на 1 сторінку
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Импортируємо модулі для регистрації Unicode шрифтів
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_unicode_fonts():
    """Регистрируємо шрифти з підтримкою кирилиці и латинскої діакрітики."""
    # Шляхи до системних шрифтів DejaVuSans (Linux/Ubuntu/Debian)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    # Для Windows:
    if not os.path.exists(font_path):
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        font_bold_path = "C:\\Windows\\Fonts\\arialbd.ttf"

    # Для macOS:
    if not os.path.exists(font_path):
        font_path = "/Library/Fonts/Arial.ttf"
        font_bold_path = "/Library/Fonts/Arial Bold.ttf"

    try:
        pdfmetrics.registerFont(TTFont("CustomUnicode", font_path))
        pdfmetrics.registerFont(TTFont("CustomUnicode-Bold", font_bold_path))
        return "CustomUnicode", "CustomUnicode-Bold"
    except Exception as e:
        print(
            f"Попередження: Не вдалося загрузити Unicode-шрифт ({e}). "
            "Використовуєтся стандартний Helvetica."
        )
        return "Helvetica", "Helvetica-Bold"


def generate_pdf_report(
    project_name: str,
    summary_results: List[Dict],
    chart_path: str,
    pdf_path: str
):
    """Створення односторінкового PDF-звіту для бізнесу."""
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    # Регистрируємо шрифт з підтримкою UTF-8
    font_name, font_bold_name = register_unicode_fonts()
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName=font_bold_name,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=9,
        leading=13
    )
    bold_style = ParagraphStyle(
        "DocBold",
        parent=body_style,
        fontName=font_bold_name
    )

    elements = []

    # Заголовок
    elements.append(
        Paragraph(f"Аналітичний звіт: {project_name}", title_style)
    )
    elements.append(
        Paragraph(
            f"Дата формування: {datetime.now().strftime('%Y-%m-%d')} | "
            "Джерело: Wikimedia Analytics API",
            body_style,
        )
    )
    elements.append(Spacer(1, 15))

    # Таблиця порівняння
    table_data = [
        [
            Paragraph("<b>Тема / Мова</b>", bold_style),
            Paragraph("<b>Перегляди (всього)</b>", bold_style),
            Paragraph("<b>Зростання (%)</b>", bold_style),
            Paragraph("<b>Волатильність (CV)</b>", bold_style),
            Paragraph("<b>Довіра (0-100)</b>", bold_style),
        ]
    ]
    for item in summary_results:
        metrics = item.get("metrics", {})
        table_data.append(
            [
                Paragraph(
                    f"{item['topic']} ({item['lang'].upper()})", body_style
                ),
                Paragraph(f"{metrics.get('total_views', 0):,}", body_style),
                Paragraph(
                    f"{metrics.get('growth_rate_pct', 0):+0.1f}%", body_style
                ),
                Paragraph(f"{metrics.get('volatility_cv', 0)}", body_style),
                Paragraph(
                    f"{metrics.get('confidence_score', 0)}/100", body_style
                ),
            ]
        )

    t = Table(table_data, colWidths=[180, 100, 90, 90, 80])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FAFC")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 15))

    # Вставка графіка
    if os.path.exists(chart_path):
        elements.append(Image(chart_path, width=540, height=240))
        elements.append(Spacer(1, 15))

    # Ключові висновки та обмеження
    elements.append(
        Paragraph("<b>Аналітичні висновки та рекомендації:</b>", bold_style)
    )
    for item in summary_results:
        m = item.get("metrics", {})
        conf = m.get("confidence_score", 0)
        rec = (
            "Перспективний напрям для гіпотез"
            if conf > 65 and m.get("growth_rate_pct", 0) > 0
            else "Високий ризик / Низька стійкість"
        )
        elements.append(
            Paragraph(
                f"• <b>{item['topic']} ({item['lang']})</b>:"
                f"{rec}. Оцінка довіри {conf}/100.",
                body_style,
            )
        )

    elements.append(Spacer(1, 10))
    elements.append(
        Paragraph(
            "<b>Обмеження аналізу:</b> "
            "Дані переглядів Wikipedia демонструють "
            "загальний інформаційний інтерес органічної аудиторії, "
            "але не гарантують готовність платити за платний B2C-продукт. "
            "Використовуйте ці дані як первинний фільтр перед проведенням "
            "CustDev та CustAcquisition тестування.",
            ParagraphStyle(
                "Limits",
                parent=body_style,
                textColor=colors.HexColor("#718096")
            ),
        )
    )

    doc.build(elements)
