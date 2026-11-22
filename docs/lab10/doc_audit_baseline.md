# Documentation Decay Audit (baseline, 2026-11-22)

Згенеровано `tools/doc_audit.py`; команди Git та їхній вивід - `docs/lab10/data/git_cli_baseline.log`.

## Інвентаризаційний реєстр

| ID | Документ | Розташування | Тип | Категорія | Аудиторії | Власник | Що НЕ покрито |
|---|---|---|---|---|---|---|---|
| A01 | README.md | README.md | продукт | експлуатаційна | новачок, бізнес, розробники | Загребенюк Б. (booooooo76) | усі: файлу немає - ні призначення системи, ні швидкого старту |
| A02 | Схема БД (database/create_db.txt, users_table_sql.txt) | database/create_db.txt, database/users_table_sql.txt | продукт | архітектурна | розробники, QA | Загребенюк Б. (booooooo76) | розробники: 19 актуальних таблиць не описані, 2 описані таблиці вже не існують |
| A03 | Тестові дані database/insert_sample_data.txt | database/insert_sample_data.txt | продукт | експлуатаційна | розробники, QA | Загребенюк Б. (booooooo76) | QA: дані під стару схему, частина таблиць уже інша |
| A04 | Діаграма класів 777.mb (Mermaid) | 777.mb | продукт | архітектурна | розробники | Загребенюк Б. (booooooo76) | розробники: немає services/ (Лаб.8), privacy/ (Лаб.4), контрактів і БД; класи User/Order не існують у коді як класи |
| A05 | Інструкція клавіатурних скорочень keyboard_user_manual.txt | keyboard_user_manual.txt | продукт | технічна | бізнес | Загребенюк Б. (booooooo76) | новачок: не пов'язана з README, не видно, що вона існує |
| A06 | QUICK_TEST_SCENARIO.txt | QUICK_TEST_SCENARIO.txt | процес | технічна | QA | Загребенюк Б. (booooooo76) | QA: лише клавіатура, нічого про замовлення, приватність, API |
| A07 | TESTING_CHECKLIST.txt | TESTING_CHECKLIST.txt | процес | технічна | QA | Загребенюк Б. (booooooo76) | QA: чекліст лише для клавіатури |
| A08 | SCREENSHOTS_GUIDE.txt | SCREENSHOTS_GUIDE.txt | процес | технічна | бізнес | Загребенюк Б. (booooooo76) | - |
| A09 | Нотатка dd | dd | процес | технічна | розробники | Загребенюк Б. (booooooo76) | - |
| A10 | .env.example | .env.example | продукт | експлуатаційна | DevOps, новачок | Загребенюк Б. (booooooo76) | новачок: не сказано, де взяти БД і як застосувати міграції |
| A11 | requirements.txt, requirements-dev.txt | requirements.txt, requirements-dev.txt | продукт | експлуатаційна | DevOps, розробники | Загребенюк Б. (booooooo76) | - |
| A12 | CI .github/workflows/quality-metrics.yml | .github/workflows/quality-metrics.yml | продукт | експлуатаційна | DevOps | Загребенюк Б. (booooooo76) | DevOps: ніде не описано словами, що робить конвеєр і де дивитися артефакт |
| A13 | Pre-commit хук (.githooks/pre-commit + docs/lab6/precommit.md) | .githooks/pre-commit, docs/lab6/precommit.md | продукт | експлуатаційна | розробники, DevOps | Загребенюк Б. (booooooo76) | новачок: не сказано, що треба виконати git config core.hooksPath .githooks |
| A14 | SonarQube (sonar-project.properties, scan.ps1) | sonar-project.properties, scan.ps1 | продукт | експлуатаційна | DevOps, QA | Загребенюк Б. (booooooo76) | DevOps: не описано, що SonarQube підіймається окремо (sonarqube-server, Docker) |
| A15 | Політики приватності docs/lab4/*.md (consent, logging_policy, pii_inventory, anonymization, personal_data_export) | docs/lab4/consent.md, docs/lab4/logging_policy.md, docs/lab4/pii_inventory.md, docs/lab4/anonymization.md, docs/lab4/personal_data_export.md | продукт | технічна | розробники, QA, бізнес | Загребенюк Б. (booooooo76) | бізнес: розкидані по папці лаби, без єдиного входу |
| A16 | Запобігання секретам docs/lab3/secrets_prevention.md | docs/lab3/secrets_prevention.md | продукт | експлуатаційна | DevOps, розробники | Загребенюк Б. (booooooo76) | - |
| A17 | Звіти-протоколи лаб у репозиторії docs/lab3, lab5-lab9 (sca_triage, measurement_protocol, halstead, cfg, chapin, hotspots, ck_mood, god_object, inheritance, sqale, economics, fpa_ucp) | docs/lab3/sca_triage.md, docs/lab5/measurement_protocol.md, docs/lab6/halstead.md, docs/lab6/cfg.md, docs/lab7/chapin.md, docs/lab7/hotspots.md, docs/lab8/ck_mood.md, docs/lab8/god_object.md, docs/lab8/inheritance.md, docs/lab9/sqale.md, docs/lab9/economics.md, docs/lab9/fpa_ucp.md | процес | архітектурна | бізнес, розробники | Загребенюк Б. (booooooo76) | новачок: це історія рішень, а не опис поточної системи |
| A18 | FINANCIAL_LEDGER.md | FINANCIAL_LEDGER.md | процес | технічна | бізнес | Загребенюк Б. (booooooo76) | - |
| A19 | Коментарі й docstring-и в коді | - | продукт | технічна | розробники | Загребенюк Б. (booooooo76) | розробники: app.py (1 281 рядок) має мало docstring-ів, маршрути не описані |
| A20 | Повідомлення комітів Git | - | процес | технічна | розробники | Загребенюк Б. (booooooo76) | розробники: ранні коміти без змісту (1.2, 1.3, 1.4) |
| A21 | Звіти лабораторних робіт (docx/pdf поза репозиторієм) | - | процес | архітектурна | бізнес | Загребенюк Б. (booooooo76) | розробники: поза Git, недоступні команді |
| A22 | Трекер задач | - | процес | технічна | розробники, QA | Загребенюк Б. (booooooo76) | усі: трекера немає (GitHub Issues порожні), задачі живуть у нотатках на кшталт dd |

## Метрики актуальності

Пороги: вік > 90 дн. підозрілий, > 180 дн. ймовірно застарілий; > 20 комітів коду після останнього оновлення документа = структурний дрейф (⚠).

| ID | Оновлено | Вік, дн. | Статус віку | Комітів документа | Комітів коду всього | Комітів коду після оновлення | Посилань | Змін за 30 дн. |
|---|---|---:|---|---:|---:|---:|---:|---:|
| A01 | - | - | файлу немає | 0 | 30 | 30 ⚠ | 0 | 0 |
| A02 | 2025-10-17 | 401 | ймовірно застарілий | 1 | 12 | 11 | 0 | 0 |
| A03 | 2025-10-17 | 401 | ймовірно застарілий | 1 | 4 | 4 | 0 | 0 |
| A04 | 2025-11-27 | 360 | ймовірно застарілий | 1 | 30 | 23 ⚠ | 0 | 0 |
| A05 | 2025-11-14 | 373 | ймовірно застарілий | 1 | 6 | 4 | 0 | 0 |
| A06 | 2025-11-14 | 373 | ймовірно застарілий | 1 | 7 | 5 | 0 | 0 |
| A07 | 2025-11-14 | 373 | ймовірно застарілий | 1 | 7 | 5 | 0 | 0 |
| A08 | 2025-11-14 | 373 | ймовірно застарілий | 1 | 7 | 5 | 0 | 0 |
| A09 | 2025-11-14 | 373 | ймовірно застарілий | 1 | 17 | 15 | 1 | 0 |
| A10 | 2026-10-04 | 49 | свіжий | 2 | 3 | 0 | 5 | 0 |
| A11 | 2026-11-14 | 8 | свіжий | 8 | 30 | 0 | 9 | 3 |
| A12 | 2026-10-31 | 22 | свіжий | 1 | 3 | 0 | 1 | 1 |
| A13 | 2026-10-24 | 29 | свіжий | 3 | 1 | 0 | 7 | 2 |
| A14 | 2026-09-13 | 70 | свіжий | 1 | 30 | 19 | 1 | 0 |
| A15 | 2026-10-18 | 35 | свіжий | 6 | 10 | 4 | 0 | 0 |
| A16 | 2026-10-04 | 49 | свіжий | 1 | 2 | 1 | 0 | 0 |
| A17 | 2026-11-14 | 8 | свіжий | 15 | 30 | 0 | 5 | 13 |
| A18 | 2026-11-14 | 8 | свіжий | 1 | 1 | 0 | 3 | 1 |
| A19 | - | - | н/д (не файл) | 0 | 30 | 0 | 0 | 0 |
| A20 | - | - | н/д (не файл) | 0 | 0 | 0 | 0 | 0 |
| A21 | - | - | н/д (не файл) | 0 | 0 | 0 | 0 | 0 |
| A22 | - | - | н/д (не файл) | 0 | 0 | 0 | 0 | 0 |

Коментарі в коді (A19): docstring мають 101 з 368 функцій і класів коду застосунку (27%).
Коміти (A20): 52 з 59 повідомлень у форматі Conventional Commits (88%).

Дрейф схеми БД (A02): у документі 23 таблиць, у реальній схемі (tests/db/schema_base.sql + migrations/) 45. Не описано 24: analytics_events, cart, delivery_methods, marketing_outbox, news, order_items, orders, payment_methods, privacy_audit_log, product_attributes, product_images, product_reviews, promotion_products, promotions, query_results, repair_requests, repair_status_history, saved_queries, software_requests, software_status_history, sql_execution_log, user_consent_history, user_consents, wishlist. Описано, але не існує 2: clients, employees.

## Матриця вердиктів

| ID | Документ | Діагноз | Вердикт | Обґрунтування |
|---|---|---|---|---|
| A01 | README.md | прогалина | **оновити** | головний вхід у проєкт відсутній; створити з призначенням, швидким стартом і шляхом онбордингу (Завд.2) |
| A02 | Схема БД (database/create_db.txt, users_table_sql.txt) | Documentation Decay | **deprecated** | описує схему жовтня 2025 (23 таблиці); реальна схема 40 таблиць + 5 таблиць міграцій Лаб.4; джерело правди тепер tests/db/schema_base.sql + migrations/, модель даних переноситься в SDD |
| A03 | Тестові дані database/insert_sample_data.txt | Documentation Decay | **deprecated** | наповнення замінено синтетичними фабриками tests/factories.py і scripts/demo_db.py (Лаб.4) |
| A04 | Діаграма класів 777.mb (Mermaid) | Documentation Decay | **видалити** | незрозуміле ім'я й розширення, описує модель листопада 2025; замінюється C4-діаграмою в docs/sdd.md |
| A05 | Інструкція клавіатурних скорочень keyboard_user_manual.txt | Dead Documentation | **оновити** | функція F1/скорочення досі працює (keyboard-shortcuts.js не змінювався), але документ писався як додаток курсової і не має споживача; перенести суть у README (розділ для користувача) |
| A06 | QUICK_TEST_SCENARIO.txt | Dead Documentation | **видалити** | одноразовий сценарій демонстрації курсової (листопад 2025); подія минула, споживача немає; функції QA покриває tests/ (315 тестів) |
| A07 | TESTING_CHECKLIST.txt | Dead Documentation | **видалити** | таблиця для розділу курсової; історичний запис, що вже потрапив у курсову роботу |
| A08 | SCREENSHOTS_GUIDE.txt | Dead Documentation | **видалити** | інструкція, які скріни зробити для курсової; мета досягнута |
| A09 | Нотатка dd | Dead Documentation | **видалити** | однорядкова чернетка-нагадування про баг без назви й контексту; місце таким нотаткам - трекер задач; єдиний збіг git grep - HTML-тег <dd> у шаблоні, тобто хибний |
| A10 | .env.example | актуальний | **оновити** | відповідає config.py; додати посилання з README та ISD |
| A11 | requirements.txt, requirements-dev.txt | актуальний | **оновити** | версії закріплені, коментарі пояснюють, навіщо інструмент; підтримувати разом із кодом |
| A12 | CI .github/workflows/quality-metrics.yml | актуальний | **оновити** | конфігурація жива; опис стадій і тригерів переноситься в ISD |
| A13 | Pre-commit хук (.githooks/pre-commit + docs/lab6/precommit.md) | актуальний | **оновити** | актуальний; крок налаштування хука додати в онбординг README |
| A14 | SonarQube (sonar-project.properties, scan.ps1) | на межі дрейфу | **оновити** | 70 днів без змін, а код застосунку отримав 19 комітів (поріг 20); конфіг працює (Лаб.8), опис запуску перенести в ISD |
| A15 | Політики приватності docs/lab4/*.md (consent, logging_policy, pii_inventory, anonymization, personal_data_export) | ризик Dead | **оновити** | зміст відповідає privacy/ (4 коміти коду після оновлення), але жоден файл репозиторію на них не посилається і за 30 днів їх не відкривали в Git; дати вхід із SDD (компонент Privacy) |
| A16 | Запобігання секретам docs/lab3/secrets_prevention.md | ризик Dead | **оновити** | зміст актуальний, але без посилань; хук відтоді отримав етап lizard (Лаб.6) - описати обидва етапи в ISD |
| A17 | Звіти-протоколи лаб у репозиторії docs/lab3, lab5-lab9 (sca_triage, measurement_protocol, halstead, cfg, chapin, hotspots, ck_mood, god_object, inheritance, sqale, economics, fpa_ucp) | історичний запис | **deprecated** | документація процесу: фіксує факт на дату лаби й не має оновлюватися; позначити як архів (docs/labN/), поточну архітектуру описують SDD та ADR |
| A18 | FINANCIAL_LEDGER.md | історичний запис | **deprecated** | згенерований артефакт Лаб.9 про чужий проєкт; лишається в корені за вимогою методички Лаб.9 |
| A19 | Коментарі й docstring-и в коді | частково | **оновити** | нові модулі (privacy/, services/) задокументовані, старі (app.py, routers/) - ні; див. покриття docstring-ами |
| A20 | Повідомлення комітів Git | частково | **оновити** | з Лаб.3 - Conventional Commits; ранні коміти неінформативні, але історію не переписуємо |
| A21 | Звіти лабораторних робіт (docx/pdf поза репозиторієм) | історичний запис | **deprecated** | здані звіти фіксують факт; поза контуром Documentation as Code |
| A22 | Трекер задач | прогалина | **оновити** | для одноосібного проєкту допустимо, але відомі дефекти (з dd) треба кудись фіксувати |
