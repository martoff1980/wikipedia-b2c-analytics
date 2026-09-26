import requests
from typing import List, Dict, Any, Tuple
import pandas as pd


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


def get_category_members(
    category_name: str, lang: str, limit: int = 10
) -> List[str]:
    """Витягує список статей із категорії Wikipedia."""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    cat_title = (
        category_name
        if category_name.startswith("Category:")
        or category_name.startswith("Категорія:")
        else f"Category:{category_name}"
    )

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": cat_title,
        "cmtype": "page",
        "cmlimit": limit,
        "format": "json",
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=5)
        data = res.json()
        members = data.get("query", {}).get("categorymembers", [])
        return [m["title"].replace(" ", "_") for m in members]
    except Exception:
        return []


def fetch_aggregated_topic_data(
    item: dict, start_str: str, end_str: str
) -> Tuple[pd.DataFrame, str]:
    """Збирає дані для окремої статті або агрегирує всю категорію."""
    lang = item.get("lang", "en")
    raw_topic = item.get("topic")
    category = item.get("category")

    # Якщо вказана категорія
    if category:
        articles = get_category_members(category, lang, limit=8)
        if not articles:
            articles = [search_wikipedia_title(category, lang)]

        combined_df = pd.DataFrame()
        for art in articles:
            views = fetch_monthly_pageviews(art, lang, start_str, end_str)
            if views:
                df_art = pd.DataFrame(views)
                if combined_df.empty:
                    combined_df = df_art
                else:
                    combined_df = pd.merge(
                        combined_df,
                        df_art,
                        on="date",
                        suffixes=("", "_other"),
                    )
                    combined_df["views"] = (
                        combined_df["views"] + combined_df["views_other"]
                    )
                    combined_df = combined_df[["date", "views"]]

        resolved_name = f"Category:{category} ({len(articles)} pages)"
        return combined_df, resolved_name

    # Стандартний режим для одноі статті
    resolved_article = search_wikipedia_title(raw_topic, lang)
    views_data = fetch_monthly_pageviews(
        resolved_article, lang, start_str, end_str
    )
    return pd.DataFrame(views_data), resolved_article
