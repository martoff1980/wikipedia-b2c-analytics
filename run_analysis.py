import argparse
import json
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

from modules.generate_report import generate_pdf_report
from modules.fetch_pageviews import (
    search_wikipedia_title,
    fetch_monthly_pageviews
)
from modules.analyze_trends import (
    calculate_metrics,
    generate_chart
)


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


def main():
    parser = argparse.ArgumentParser(
        description="Wikipedia B2C Market Demand Skill Engine"
    )
    parser.add_argument(
        "--queries",
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
    start_dt = end_dt - timedelta(days=months * 30)
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

    output_response = {
        "status": "success",
        "project_name": project_name,
        "results": summary_results,
        "artifacts": {"pdf_report": output_pdf, "chart_image": output_chart},
    }

    print(json.dumps(output_response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
