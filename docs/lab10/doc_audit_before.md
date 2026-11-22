# Documentation Decay Audit (before, 2026-11-22)

Згенеровано `tools/doc_audit.py`; команди Git та їхній вивід - `docs/lab10/data/git_cli_before.log`.

## Інвентаризаційний реєстр

| ID | Документ | Розташування | Тип | Категорія | Аудиторії | Власник | Що НЕ покрито |
|---|---|---|---|---|---|---|---|
| P1 | README.md | README.md | продукт | експлуатаційна | новачок, бізнес | Загребенюк Б. (booooooo76) | - |
| P2 | SDD docs/sdd.md | docs/sdd.md | продукт | архітектурна | розробники, QA | Загребенюк Б. (booooooo76) | - |
| P3 | ISD docs/isd.md | docs/isd.md | продукт | експлуатаційна | DevOps | Загребенюк Б. (booooooo76) | - |
| P4 | ADR docs/architecture/adr/ | docs/architecture/adr | продукт | архітектурна | розробники | Загребенюк Б. (booooooo76) | - |
| P5 | Регламент docs/maintenance.md | docs/maintenance.md | процес | експлуатаційна | розробники, DevOps | Загребенюк Б. (booooooo76) | - |

## Метрики актуальності

Пороги: вік > 90 дн. підозрілий, > 180 дн. ймовірно застарілий; > 20 комітів коду після останнього оновлення документа = структурний дрейф (⚠).

| ID | Оновлено | Вік, дн. | Статус віку | Комітів документа | Комітів коду всього | Комітів коду після оновлення | Посилань | Змін за 30 дн. |
|---|---|---:|---|---:|---:|---:|---:|---:|
| P1 | 2026-11-22 | 0 | свіжий | 2 | 22 | 0 | 6 | 2 |
| P2 | 2026-11-22 | 0 | свіжий | 2 | 31 | 0 | 10 | 2 |
| P3 | 2026-11-22 | 0 | свіжий | 2 | 26 | 0 | 6 | 2 |
| P4 | 2026-11-22 | 0 | свіжий | 2 | 12 | 0 | 6 | 2 |
| P5 | 2026-11-22 | 0 | свіжий | 1 | 0 | 0 | 5 | 1 |

Коментарі в коді (A19): docstring мають 104 з 368 функцій і класів коду застосунку (28%).
Коміти (A20): 57 з 64 повідомлень у форматі Conventional Commits (89%).

Дрейф схеми БД (A02): у документі 0 таблиць, у реальній схемі (tests/db/schema_base.sql + migrations/) 45. Не описано 45: analytics_events, cart, categories, computer_configurations, config_components, contract_obligations, contracts, delivery_items, delivery_methods, keys, marketing_outbox, news, order_items, orders, payment_methods, privacy_audit_log, product_attributes, product_images, product_reviews, products, promotion_products, promotions, query_results, registration_requests, repair_parts, repair_requests, repair_status_history, repairs, return_items, returns, sale_items, sales, saved_queries, service_orders, service_types, software_requests, software_status_history, sql_execution_log, suppliers, supply_deliveries, user_activity_log, user_consent_history, user_consents, warranties, wishlist. Описано, але не існує 0: -.

## Матриця вердиктів

| ID | Документ | Діагноз | Вердикт | Обґрунтування |
|---|---|---|---|---|
| P1 | README.md | паспорт | **оновити** | вхід у проєкт; цикл 90 днів |
| P2 | SDD docs/sdd.md | паспорт | **оновити** | будова системи; цикл 180 днів |
| P3 | ISD docs/isd.md | паспорт | **оновити** | розгортання; цикл 90 днів |
| P4 | ADR docs/architecture/adr/ | паспорт | **оновити** | рішення; цикл 180 днів |
| P5 | Регламент docs/maintenance.md | паспорт | **оновити** | регламент; цикл 90 днів |
