import argparse
import json
import os
import sys
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pathlib import Path

from modules.generate_report import generate_pdf_report
from modules.fetch_pageviews import (
    search_wikipedia_title,
    fetch_monthly_pageviews,
    fetch_aggregated_topic_data,
)
from modules.analyze_trends import (
    calculate_metrics,
    generate_chart,
    generate_chart_forecast,
    calculate_metrics_and_forecast,
)
from modules.ai_agents import call_lightweight_agent

def parse_queries_input(queries_input: str) -> dict:
    """ Парсить вхідні дані -- JSON рядок або
    шлях до файлу JSON. """

    queries_input = queries_input.strip()

    try:
        return json.loads(queries_input)
    except (json.JSONDecodeError, TypeError):
        pass

    try:
        if os.path.isfile(queries_input):
            with open(queries_input, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"Помилка читання файла JSON: {str(e)}",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    print(
        json.dumps(
            {
                "status": "error",
                "message":
                    "Некоректний формат JSON. "
                    "Передайте валідний JSON-рядок або шлях до .json файлу.",
            },
            ensure_ascii=False,
        )
    )
    sys.exit(1)


def demo_validation_log():
    """ Демонстраційна функція для валідаційного логування """
    parser = argparse.ArgumentParser(
        description="Wikipedia B2C Market Demand Skill Engine"
    )
    parser.add_argument(
        "--queries",
        "-q",
        type=str,
        required=True,
        help="JSON string with parameters"
    )
    args = parser.parse_args()

    # Парсінг аргументів (JSON string vs File Path)
    config = parse_queries_input(args.queries)

    project_name = config.get("project_name", "B2C Research")
    months = config.get("period_months", 24)
    items = config.get("items", [])
    output_pdf = config.get("output_pdf", "reports/report.pdf")
    output_chart = config.get("output_chart", "reports/chart.png")

    end_dt = datetime.now()
    start_dt = end_dt - relativedelta(months=months)
    start_str = start_dt.strftime("%Y%m0100")
    end_str = end_dt.strftime("%Y%m0100")

    summary_results = []
    data_map = {}

    for item in items:
        raw_topic = item["topic"]
        lang = item["lang"]

        # Точне визначення сторінки
        article_title = search_wikipedia_title(raw_topic, lang)
        views_data = fetch_monthly_pageviews(
            article_title,
            lang,
            start_str,
            end_str
        )

        df = pd.DataFrame(views_data)
        metrics = calculate_metrics(df)

        label = f"{raw_topic} [{lang}]"
        data_map[label] = df

        summary_results.append(
            {
                "topic": raw_topic,
                "resolved_article": article_title,
                "lang": lang,
                "metrics": metrics,
            }
        )

    # Генерація графіків та звіту
    generate_chart(data_map, output_chart)
    generate_pdf_report(
        project_name,
        summary_results,
        output_chart,
        output_pdf
    )

    # Фінальний вивід
    output_response = {
        "status": "success",
        "project_name": project_name,
        "results": summary_results,
        "artifacts": {"pdf_report": output_pdf, "chart_image": output_chart},
    }

    print("============ Validation Log ============")
    print(json.dumps(output_response, ensure_ascii=False, indent=2))
    print("========================================")


def demo_future_scale():
    """ Демонстраційна функція для масштабування з прогнозом """
    parser = argparse.ArgumentParser(
        description="Wikipedia B2C Market Demand Skill Engine"
    )
    parser.add_argument(
        "--queries",
        "-q",
        type=str,
        required=True,
        help="JSON string or path to JSON file with parameters",
    )
    args = parser.parse_args()

    # Парсінг аргументів (JSON string vs File Path)
    config = parse_queries_input(args.queries)

    project_name = config.get("project_name", "B2C Research")
    months = config.get("period_months", 24)
    items = config.get("items", [])

    output_pdf = Path(config.get(
        "output_pdf", "reports/market_research_report.pdf"
        )
    )
    output_pdf = str(output_pdf.with_name(
        f"{output_pdf.stem}_with_forecast{output_pdf.suffix}"
        )
    )

    output_chart = Path(config.get(
        "output_chart", "reports/market_research_report.png"
        )
    )
    output_chart = output_chart.with_name(
        f"{output_chart.stem}_with_forecast{output_chart.suffix}"
    )

    if not items:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Список 'items' порожній або відсутній.",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    # Точковий розрахунок часового діапазону для збору даних
    end_dt = datetime.now()
    start_dt = end_dt - relativedelta(months=months)
    start_str = start_dt.strftime("%Y%m0100")
    end_str = end_dt.strftime("%Y%m0100")

    summary_results = []
    data_map = {}
    forecast_map = {}

    # Основний цикл обработки (підтримка категорій та одиночних статтей)
    for item in items:
        lang = item.get("lang")
        topic_label = item.get("topic") or item.get("category")

        if not topic_label or not lang:
            continue

        try:
            df, resolved_name = fetch_aggregated_topic_data(
                item, start_str, end_str
            )
            metrics = calculate_metrics_and_forecast(df)

            label = f"{topic_label} [{lang}]"
            data_map[label] = df
            forecast_map[label] = metrics.get("forecast_next_months", [])

            summary_results.append(
                {
                    "topic": item.get("topic"),
                    "category": item.get("category"),
                    "resolved_article": resolved_name,
                    "lang": lang,
                    "metrics": metrics,
                }
            )
        except Exception as err:
            summary_results.append(
                {
                    "topic": topic_label,
                    "lang": lang,
                    "error": f"Не вдалося отримати дані: {str(err)}",
                }
            )

    # Генерація артефактів (Графік з прогнозом + PDF)
    try:
        generate_chart_forecast(data_map, forecast_map, output_chart)
        generate_pdf_report(
            project_name, summary_results, output_chart, output_pdf
        )
    except Exception as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"Помилка генерації артефактів: {str(e)}",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    # Фінальний вивід
    output_response = {
        "status": "success",
        "project_name": project_name,
        "results": summary_results,
        "artifacts": {"pdf_report": output_pdf, "chart_image": output_chart},
    }

    print("============ Future Scale ==============")
    print(json.dumps(
        output_response, ensure_ascii=False, indent=2, default=str)
    )
    print("========================================")

def demo_with_ai_agents():
    """ Демонстраційна функція для інтеграції з AI-агентами """

    parser = argparse.ArgumentParser(
        description="Wikipedia B2C Market Demand Skill Engine"
    )

    # Робимо аргументи взаїмовисключнимии або опціональними
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--queries",
        "-q",
        type=str,
        help="JSON string or path to JSON file with parameters",
    )
    group.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Natural language prompt for LLM agent",
    )

    parser.add_argument(
        "--prompt-file",
        type=str,
        default="prompts/agent_system.prompt",
        help="Path to custom system prompt file "
            "(default: prompts/agent_system.prompt)",
    )

    args = parser.parse_args()

    # Конфигурація (через LLM Agent или прямим парсінгом)
    if args.prompt:
        print(
            f"[INFO] Генерація конфігурації через OpenRouter для запиту: '{args.prompt}'..."
        )
        config = call_lightweight_agent(
            user_prompt=args.prompt, prompt_file=args.prompt_file
        )
    elif args.queries:
        config = parse_queries_input(args.queries)
    else:
        parser.error("Необхідно вказати --queries або --prompt")

    project_name = config.get("project_name", "B2C Research")
    months = config.get("period_months", 24)
    items = config.get("items", [])
    output_pdf = Path(config.get(
        "output_pdf", "reports/market_research_report.pdf"
        )
    )
    
    output_pdf = str(output_pdf.with_name(
        f"{output_pdf.stem}_with_ai_agents{output_pdf.suffix}"
        )
    )

    output_chart = Path(config.get(
        "output_chart", "reports/market_research_report.png"
        )
    )
    output_chart = output_chart.with_name(
        f"{output_chart.stem}_with_ai_agents{output_chart.suffix}"
    )

    if not items:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Список 'items' порожній або відсутній у конфігурації.",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    # Точковий розрахунок часового діапазону для збору даних
    end_dt = datetime.now()
    start_dt = end_dt - relativedelta(months=months)
    start_str = start_dt.strftime("%Y%m0100")
    end_str = end_dt.strftime("%Y%m0100")

    summary_results = []
    data_map = {}
    forecast_map = {}

    # Основний цикл обработки (підтримка категорій та одиночних статтей)
    for item in items:
        lang = item.get("lang", "en")
        topic_label = item.get("topic") or item.get("category")

        if not topic_label:
            continue

        try:
            df, resolved_name = fetch_aggregated_topic_data(
                item, start_str, end_str
            )
            metrics = calculate_metrics_and_forecast(df)

            label = f"{topic_label} [{lang}]"
            data_map[label] = df
            forecast_map[label] = metrics.get("forecast_next_months", [])

            summary_results.append(
                {
                    "topic": item.get("topic"),
                    "category": item.get("category"),
                    "resolved_article": resolved_name,
                    "lang": lang,
                    "metrics": metrics,
                }
            )
        except Exception as err:
            summary_results.append(
                {
                    "topic": topic_label,
                    "lang": lang,
                    "error": f"Не вдалося отримати дані: {str(err)}",
                }
            )

    # Генерація артефактів (Графік з прогнозом + PDF)
    try:
        generate_chart(data_map, forecast_map, output_chart)
        generate_pdf_report(
            project_name, summary_results, output_chart, output_pdf
        )
    except Exception as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": f"Помилка генерації артефактів: {str(e)}",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    # Фінальний вивід
    output_response = {
        "status": "success",
        "project_name": project_name,
        "results": summary_results,
        "artifacts": {"pdf_report": output_pdf, "chart_image": output_chart},
    }
    
    print("============ AI Agent and Future Scale  ==============")
    print(json.dumps(output_response, ensure_ascii=False, indent=2))
    print("========================================")

if __name__ == "__main__":
    demo_validation_log()
    demo_future_scale()
    demo_with_ai_agents()
