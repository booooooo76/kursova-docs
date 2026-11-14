# Лаб.9, Завд.1 — Forensic-аудит SQALE-моделі open-source системи

## Картка об'єкта аудиту

| Поле | Значення |
|---|---|
| Проєкт | **lear** — Legal Entities and Asset Registry (BC Registries, уряд Британської Колумбії) |
| Призначення | державний реєстр юридичних осіб: реєстрація компаній, подання заяв (filings), продовження юрисдикції (continuation-in), ліквідація; бекенд `legal-api` на Flask + SQLAlchemy + PostgreSQL |
| Репозиторій | https://github.com/bcgov/lear |
| Організація SonarCloud | `bcgov-sonarcloud` (Province of British Columbia) |
| Project key | `bcgov_lear` |
| Дашборд | https://sonarcloud.io/project/overview?id=bcgov_lear |
| Аналіз | Autoscan, 2026-11-13T17:56:07Z, профіль «Sonar way comprehensive» |
| Мови (ncloc) | py 144 304, js 72 142, plsql 18 167, yaml 12 167, web 11 184, ipynb 6 283, shell 5 570, ... |

Критерій масштабу: ncloc = **271 030 ≥ 50 000** — виконано.

## Протокол хмарного API-виклику

```
curl -s "https://sonarcloud.io/api/measures/component?component=bcgov_lear&metricKeys=sqale_index,ncloc,sqale_rating" -o docs/lab9/report.json
```

Те саме робить `scripts/lab9_sonarcloud.ps1`. API публічне, токен не потрібен. Відповідь `HTTP/1.1 200`,
`Content-Type: application/json` (заголовки — `docs/lab9/data/report.headers.txt`).

Сирий JSON (`docs/lab9/report.json`, знято 14.11.2026):

```json
{"component":{"id":"AXBjoIUIDpWz5XcS6zUL","key":"bcgov_lear","name":"lear","qualifier":"TRK",
 "measures":[{"metric":"ncloc","value":"271030"},
             {"metric":"sqale_index","value":"175583","bestValue":false},
             {"metric":"sqale_rating","value":"1.0","bestValue":true}]}}
```

Для перевірки додатково знято `sqale_debt_ratio`, `development_cost` (`docs/lab9/data/verify_extra.json`).

## Математична паспортизація (SQALE Audit Ledger)

Розрахунок відтворює `tools/sqale_audit.py docs/lab9/report.json`.

| Крок | Формула | Результат |
|---|---|---|
| Борг, людино-годин | 175 583 / 60 | **2 926,38 год** |
| Борг, робочих днів | 2 926,38 / 8 | **365,80 людино-днів** |
| Обсяг написання з нуля | 271 030 × 30 / 60 = 271 030 × 0,5 | 135 515 год |
| TDD | 2 926,38 / 135 515 × 100 % | **2,16 %** |
| Рейтинг за шкалою SQALE | A ≤ 5 % | **A** |
| `sqale_rating` з хмари | 1.0 → A | **A — збігається** |

| Масштаб (ncloc) | Обсяг боргу | TDD | Хмарний рейтинг |
|---|---|---|---|
| 271 030 | 2 926,38 людино-год / 365,80 роб. днів | 2,16 % | 1.0 = A |

## Верифікація хмарних розрахунків

1. `development_cost` = 8 130 900 хв = 271 030 × 30. Отже, SonarCloud справді бере 30 хв на рядок, як у формулі SQALE.
2. `sqale_debt_ratio` = 2,2 % = 175 583 / 8 130 900 × 100 % = 2,159 % (хмара округлює до десятих). Наш TDD 2,16 %
   збігається.
3. `sqale_rating` = 1.0 (A), бо 2,16 % ≤ 5 %. Рейтинг підтверджено незалежно.

## Експертний висновок

Борг lear у абсолютних числах великий: 365 людино-днів, тобто приблизно півтора року роботи одного інженера. Відносно
розміру системи він малий: 2,16 % від вартості написання коду з нуля, рейтинг A з запасом (до межі B ще 2,8 п. п.). Це
типово для зрілого державного проєкту з постійним Autoscan і Quality Gate: борг накопичується, але повільніше, ніж росте
код. Ризик не у відсотку, а в абсолютній сумі: 8 460 code smells означають, що «погасити все» вже не вийде за один
спринт, і борг треба планувати як бюджетну статтю (див. Завд.2).
