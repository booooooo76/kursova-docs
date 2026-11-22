---
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-04-16
tags:
  - architecture
---

# Лаб.4: PII Inventory (інвентаризація персональних даних)

Усі значення в документі синтетичні або взагалі відсутні: реальних персональних даних тут немає.
Машинний еквівалент цього документа — `privacy/policy.py`; його повноту перевіряє `tests/test_pii_inventory.py`.

## 1. Система

| | |
|---|---|
| Проєкт | «Kursova PC Shop»: інтернет-магазин комп'ютерної техніки |
| Стек | Python 3.11, Flask, Flask-Login, psycopg2 (сирий SQL через `models/database.py`, без ORM), PostgreSQL 18 |
| Сховище | Одна БД PostgreSQL, 40 таблиць до Лаб.4 (+ `privacy_audit_log` і 4 таблиці згод, див. міграції 001 і 002); 4 з них (`service_orders` і застарілі `repairs`, `returns`, `sales`) посилаються на користувача без зовнішнього ключа (див. п. 5) |
| Автентифікація | Flask-Login: сесійна cookie, підписана `SECRET_KEY`; у cookie лежить `_user_id`. Ролі `keys.access_right`: guest, authorized, operator, admin |
| Суб'єкт даних | Користувач таблиці `keys` (`user_id`) |
| Логування (до Лаб.4) | 57 викликів `print(f"...{e}")` у 7 файлах + таблиці `user_activity_log`, `sql_execution_log` |

## 2. Категорії персональних даних

| Категорія | Поля | Джерело (як потрапляє) | Сховище | У логах (до Лаб.4) | В експорті |
|---|---|---|---|---|---|
| Прямі ідентифікатори | логін, ПІБ | реєстрація, оформлення замовлення, заявки | `keys.login/full_name`, `orders.client_name`, `repair_requests.client_name`, `software_requests.client_name`, `registration_requests.guest_login` | так (повідомлення про помилки) | так |
| Контактні дані | email, телефон, адреса доставки | реєстрація, форми замовлення й заявок | `keys.email`, `orders.client_email/client_phone/delivery_address`, `repair_requests.*`, `software_requests.*` | так (тексти винятків БД) | так |
| Технічні ідентифікатори | IP-адреса, `user_id`, сесійна cookie | кожен запит | `user_activity_log.ip_address`, `sql_execution_log.ip_address`; cookie лише в браузері | IP зберігається в БД | IP так; cookie ні |
| Історія дій | журнал активності, історія SQL-консолі, історія статусів, кошик, список бажань, конфігурації ПК, відгуки | дії користувача в застосунку | `user_activity_log`, `sql_execution_log`, `repair/software_status_history`, `cart`, `wishlist`, `computer_configurations`, `product_reviews` | частково | так (крім тексту SQL) |
| Транзакційні записи | замовлення, позиції, сервісні замовлення, заявки | оформлення замовлення, сервісні форми | `orders`, `order_items`, `service_orders`, `repair_requests`, `software_requests` | так | так |
| Облікові дані | хеш пароля | реєстрація | `keys.password` | не повинен | **ніколи** |
| Дані про згоду | мета, версія політики, час надання й відкликання, канал, хто виконав | команди GRANT / REVOKE (Завд.4) | `user_consents`, `user_consent_history`; дані залежних дій: `marketing_outbox`, `analytics_events` | коди й числа (PII немає) | так (`actor_id` ні) |

## 3. Поля, які ніколи не повертаються через експорт

`actor_id`, `admin_notes`, `assigned_employee_id`, `changed_by`, `password`, `password_hash`, `processed_by`, `received_by`, `reset_token`, `security_answer`, `verification_token`

Крім того, з експорту виключено дані інших користувачів: тексти SQL-запитів і результати запитів (можуть містити чужі PII-літерали), а також посилання на працівників (`orders.processed_by`, `registration_requests.admin_id`, `registration_requests.processed_by`, `repair_requests.assigned_employee_id`, `repair_status_history.changed_by`, `repairs.employee_id`, `returns.employee_id`, `sales.employee_id`, `service_orders.employee_id`, `software_requests.assigned_employee_id`, `software_status_history.changed_by`, `supply_deliveries.received_by`): це ідентифікатори інших осіб.

## 4. Політика обробки записів (DELETE / ANONYMIZE / RETAIN / SKIP)

| Таблиця.колонка суб'єкта | Дія | Як знаходимо рядки | Що знеособлюється (колонка → спосіб) | Секція експорту | Обґрунтування |
|---|---|---|---|---|---|
| `keys.user_id` | ANONYMIZE | за user_id | login → RANDOM_LOGIN, email → NULL, full_name → NULL, password → UNUSABLE_SECRET, last_login → NULL, is_active → FALSE, access_right → GUEST_ROLE | profile | Головна сутність: рядок ЛИШАЄТЬСЯ (на нього посилаються замовлення з NO ACTION), але всі ідентифікатори знеособлюються, доступ закривається (is_active=false, роль guest, непридатний пароль). |
| `orders.user_id` | ANONYMIZE | за user_id | client_name → REMOVED_TEXT, client_phone → REMOVED_TEXT, client_email → NULL, delivery_address → NULL, notes → NULL | orders | Замовлення це фінансовий запис. Змодельоване правило утримання (облік): сума, дата й статус лишаються; контактні дані, адреса доставки й вільний текст прибираються. |
| `order_items.order_id` | RETAIN | через батьківський запис | — | order_items | Позиції замовлення: назва товару, кількість, ціна. PII немає; потрібні для цілісності фінансового запису. |
| `service_orders.client_id` | ANONYMIZE | за user_id | description → NULL | service_orders | Замовлення сервісу: вартість і статус лишаються як бізнес-запис; вільний опис може містити PII, тому прибирається. Посилання client_id на keys.user_id БЕЗ зовнішнього ключа: знайдено інвентаризацією. |
| `repair_requests.user_id` | ANONYMIZE | за user_id | client_name → REMOVED_TEXT, client_phone → REMOVED_TEXT, client_email → NULL, problem_description → REMOVED_TEXT, repair_notes → NULL, admin_notes → NULL | repair_requests | Заявка на ремонт: тип пристрою, вартість і статус лишаються; контакти й усі вільні тексти прибираються (вони можуть містити імена та інші PII). |
| `repair_status_history.request_id` | ANONYMIZE | через батьківський запис | comment → NULL | repair_status_history | Історія статусів заявки: переходи лишаються, коментар працівника (вільний текст про клієнта) прибирається. |
| `software_requests.user_id` | ANONYMIZE | за user_id | client_name → REMOVED_TEXT, client_phone → REMOVED_TEXT, client_email → NULL, additional_notes → NULL, installation_notes → NULL, admin_notes → NULL | software_requests | Заявка на ПЗ: аналогічно ремонту. Склад пакета й вартість лишаються, контакти та вільні тексти прибираються. |
| `software_status_history.request_id` | ANONYMIZE | через батьківський запис | comment → NULL | software_status_history | Історія статусів заявки на ПЗ: як і для ремонту. |
| `registration_requests.guest_login` | ANONYMIZE | за текстом логіну | guest_login → SUBJECT_NEW_LOGIN, message → NULL | registration_requests | Запит на підвищення прав зберігає логін ТЕКСТОМ без зовнішнього ключа («похідне» PII). Тому шукаємо за старим логіном і замінюємо на ТОЙ САМИЙ новий логін, що й у keys; повідомлення прибираємо. |
| `cart.user_id` | DELETE | за user_id | — | cart | Кошик це чернетка без підстави для зберігання, тож видаляється повністю. |
| `wishlist.user_id` | DELETE | за user_id | — | wishlist | Список бажань: особисті вподобання, підстави зберігати немає, видаляється. |
| `computer_configurations.user_id` | DELETE | за user_id | — | configurations | Збережені конфігурації ПК: особисті дані користувача (назва нерідко містить ім'я), видаляються разом із компонентами. |
| `config_components.config_id` | DELETE | через батьківський запис | — | configuration_components | Компоненти конфігурації: частина конфігурації, видаляються разом з нею (в БД ON DELETE CASCADE). |
| `product_reviews.user_id` | ANONYMIZE | за user_id | review_text → NULL, pros → NULL, cons → NULL | reviews | Оцінка товару корисна для каталогу і лишається; вільний текст відгуку (може містити PII) прибирається. |
| `user_activity_log.user_id` | ANONYMIZE | за user_id | ip_address → NULL, details → NULL | activity | Журнал активності: факт дії й час лишаються (аудит безпеки), IP-адреса (технічний ідентифікатор) і вільний текст деталей прибираються. |
| `sql_execution_log.user_id` | ANONYMIZE | за user_id | ip_address → NULL, sql_query → REMOVED_TEXT, error_message → NULL | sql_console_history | Журнал SQL-консолі: метадані лишаються; текст запиту й помилки можуть містити чужі PII-літерали, тому прибираються, а в експорт не потрапляють. |
| `query_results.user_id` | ANONYMIZE | за user_id | result_data → NULL, error_message → NULL | — | Збережені результати запитів містять вибірки даних (можливо чужих), тому знеособлюються й не експортуються. |
| `saved_queries.created_by` | RETAIN | за user_id | — | authored_queries | Збережений запит це робочий артефакт; PII немає, а зв'язок з автором тепер веде на знеособлений обліковий запис. |
| `news.author_id` | RETAIN | за user_id | — | authored_news | Опублікована новина це публічний контент компанії; PII немає, автор тепер знеособлений обліковий запис. |
| `user_consents.user_id` | RETAIN | за user_id | — | consents | Поточний стан згоди: лише коди, версії й часові мітки, прямих PII немає. Рядок ЛИШАЄТЬСЯ як доказ, що обробку було припинено. Перед цим анонімізація явно ЗНІМАЄ всі діючі згоди (consent.withdraw_all, з записом в історію), тож стан після операції завжди «відкликано». |
| `user_consent_history.user_id` | RETAIN | за user_id | — | consent_history | Незмінний (append-only) доказ згод: яку політику, коли, через який канал. PII немає (actor_id і correlation_id це числа/коди; actor_id в експорт не віддається). Це змодельована підстава зберігати докази згоди (Art. 7(1)). |
| `marketing_outbox.user_id` | DELETE | за user_id | — | marketing_messages | Черга маркетингових листів: поведінкові дані без підстави для зберігання після виходу користувача, тож видаляється (разом із ще не надісланими листами). Адреси в черзі немає: її беруть із keys під час відправки. |
| `analytics_events.user_id` | DELETE | за user_id | — | analytics_events | Події аналітики: профіль поведінки користувача, лише за його згодою; після виходу видаляються повністю. |
| `privacy_audit_log.subject_id` | RETAIN | за user_id | — | privacy_audit | Доказ виконання вимог приватності (хто/коли/результат); у таблиці лише числові ідентифікатори, PII немає. actor_id в експорт не віддається: це ідентифікатор іншої особи. |
| `repairs.client_id` | SKIP | за user_id | — | — | Застаріла порожня таблиця: у коді не використовується, семантика client_id не підтверджена (немає FK). Якщо в ній з'являться дані, потрібне рішення (див. тест порожніх SKIP-таблиць у документі). |
| `returns.client_id` | SKIP | за user_id | — | — | Застаріла порожня таблиця без FK: як repairs. |
| `sales.client_id` | SKIP | за user_id | — | — | Застаріла порожня таблиця без FK; маршрут /sales у коді посилається на неіснуючу таблицю clients. |

Способи знеособлення: `NULL` (порожньо), `REMOVED_TEXT` (`[removed]` для NOT NULL колонок), `RANDOM_LOGIN` (унікальний випадковий `anon-<hex>`, зв'язок з оригіналом не зберігається), `UNUSABLE_SECRET` (випадковий рядок замість хеша, вхід неможливий).

Чому **анонімізація** `keys`, а не видалення рядка: на `keys` посилається 24 зовнішніх ключі, і більшість із них (зокрема `orders.user_id`) має `ON DELETE NO ACTION`, тож `DELETE` упав би на замовленнях. До того ж замовлення — фінансовий запис, який за змодельованим правилом утримання лишається, але без PII.

Посилання на працівників (`orders.processed_by`, `registration_requests.admin_id`, `registration_requests.processed_by`, `repair_requests.assigned_employee_id`, `repair_status_history.changed_by`, `repairs.employee_id`, `returns.employee_id`, `sales.employee_id`, `service_orders.employee_id`, `software_requests.assigned_employee_id`, `software_status_history.changed_by`, `supply_deliveries.received_by`) не змінюються: рядок належить бізнес-процесові, а не суб'єкту.

## 5. Що виявила інвентаризація (неочевидне)

1. **`service_orders.client_id` → `keys.user_id` без зовнішнього ключа.** 10 рядків, усі збігаються з користувачами. Формальний аналіз FK цю таблицю пропустив би.
2. **`registration_requests.guest_login` зберігає логін текстом**, без зв'язку з `keys`. Це «похідне» PII: знайти його можна лише за старим логіном, тому анонімізація має спочатку запам'ятати логін, а потім замінити його в обох місцях на один і той самий новий.
3. **Застарілі таблиці `repairs`, `returns`, `sales`** мають `client_id` без FK і порожні; маршрут `/sales` посилається на неіснуючу таблицю `clients`. Позначені `SKIP` з обґрунтуванням. Якщо в них з'являться дані, потрібне рішення.
4. **View `v_repair_requests_full`, `v_software_requests_full`** показують PII, але не зберігають власних даних: після анонімізації базових таблиць вони відображають вже знеособлені значення.
5. **`suppliers`** (контакти компаній) це B2B-дані, а не користувачі системи; поза межами цієї політики (`OUT_OF_SCOPE_COLUMNS`).
6. **Вільні тексти** (`notes`, `description`, `comment`, `message`, `problem_description` тощо) можуть містити PII, які неможливо розпізнати автоматично, тому під час анонімізації вони прибираються цілком.
7. **Усі записи прив'язані через `user_id`.** У робочій БД немає записів без `user_id`, які збігалися б з email користувача. Припущення, що «гостьових» записів нема, зафіксовано як відомі межі.

## 6. Контрольні тестові дані

`tests/factories.py` створює вигаданого користувача з записами в **кожному** джерелі PII та унікальним контрольним значенням у кожному полі:

| Дані | Приклад (синтетичний) | Чому безпечно |
|---|---|---|
| email | `demo_u1@example.test` | домен `example.test` зарезервований (RFC 2606), пошти не існує |
| IP | `203.0.113.1` | діапазон TEST-NET-3 (RFC 5737), призначений для документації |
| телефон | `+380500000001` | вигадана послідовність |
| тексти | `CONTROL-u1-order-note` | унікальні маркери, за якими видно, де значення лишилось |
| пароль | `synthetic-not-a-real-password` | не відкриває жодного облікового запису |

За цими маркерами перевіряються: повнота експорту (кожен маркер є у відповіді), відсутність заборонених полів, результат анонімізації (жоден маркер не лишився в жодній таблиці), маскування логів.

## 7. Автоматичні перевірки інвентаризації

```text
python -m pytest tests/test_pii_inventory.py -q
```

* кожна таблиця з посиланням на `keys` (за FK) має рішення в реєстрі або є посиланням на працівника;
* кожна колонка-посилання на людину без FK (як `service_orders.client_id`) теж має рішення;
* кожна PII-подібна колонка (за назвою) покрита політикою або явно винесена за межі;
* усі колонки з реєстру існують у БД, а способи знеособлення сумісні з типами колонок;
* фабрика створює рядки в кожному джерелі PII, а умова вибірки не змішує дані різних користувачів.

Перевірено навмисним порушенням: тимчасова таблиця `zz_probe` з посиланням на `keys` і колонкою `contact_email` валила три тести, поки для неї не було рішення.

## 8. Поза межами програмної реалізації

Правова підстава обробки, конкретні строки зберігання, повідомлення суб'єктів і процедури реагування на інциденти це організаційні й юридичні рішення. У роботі правила RETAIN лише **змодельовані** (наприклад, «замовлення зберігається як фінансовий запис»).

## Пов'язані у базі знань

[[0002-privacy-by-design-module]] · [[sdd]] · [[consent]] · [[pii_inventory]] #architecture
