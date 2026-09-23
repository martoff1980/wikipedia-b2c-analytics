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
