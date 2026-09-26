import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def call_lightweight_agent(user_prompt: str) -> dict:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Обов'язкові заголовки для OpenRouter Ranking
        "HTTP-Referer":
            "https://github.com/martoff1980/wikipedia-b2c-analytics",
        "X-Title": "Wikipedia B2C Analytics Skill Engine",
    }

    payload = {
        # Використовуємо список моделей: якщо перша недоступна/перевантажена,
        # OpenRouter автоматично переключить на наступну
        "models": [
            "anthropic/claude-3.5-haiku",
            "openai/gpt-4o-mini",
            # Автоматичний безкоштовний фоллбек
            "meta-llama/llama-3.3-70b-instruct:free"
        ],
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ти — AI-асистент. "
                    "Твоє завдання — перетворити запит користувача "
                    "на валідний JSON-конфіг для аналізу ринку. "
                    "Повертай ТІЛЬКИ JSON без додаткового тексту чи Markdown."
                )
            },
            {"role": "user", "content": user_prompt}
        ],
        # Низька температура для стабільності структури
        "temperature": 0.1
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    res_data = response.json()

    content = res_data["choices"][0]["message"]["content"]
    return json.loads(content)
