import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List
from datetime import datetime
from dateutil.relativedelta import relativedelta
from prophet import Prophet


def generate_chart_forecast(
    data_map: Dict[str, pd.DataFrame],
    forecast_map: Dict[str, List[Dict]],
    output_path: str,
) -> None:
    """Побудова та збереження тренд-графіка."""
    plt.figure(figsize=(10, 4.5), dpi=300)
    plt.style.use(
        "seaborn-v0_8-whitegrid"
        if "seaborn-v0_8-whitegrid" in plt.style.available
        else "default"
    )

    for label, df in data_map.items():
        if not df.empty:
            plt.plot(
                df["date"],
                df["views"],
                marker="o",
                linewidth=2,
                label=label
            )

        # Линія прогнозу
        if label in forecast_map and forecast_map[label]:
            fc_df = pd.DataFrame(forecast_map[label])
            last_hist = df.iloc[-1]
            fc_dates = [last_hist["date"]] + list(fc_df["date"])
            fc_views = [last_hist["views"]] + list(fc_df["views"])

            plt.plot(
                fc_dates,
                fc_views,
                linestyle="--",
                linewidth=1.8,
                alpha=0.8,
                label=f"{label} (Forecast)",
            )

    plt.title(
        "Динаміка інтересу (Перегляди сторінок Wikipedia)",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Місяць", fontsize=10)
    plt.ylabel("Кількість переглядів", fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.legend(loc="upper left", frameon=True)
    plt.tight_layout()

    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
        exist_ok=True,
    )
    plt.savefig(output_path)
    plt.close()


def forecast_demand_prophet(
    df: pd.DataFrame, forecast_months: int = 6
) -> list[dict]:
    """Будує прогноз тренду на N місяців вперед за допомогою Prophet."""
    # Підготовка даних під формат Prophet (ds = date, y = views)
    prophet_df = df.rename(columns={"date": "ds", "views": "y"}).copy()

    # У Wikipedia AQS дата передається як 'YYYY-MM' -> приводимо до datetime
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"] + "-01")

    # Ініциализація моделі (без графіків і логування)
    model = Prophet(
        yearly_seasonality=False,
        weekly_seasonality=False,
        daily_seasonality=False,
        interval_width=0.80,  # 80% довірчий інтервал
    )

    # Системний вивід Prophet
    model.fit(prophet_df)

    # Створення датафрейма для майбутьних дат
    future = model.make_future_dataframe(periods=forecast_months, freq="MS")
    forecast = model.predict(future)

    # Беремо тільки майбутьні значення
    future_forecast = forecast.tail(forecast_months)

    forecast_data = []
    for _, row in future_forecast.iterrows():
        forecast_data.append({
            "date": row["ds"].strftime("%Y-%m"),
            "views": max(0, int(row["yhat"])),  # yhat — точковий прогноз
            "views_lower": max(0, int(row["yhat_lower"])),
            "views_upper": max(0, int(row["yhat_upper"])),
        })

    return forecast_data


def forecast_demand_fallback(
    df: pd.DataFrame, forecast_months: int = 6
) -> list[dict]:
    """Якщо библиотека prophet не встановлена."""
    views = df["views"].values
    x = np.arange(len(views))
    slope, intercept = np.polyfit(x, views, 1)

    last_date = datetime.strptime(df["date"].iloc[-1], "%Y-%m")
    forecast_data = []

    for i in range(1, forecast_months + 1):
        next_dt = last_date + relativedelta(months=i)
        predicted_views = max(0, int(slope * (len(views) + i - 1) + intercept))
        forecast_data.append({
            "date": next_dt.strftime("%Y-%m"),
            "views": predicted_views,
        })

    return forecast_data


def calculate_metrics_and_forecast(
    df: pd.DataFrame, forecast_months: int = 6
) -> dict[str, Any]:
    """Разрахунок метріки тренду, волатильність, Confidence Score
    та робить прогноз."""
    if df.empty or len(df) < 6:
        return {"error": "Недостатньо даних для аналізу"}

    df = df.sort_values("date").reset_index(drop=True)
    total_views = int(df["views"].sum())
    avg_views = float(df["views"].mean())
    std_views = float(df["views"].std())

    # Волатильность (CV)
    cv = round(std_views / avg_views, 2) if avg_views > 0 else 0.0

    # Зріст (порівняння 1-ої и 2-ої половини периоду)
    half = len(df) // 2
    first_half_avg = df.iloc[:half]["views"].mean()
    second_half_avg = df.iloc[half:]["views"].mean()
    growth_rate = (
        round(
            ((second_half_avg - first_half_avg) / first_half_avg) * 100, 2
        )
        if first_half_avg > 0
        else 0.0
    )

    # Confidence Score
    volume_score = min(40, math.log10(max(total_views, 1)) * 8)
    stability_score = max(0, 30 - (cv * 25))
    trend_score = (
        30 if growth_rate > 5 and cv < 0.6 else (15 if growth_rate > 0 else 5)
    )
    confidence_score = round(
        min(100, volume_score + stability_score + trend_score), 1
    )

    # Спроба використати Prophet, інакше fallback
    try:
        forecast_data = forecast_demand_prophet(
            df, forecast_months=forecast_months
        )
        engine_used = "Prophet (Meta)"
    except Exception:
        # Немає бібліотеки або недостатньо точек для Prophet
        forecast_data = forecast_demand_fallback(
            df, forecast_months=forecast_months
        )
        engine_used = "Linear Fallback"

    # Визначення напрямку тренду за останньою точкою прогнозу
    last_hist_views = df["views"].iloc[-1]
    last_forecast_views = forecast_data[-1]["views"]

    if last_forecast_views > last_hist_views * 1.05:
        forecast_trend = "Upward"
    elif last_forecast_views < last_hist_views * 0.95:
        forecast_trend = "Downward"
    else:
        forecast_trend = "Flat"

    return {
        "total_views": total_views,
        "avg_monthly_views": int(avg_views),
        "growth_rate_pct": growth_rate,
        "volatility_cv": cv,
        "confidence_score": confidence_score,
        "forecast_engine": engine_used,
        "forecast_trend": forecast_trend,
        "forecast_next_months": forecast_data,
    }
