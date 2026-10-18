# Лаб.4, Завд.2: Right of Access та Personal Data Export (GDPR Art. 15)

Усі приклади отримано з **демо-БД з вигаданими користувачами** (`example.test`), реальних PII тут немає.

## 1. Контракт

`GET /api/users/{id}/personal-data`: повний машинозчитуваний експорт персональних даних користувача `id`.

| Код | Коли | Тіло |
|---|---|---|
| **200** | власник запитує свої дані, або `admin` запитує дані існуючого користувача | експорт (п. 2) |
| **401** | немає входу | `{"error": "authentication_required"}` |
| **403** | чужий профіль для не-адміна: **і для існуючого, і для неіснуючого `id` відповідь однакова** | `{"error": "forbidden"}` |
| **404** | лише для `admin`: такого користувача немає | `{"error": "not_found"}` |
| **503** | БД недоступна | `{"error": "service_unavailable"}` |
| 405 | будь-який метод, окрім GET | |

Заголовки відповіді: `Content-Type: application/json`, `Cache-Control: no-store` (персональні дані не кешуються), `X-Correlation-ID`.

## 2. Структура відповіді

Верхній рівень стабільний: `meta` (метадані формування) і `data` (секції). Нижче скорочений **справжній** експорт демо-користувача:

```json
{
  "meta": {
    "schema_version": "1.0",
    "generated_at": "2026-10-10T20:18:56+00:00",
    "timezone": "UTC",
    "timestamps": "Значення дати-часу з бази подано без зони (локальний час сервера БД).",
    "subject_id": 1,
    "sections": [
      {
        "section": "profile",
        "category": "identity_and_contact",
        "source_table": "keys",
        "record_count": 1
      },
      {
        "section": "orders",
        "category": "transactions",
        "source_table": "orders",
        "record_count": 1
      },
      {
        "section": "order_items",
        "category": "transactions",
        "source_table": "order_items",
        "record_count": 1
      },
      {
        "...": "20 more sections"
      }
    ],
    "omissions": [
      {
        "section": "settings",
        "reason": "Система не зберігає персональних налаштувань профілю."
      }
    ]
  },
  "data": {
    "profile": {
      "user_id": 1,
      "login": "demo_alice",
      "email": "demo_alice@example.test",
      "full_name": "Control Person 1",
      "access_right": "authorized",
      "created_at": "2026-10-10T23:14:41.430056",
      "last_login": "2026-10-10T23:14:41.430056",
      "is_active": true
    },
    "orders": [
      {
        "order_id": 1,
        "order_number": "ORD-CONTROL-1",
        "order_date": "2026-10-10T23:14:41.430056",
        "status": "new",
        "payment_status": "pending",
        "payment_method": "card",
        "delivery_type": "courier",
        "delivery_address": "Control Street 1, apt 1",
        "client_name": "Control Person 1",
        "client_phone": "+380500000001",
        "client_email": "demo_alice@example.test",
        "total_amount": "1000.00",
        "delivery_cost": "0.00",
        "discount_amount": "0.00",
        "final_amount": "1000.00",
        "notes": "CONTROL-u1-order-note",
        "tracking_number": null
      }
    ],
    "cart": [
      {
        "cart_id": 1,
        "product_id": 1,
        "quantity": 2,
        "added_date": "2026-10-10T23:14:41.430056"
      }
    ],
    "...": "20 more sections"
  }
}
```

* `schema_version`: версія контракту. Якщо схема зміниться, старі експорти лишаться однозначними.
* `generated_at`: час формування в **UTC** з явним зсувом; значення дати-часу з бази подано як є, без зони (про це сказано в `meta.timestamps`).
* `sections`: для кожної секції її **категорія**, **таблиця-джерело** й **кількість записів**.
* `omissions`: **задокументовані пропуски** (категорії, яких у системі немає), а не тихо відсутні секції.
* Відсутні дані: секція лишається, але порожня (`[]`), тож схема однакова в усіх користувачів. Це перевіряє тест.
* Суми (`numeric`) віддаються рядком, щоб не втратити точність; записи впорядковані за первинним ключем, тож експорт відтворюваний.

## 3. Джерела даних (звідки береться кожна секція)

Секції генеруються з реєстру `privacy/policy.py`; колонки перелічені **явно** (ніколи `SELECT *`).

| Секція | Таблиця | Категорія | Колонки |
|---|---|---|---|
| `profile` | `keys` | identity_and_contact | user_id, login, email, full_name, access_right, created_at, last_login, is_active |
| `orders` | `orders` | transactions | order_id, order_number, order_date, status, payment_status, payment_method, delivery_type, delivery_address, client_name, client_phone, client_email, total_amount, delivery_cost, discount_amount, final_amount, notes, tracking_number |
| `order_items` | `order_items` | transactions | order_item_id, order_id, product_id, product_name, quantity, unit_price, total_price |
| `service_orders` | `service_orders` | transactions | service_order_id, service_type_id, order_date, scheduled_date, completion_date, description, hours_spent, total_cost, payment_status, status |
| `repair_requests` | `repair_requests` | service_requests | request_id, client_name, client_phone, client_email, device_type, manufacturer, model, problem_description, repair_type, request_date, status, estimated_cost, estimated_completion_date, actual_cost, actual_completion_date, repair_notes |
| `repair_status_history` | `repair_status_history` | service_requests | history_id, request_id, old_status, new_status, change_date, comment |
| `software_requests` | `software_requests` | service_requests | request_id, client_name, client_phone, client_email, package_type, selected_software, additional_notes, preferred_date, service_format, request_date, status, estimated_cost, estimated_completion_date, actual_cost, actual_completion_date, installation_notes |
| `software_status_history` | `software_status_history` | service_requests | history_id, request_id, old_status, new_status, change_date, comment |
| `registration_requests` | `registration_requests` | account_requests | request_id, guest_login, requested_access, request_date, status, response_date, message |
| `cart` | `cart` | user_activity | cart_id, product_id, quantity, added_date |
| `wishlist` | `wishlist` | user_activity | wishlist_id, product_id, added_date |
| `configurations` | `computer_configurations` | user_activity | config_id, config_name, purpose, total_price, creation_date, assembly_date, status |
| `configuration_components` | `config_components` | user_activity | config_component_id, config_id, product_id, component_type, quantity, price_at_config |
| `reviews` | `product_reviews` | user_content | review_id, product_id, rating, review_text, pros, cons, review_date, is_verified_purchase |
| `activity` | `user_activity_log` | activity_logs | log_id, action, table_affected, record_id, action_timestamp, ip_address, details |
| `sql_console_history` | `sql_execution_log` | activity_logs | log_id, executed_at, execution_time_ms, rows_affected, status, ip_address |
| `authored_queries` | `saved_queries` | user_content | query_id, title, description, created_at, is_public |
| `authored_news` | `news` | user_content | news_id, title, created_at, published_date, is_published |
| `consents` | `user_consents` | consent | consent_id, purpose, is_granted, policy_version, granted_at, withdrawn_at, updated_at, source |
| `consent_history` | `user_consent_history` | consent | event_id, purpose, action, policy_version, source, occurred_at |
| `marketing_messages` | `marketing_outbox` | consent_dependent_activity | outbox_id, campaign, status, queued_at, processed_at |
| `analytics_events` | `analytics_events` | consent_dependent_activity | event_id, event_name, occurred_at |
| `privacy_audit` | `privacy_audit_log` | privacy_operations | audit_id, event_type, result, occurred_at |

Усі секції читаються в **одній транзакції `REPEATABLE READ` лише для читання**: це знімок, тож експорт узгоджений, навіть якщо дані змінюються під час читання.

## 4. Мінімізація: що НЕ віддається

Жорсткий фільтр `NEVER_EXPORT_COLUMNS` діє незалежно від реєстру (другий рубіж): `actor_id`, `admin_notes`, `assigned_employee_id`, `changed_by`, `password`, `password_hash`, `processed_by`, `received_by`, `reset_token`, `security_answer`, `verification_token`.

Таблиці користувача, що навмисно не експортуються або експортуються частково:

* `query_results`: Збережені результати запитів містять вибірки даних (можливо чужих), тому знеособлюються й не експортуються.
* `keys.password` (хеш пароля), `admin_notes` (внутрішні примітки), ідентифікатори працівників (`processed_by`, `assigned_employee_id`, `changed_by`, `received_by`), тексти SQL-запитів: це або секрети, або дані інших осіб.

## 5. Контроль доступу

| Хто запитує | Свої дані | Дані існуючого іншого | Неіснуючий id |
|---|---|---|---|
| Без входу | 401 | 401 | 401 |
| Звичайний користувач | 200 | **403** | **403** (така сама відповідь) |
| `admin` | 200 | 200 | 404 |

Ключові рішення:

1. **Порівнюється автентифікований користувач із `id` з URL**, а не довіряється path-параметру (захист від **IDOR**).
2. **Рішення про доступ ухвалюється до звернення до БД за чужим профілем**: чужі дані навіть не читаються, і час відповіді не залежить від існування профілю. Тест підміняє `build_export` викликом, що падає, й перевіряє, що для чужого id його не викликано.
3. **Однакова відмова** для існуючого й неіснуючого id (захист від перебору користувачів, *user enumeration*). 404 бачить лише `admin`, якому існування користувача не секрет.
4. **Повноваження `admin`** явне: `access_right == 'admin'`.
5. Для API відповідь 401 це JSON, а не редирект на сторінку входу.

## 6. Логи й аудит

* У лог іде лише факт, `actor_id`, `subject_id`, результат, кількість секцій і записів та correlation ID. **Повний JSON і значення в лог не потрапляють** (перевіряє тест).
* Кожна спроба (успіх, відмова, не знайдено) пишеться в `privacy_audit_log`: тип події, хто, чиї дані, результат, correlation ID. Колонок із текстом немає, тож PII туди потрапити не може.
* Суб'єкт бачить власні записи аудиту в секції `privacy_audit`: тобто в наступному експорті видно, що його дані вже запитували (звідси єдина відмінність між двома експортами поспіль).

## 7. Тести (`tests/test_personal_data_export.py`, 22 інтеграційні тести на справжній тестовій БД)

```
python -m pytest tests/test_personal_data_export.py -q
```

| Що перевіряє | Тести |
|---|---|
| Успішний експорт власних даних, контракт | структура `meta`/`data`, UTC, `no-store`, задокументовані пропуски |
| **Наявність контрольних записів із кожного джерела** | усі 23 секції непорожні; кожне контрольне значення є у відповіді; `record_count` збігається зі вмістом |
| Без змішування й дублів | дані двох інших користувачів відсутні; дублів у секціях немає |
| **Відсутність заборонених полів** | хеш і відкритий пароль не в тексті; жодного ключа з `NEVER_EXPORT`; внутрішні примітки й чужі SQL відсутні; фільтр працює, навіть якщо реєстр помилково містить `password` |
| **Відмова стороннього** | 403 без даних; **ідентична** відповідь для неіснуючого id; чужий профіль не читається з БД |
| Неіснуючий id / без входу / admin | 401 JSON; admin: 200 для існуючого, 404 для відсутнього; лише GET |
| Стабільність схеми | користувач без записів: та сама схема з порожніми секціями; експорт відтворюваний |
| Збій БД | 503 без даних |
| **Логи й аудит** | у лозі немає значень і повного JSON; відмова логується без чужих даних; аудит фіксує успіх і відмову без PII та зв'язаний з correlation ID |

**Мутаційна перевірка** (плагіни pytest, код не змінювався):

| Навмисне порушення | Результат |
|---|---|
| Прибрано перевірку авторизації (IDOR) | **падають 5 тестів**: чужий отримує дані, відповіді відрізняються, чужий профіль читається з БД, відмова не логується, аудит не фіксує відмову |
| Реєстр віддає `password` і вимкнено жорсткий фільтр | **падають 2 тести**: заборонені поля, фільтр-рубіж |

## 7.1. Демонстрація (крок 2 захисту)

```
python scripts/demo_db.py                                            # одноразова демо-БД з вигаданими користувачами
$env:DB_NAME = "computer_store_demo"; python app.py                  # сервер на демо-БД (термінал 1)
.\scripts\privacy_demo.ps1                                            # API-клієнт (термінал 2)
```

Клієнт показує: власник (200 + секції та їх джерела), чужий (403), неіснуючий id (така сама 403), без входу (401).

## 8. Відомі межі

* **Дата-час без зони.** Колонки `timestamp without time zone` старої схеми віддаються як є; зона `UTC` стосується лише `generated_at`. Нові таблиці (`privacy_audit_log`) вже мають зону.
* **Записи без `user_id`** (наприклад, гостьове замовлення з тим самим email) у експорт не входять. У робочих даних таких немає (перевірено інвентаризацією), але це відома межа.
* **Аудит best effort.** Збій запису в `privacy_audit_log` не блокує відповідь, але гучно логується (`privacy_audit_write_failed`).
* Обмеження частоти запитів (rate limiting) і підтвердження особи (повторна автентифікація перед експортом) не реалізовані: це наступний рівень захисту.
* Адміністратор може експортувати будь-кого; обмеження на рівні організації («навіщо адміну ці дані») це процес, а не код. Тому кожен такий виклик потрапляє в аудит.
* Секцію `settings` позначено як `omissions` (система не зберігає налаштувань профілю). Секції `consents` і `consent_history` (Завд.4) тепер справжні.
