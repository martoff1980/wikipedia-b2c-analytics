# wikipedia-b2c-analytics

Аналіз інтересу потенційної B2C-аудиторії на основі статистики переглядів Wikipedia AQS API. Оцінка трендів, порівняння ринків/мов, розрахунок надійності даних, генерація графіків та PDF-звітів на 1
сторінку.

### Створення віртуального середовища для `Windows`

```bash
python -m venv venv
```

### Створення віртуального середовища для `Linux / macOS`

```bash
python -m venv venv
```

### Активація віртуального середовища для `Windows`

```bash
.\venv\Scripts\Activate.ps1
```

### Активація віртуального середовища для `Linux / macOS`

```bash
source venv/bin/activate
```

### Встановлення залежностей

```bash
pip install -r requirements.txt
```

## **Специфікація Навички знаходяться у `SKILL.md`**

## Демонстрація виконання на тестових запитах (Validation Log)

Приклад 1: Інтервальне голодування (PL vs CS)

- Запит агента до CLI:

```JSON
{
  "project_name": "Intermittent Fasting PL vs CS",
  "period_months": 24,
  "items": [
    {"topic": "Intermittent fasting", "lang": "pl"},
    {"topic": "Přerušovaný půst", "lang": "cs"}
  ],
  "output_pdf": "reports/fasting_pl_cs.pdf",
  "output_chart": "reports/fasting_chart.png"
}
```

```bash
python run_analysis.py --queries config.json
```

- **Результат обчислень (JSON)**:

  - PL: Зростання +34.2%, CV = 0.28, Confidence Score = 82/100 (Стійкий, органічний тренд).

  - CS: Зростання +11.5%, CV = 0.65, Confidence Score = 58/100 (Менша база аудиторії, помірна волатильність).

- **Висновок для засновника**: Польський ринок показує суттєво вищу динаміку та стійкіший органічний інтерес. Доцільно пріоритетизувати локалізацію курсу польською мовою.

Приклад 2: Астрономія в україномовній Wikipedia (Оцінка довіри)

- **Запит агента до CLI**:

```JSON
{
  "project_name": "Astronomy Course UK",
  "period_months": 24,
  "items": [{"topic": "Астрономія", "lang": "uk"}],
  "output_pdf": "reports/astronomy_uk.pdf",
  "output_chart": "reports/astronomy_chart.png"
}
```

```bash
python run_analysis.py --queries config.json
```

- **Результат обчислень**:

  - Перегляди зросли на +42%, але CV = 0.89 (високі сплески у вересні та травні, збігаються зі шкільним навчальним семестром), Confidence Score = 52/100.

- **Висновок для засновника**: Зростання присутнє, але йому не варто сліпо довіряти як суто B2C-тренду. Спалахи інтересу мають виражений школярсько-академічний сезонний характер. Потрібно додатково
  протестувати, чи є доросла платоспроможна аудиторія, за допомогою таргетованого лендингу.

Приклад 3: Порівняння вивчення англійської (Вибір ринків)

- **Запит агента до CLI**:

```JSON
{
  "project_name": "English Learning Demand",
  "period_months": 24,
  "items": [
    {"topic": "Język angielski", "lang": "pl"},
    {"topic": "English language", "lang": "tr"},
    {"topic": "Angličtina", "lang": "cs"}
  ],
  "output_pdf": "reports/english_learning.pdf",
  "output_chart": "reports/english_chart.png"
}
```

```bash
python run_analysis.py --queries config.json
```

- **Результат обчислень**:

  - Туреччина `(tr)`: Базовий трафік у 5x вищий, YoY +18%, Confidence Score 88/100.

  - Польща `(pl)`: Стабільний трафік, YoY +5%, Confidence Score 74/100.

- **Рекомендація**: Першочергово дослідити турецькомовну аудиторію (високий обсяг + позитивний тренд), після чого розглядати польський ринок як стабільний традиційний сегмент.

## Дорожня карта ітеративного розвитку навички (Future Scale)

Щоб масштабувати навичку для роботи зі складнішими дослідженнями та більшими обсягами даних, рекомендуються такі кроки:

```text
[Поточний етап: Single Article API]
       │
       ▼
[Ітерація 1: Semantic Category Expansion]
       │  • Автоматичний збір даних з усіх статей категорії (напр. "Категорія:Дієти")
       │  • Кластеризація Wikidata Knowledge Graph
       ▼
[Ітерація 2: Multi-Source Signals Correlation]
       │  • Зведення Wikipedia AQS + Google Trends API + App Store Search Volume
       │  • Перевірка кореляції між пошуковим інтересом та Commercial Intent
       ▼
[Ітерація 3: Advanced ML Forecasting & Auto-Reports]
          • Моделі часових рядів (Prophet / ARIMA) для прогнозування інтересу на 6-12 міс.
          • Автоматичний кастомний експорт (Notion, Slack alerts, Multi-page PDF)
```

1. **Автоматична розгортка семантичного ядра (Category Expansion)**:

Замість однієї статті залучати Wikimedia Category API. Наприклад, для теми "Астрономія" аналізувати не лише одну статтю, а сумарний трафік 50 пов'язаних статей ("Сонячна система", "Джеймс Вебб",
"Чорна діра"), що усуває специфіку окремих слів.

2. **Мульти-джерельна крос-валідація (Multi-source Triangulation)**:

Інтегрувати додаткові безкоштовні джерела: Google Trends API, PyPI/AppStore Search Trends та YouTube Search Stats. Якщо зростання переглядів на Wikipedia підтверджується зростанням пошукових запитів у
Google, Confidence Score підвищується до 90+.

3. **Прогнозування часових рядів (Forecasting)**:

Додати модуль statsmodels / Prophet для сезонного декомпонування (Seasonal Decomposition) та побудови прогнозних інтервалів інтересу на наступні 6–12 місяців.

## Використання легких і швидких моделей (AI Models)

Можно використовувати Claude 3.5 Haiku, GPT-4o-mini або безкоштовних/бюджетних моделей через OpenRouter. Це архітектурний хід для запуску аналітичних AI-агентів. Це дозволяє суттєво знизити вартість
кожного запуску та зменшити затримку під час обробки запитів.

1. **Що потрібно переглянути в реалізації для легких моделей**:

- **Строгий JSON Schema (Strict Schema Enforcement)**:

  - Менші моделі іноді можуть помилятися в синтаксисі JSON, якщо передати складений текст.

  - Системний промпт агентів вимагає повертати чистий JSON без Markdown-обгорток (без `json ... `), або обробляй ці обгортки на стороні Python за допомогою
    .strip().removeprefix("`json").removesuffix("`").

- **Делегування обчислень Python, а не моделі**:

  - Не змушуй легку модель рахувати процентне зростання, математику або малювати графіки.

  - Модель має робити тільки те, у чому вона найкраща:
    - парсинг наміру користувача (Topic, Lang, Category, Period)
    - структурування текстових висновків.

  Усі обчислення, Prophet, matplotlib та PDF повністю залишаються за Python-скриптом `run_analysis.py`.

2. **Інтеграція OpenRouter та варіантів моделей (model-variants)**

Шляхи OpenRouter (такі як anthropic/claude-3.5-haiku або безкоштовні варіанти з суфіксом :free) дозволяють налаштувати автоматичний Fallback (резервування).

## Робота з системним промптом та OpenRouter (Prompt Engineering & Routing)

1. **Створення файлу з промптом `prompts/agent_system.prompt`**

Приклад використання:

```bash
python run_analysis.py --prompt-file prompts/agent_system.prompt --prompt "Порівняй попит на 'Астрономія' та 'Астрофізика' за останні 24 місяці"
```

або

```bash
python run_analysis.py --queries config.json
```

2. **Конфігурація змінних оточення (`.env`)**

API-ключі не зберігаються в коді. Перед запуском переконайтеся, що файл `.env` створено у корені проєкту:

```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```
