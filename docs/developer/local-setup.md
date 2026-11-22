---
title: Локальне середовище
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-02-20
tags:
  - developer
  - ops
---

# Локальне середовище розробника

Швидкий старт на демо-БД є в README (рівень 1). Тут — повна інструкція для розробки.

## 1. Інструменти

| Що | Версія | Навіщо |
|---|---|---|
| Python | 3.11 | застосунок і інструменти якості (`venv`) |
| PostgreSQL | 18, служба `postgresql-x64-18` | робоча, тестова й демо-БД |
| Git | 2.4x | хуки в `.githooks/` |
| Docker Desktop | для SonarQube і OpenAPI Generator | необов'язково |
| Node.js | 22 | markdownlint, Spectral через `npx` |

## 2. Встановлення

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt -r requirements-docs.txt
Copy-Item .env.example .env          # SECRET_KEY, DB_PASSWORD; решта має значення за замовчуванням
git config core.hooksPath .githooks  # хук pre-commit: gitleaks + lizard
```

## 3. Бази даних

| БД | Як отримати |
|---|---|
| демо `computer_store_demo` | `python scripts\demo_db.py` — схема, міграції, синтетичні користувачі |
| робоча `computer_store` | створити БД, `psql -f tests\db\schema_base.sql`, потім `python scripts\migrate.py` |
| тестова `<DB_NAME>_test` | pytest створює сам при кожному запуску |

Після запуску застосунку перевірте `GET /api/health`: `migrations: missing` означає, що міграції не застосовано.

## 4. Щоденні команди

```powershell
.\venv\Scripts\python.exe app.py                 # застосунок на :5000, довідка API на /api/docs
.\venv\Scripts\python.exe -m pytest -q           # тести (потрібен PostgreSQL)
.\venv\Scripts\python.exe -m mkdocs serve        # сайт документації на :8000
npx @stoplight/spectral-cli@6.11.1 lint docs/api/openapi.yaml
npx markdownlint-cli2@0.14.0 "docs/**/*.md" README.md
.\venv\Scripts\python.exe tools\doc_currency.py  # код і документи синхронні
```

## 5. Клавіатура в інтерфейсі

F1 — довідка зі скороченнями; Esc — закрити діалог або назад; Enter — наступне поле або надіслати форму;
Ctrl + S — зберегти форму.

## Пов'язані

[[CONTRIBUTING]] · [[code-standards]] · [[isd]] #developer #ops
