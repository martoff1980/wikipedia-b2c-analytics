import requests
from typing import List, Dict, Any

USER_AGENT = "WikipediaB2CAnalyticsBot/1.0 (learning_app_research@example.com)"


def search_wikipedia_title(topic: str, lang: str) -> str:
    """Пошук точної назви статті мовою розділу,
    якщо передано загальний термін."""

    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": topic,
        "format": "json",
        "srlimit": 1,
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=5)
        data = res.json()
        search_res = data.get("query", {}).get("search", [])
        if search_res:
            return search_res[0]["title"].replace(" ", "_")
    except Exception:
        pass
    return topic.replace(" ", "_")


def fetch_monthly_pageviews(
    article: str, lang: str, start_date: str, end_date: str
) -> List[Dict[str, Any]]:
    """Отримання щомісячної статистики з Wikimedia Analytics API."""
    project = f"{lang}.wikipedia.org"
    # Формат API:
    url = (
        f"https://wikimedia.org/api/rest_v1/metrics/pageviews/"
        f"per-article/{project}/all-access/user/{article}/"
        f"monthly/{start_date}/{end_date}"
    )
    headers = {"User-Agent": USER_AGENT}

    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        return []

    items = res.json().get("items", [])
    result = []
    for item in items:
        timestamp = item["timestamp"]  # YYYYMMDD00
        views = item["views"]
        date_str = f"{timestamp[:4]}-{timestamp[4:6]}"
        result.append({"date": date_str, "views": views})
    return result
