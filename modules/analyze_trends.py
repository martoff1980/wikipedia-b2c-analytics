import os
import math
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any


def calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Розрахунок трендів, волатильності та коефіцієнта довіри."""

    if df.empty or len(df) < 6:
        return {"error": "Недостатньо даних для аналізу"}

    df = df.sort_values("date")
    total_views = df["views"].sum()
    avg_views = df["views"].mean()
    std_views = df["views"].std()

    # Коефіцієнт варіації (оцінка сплесків/волатильності)
    cv = std_views / avg_views if avg_views > 0 else 0

    # Розрахунок YoY або сумарного зростання за період
    first_half = df.iloc[: len(df) // 2]["views"].mean()
    second_half = df.iloc[len(df) // 2:]["views"].mean()
    growth_rate = (
        ((second_half - first_half) / first_half * 100)
        if first_half > 0
        else 0
    )

    # Confidence Score (0-100)
    # Базовий обсяг (до 40 балів): більше переглядів = вища репрезентативність
    volume_score = min(40, math.log10(max(total_views, 1)) * 8)

    # Стабільність (до 30 балів): висока волатильність (CV > 0.8) знижує довіру
    stability_score = max(0, 30 - (cv * 25))

    # Тривалість та наявність тренду (до 30 балів)
    trend_score = (
        30
        if growth_rate > 5 and cv < 0.6
        else (15 if growth_rate > 0 else 5)
    )

    confidence_score = round(
        min(100, volume_score + stability_score + trend_score), 1
    )

    return {
        "total_views": int(total_views),
        "avg_monthly_views": int(avg_views),
        "growth_rate_pct": round(growth_rate, 2),
        "volatility_cv": round(cv, 2),
        "confidence_score": confidence_score,
    }


def generate_chart(data_map: Dict[str, pd.DataFrame], output_path: str):
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
