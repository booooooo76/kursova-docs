# Kursova PC Shop

Вебзастосунок комп'ютерного магазину із сервісним центром: каталог і продаж техніки, конфігуратор ПК, заявки на
ремонт і встановлення ПЗ, облік постачальників і поставок, адміністрування користувачів. Flask + PostgreSQL, із
вбудованим захистом персональних даних (експорт, право на забуття, згоди).

**База знань (сайт документації): <https://booooooo76.github.io/kursova-docs/>**

## Для кого і що вміє

| Хто | Що робить у системі |
|---|---|
| Відвідувач (guest) | переглядає каталог і новини, збирає кошик |
| Клієнт (authorized) | оформлює замовлення, веде обране, подає заявки на ремонт і ПЗ, керує профілем, згодами й своїми персональними даними |
| Оператор (operator) | веде товари, обробляє замовлення та заявки, публікує новини, працює з постачальниками й поставками |
| Адміністратор (admin) | керує користувачами й правами, дивиться статистику, працює із SQL-консоллю |

## Швидкий старт (Windows, PowerShell)

Потрібно: Python 3.11, PostgreSQL 18, Git.

```powershell
git clone https://github.com/booooooo76/Kursova.git; cd Kursova
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
Copy-Item .env.example .env        # заповнити SECRET_KEY і DB_PASSWORD
.\venv\Scripts\python.exe scripts\demo_db.py          # демо-БД: схема + міграції + синтетичні дані
$env:DB_NAME = "computer_store_demo"; .\venv\Scripts\python.exe app.py
```

Відкрийте <http://localhost:5000>. Перевірка стану: `Invoke-RestMethod http://localhost:5000/api/health` повертає
`status: ok`; 503 з `migrations: missing` означає, що треба виконати `scripts\migrate.py`. Інтерактивна довідка API
працюючого екземпляра: <http://localhost:5000/api/docs>.

## Документація: чотири рівні

| Рівень | Питання | Де |
|---|---|---|
| 1. README | що це і як запустити? | цей файл |
| 2. Developer Docs | як приєднатися до розробки? | [Розробникам](https://booooooo76.github.io/kursova-docs/developer/CONTRIBUTING/) (`docs/developer/`) |
| 3. API Docs | як інтегруватися? | [API](https://booooooo76.github.io/kursova-docs/api/) (`docs/api/openapi.yaml`) |
| 4. Architecture Docs | чому система влаштована саме так? | [Архітектура](https://booooooo76.github.io/kursova-docs/architecture/sdd/) (`docs/architecture/`: SDD, ISD, ADR) |

## Definition of Done для документації

| Що перевіряється | Інструмент | Де запускається |
|---|---|---|
| Контракт API | Spectral, 0 errors (`.spectral.yaml`) | CI `docs.yml` |
| Розмітка Markdown | markdownlint (`.markdownlint.jsonc`) | CI `docs.yml` |
| Посилання й навігація | `mkdocs build --strict` | CI `docs.yml` |
| Актуальність | `review_date` у front matter (`tools/doc_review_dates.py`) | CI `docs.yml` |
| Код і документи разом | `tools/doc_currency.py` | перед злиттям |

Правило: **docs-or-don't-merge** — зміна публічної поведінки не зливається без оновлення `docs/`, OpenAPI та
`CHANGELOG.md` (чек-лист у [CONTRIBUTING](https://booooooo76.github.io/kursova-docs/developer/CONTRIBUTING/)).
