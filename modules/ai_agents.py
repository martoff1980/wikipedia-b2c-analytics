import requests
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def load_system_prompt(
    prompt_path: str = "prompts/agent_system.prompt",
) -> str:
    """Завантаження системного промпту з потрібного файлу."""
    if not os.path.exists(prompt_path):
        # Дефолтный фоллбэк на случай, если файл не найден
        return (
            "Ти — AI-оркестратор. "
            "Перетвори запит користувача на валідний JSON-конфіг. "
            "Повертай ТІЛЬКИ чистий JSON."
        )

    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def call_lightweight_agent(
    user_prompt: str, prompt_file: str = "prompts/agent_system.prompt"
) -> dict:
    # Читання промпту з окремого файлу
    system_instruction = load_system_prompt(prompt_file)

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
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        # Низька температура для стабільності структури
        "temperature": 0.1
    }

    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(payload), timeout=15
        )
        response.raise_for_status()

        res_data = response.json()
        content = res_data["choices"][0]["message"]["content"]

        # Очистка від можливих Markdown-обгорток
        if content.startswith("```"):
            content = content.strip("`").removeprefix("json").strip()

        return json.loads(content)

    except Exception as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message":
                        "Помилка генерації конфігу через OpenRouter: "
                        f"{str(e)}",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)
