---
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-04-16
tags:
  - architecture
---

# Лаб.4, Завд.4: Consent Management Engine (GDPR Art. 7)

Усі приклади синтетичні: користувачі `demo_alice`, `demo_bob`, `demo_admin` існують лише в одноразовій демо-БД.

## 1. Проблема й ідея

Рядок `is_marketing = true` у таблиці ще не є згодою: якщо розсилка його не читає, користувач «погодився» формально. Тому тут:

1. **Стан** згоди (`user_consents`) читається **безпосередньо перед дією**, а не під час реєстрації чи з кешу.
2. **Доказ** (`user_consent_history`) відповідає на питання «яку політику, коли, через який канал, ким» і не може бути змінений.
3. **Policy Gate** (`consent.gate`) повертає ALLOW або DENY. DENY завершує дію **без побічного ефекту**.
4. Відкликання діє **негайно**: кешу немає, а фонове завдання перевіряє згоду знову в момент відправки.

Згода не універсальний прапорець: Gate викликають лише дві **необов'язкові** дії (маркетингова розсилка й аналітика). Замовлення, вхід, ремонт, експорт даних, анонімізація працюють без жодної згоди (тест `test_contract_functions_are_not_blocked_by_missing_consent`).

## 2. Модель даних (`migrations/002_consent.sql`)

| Таблиця | Роль | Ключові поля |
|---|---|---|
| `user_consents` | поточний стан, один рядок на пару (користувач, мета) | `user_id`, `purpose`, `is_granted`, `policy_version`, `granted_at`, `withdrawn_at`, `updated_at`, `source` |
| `user_consent_history` | **append-only** доказ | `user_id`, `purpose`, `action` (GRANT/REVOKE), `policy_version`, `source`, `actor_id`, `correlation_id`, `occurred_at` |
| `marketing_outbox` | залежна дія 1 (MARKETING_EMAIL) | `user_id`, `campaign`, `status` (QUEUED/SENT/CANCELLED), `reason`, `queued_at`, `processed_at` |
| `analytics_events` | залежна дія 2 (OPTIONAL_ANALYTICS) | `user_id`, `event_name`, `occurred_at` |

**Мети:** `MARKETING_EMAIL`, `OPTIONAL_ANALYTICS`. Кожна має власний рядок і власну чинну версію політики (`consent.CURRENT_POLICY_VERSION`).

Захист на рівні БД (діє, навіть якщо код помилиться):

* `UNIQUE (user_id, purpose)`: повторні команди оновлюють один рядок, суперечливих дублікатів не буває;
* `CHECK`: діюча згода обов'язково має `granted_at` і не має `withdrawn_at`; відкликана обов'язково має `withdrawn_at`; мета й канал з білого списку;
* тригер забороняє `UPDATE` і `DELETE` у `user_consent_history`;
* жодного вільного тексту в усіх чотирьох таблицях: лише коди, числа, часові мітки. Згода не може стати прихованою копією PII.

**Як зберігається доказ:**

| Питання | Де відповідь |
|---|---|
| Яку політику прийняв? | `policy_version` (стан і кожна подія історії) |
| Коли? | `granted_at`, `occurred_at` (з часовою зоною) |
| Через який канал? | `source`: WEB / MOBILE / API (від клієнта); SUPPORT (відкликав admin); ERASURE (знято правом на видалення) |
| Ким виконано? | `actor_id` в історії (сам суб'єкт чи admin) |
| Коли відкликав? | `withdrawn_at`; подія REVOKE в історії |
| Як пов'язати з запитом? | `correlation_id` з журналу застосунку |

## 3. API

| Метод і шлях | Хто | Дія |
|---|---|---|
| `GET /api/users/<id>/consents` | власник або admin | стан по **кожній** меті (`NOT_SET` / `GRANTED` / `WITHDRAWN`) і історія |
| `POST /api/users/<id>/consents/<purpose>/grant` | **лише сам суб'єкт** | надати згоду; тіло `{"policy_version": "...", "source": "WEB"}` |
| `POST /api/users/<id>/consents/<purpose>/revoke` | власник або admin | відкликати згоду |
| `POST /api/users/<id>/marketing/send` | лише admin | поставити лист у чергу, **якщо** є згода цільового користувача |
| `POST /api/marketing/process-queue` | лише admin | фонове опрацювання черги (згода перевіряється знову) |
| `POST /api/users/<id>/analytics/events` | лише сам суб'єкт | записати подію, **якщо** є згода |

Рішення щодо доступу:

* **GRANT лише сам суб'єкт.** Згода це воля людини; якби admin міг «погодитись за користувача», це була б підроблена згода. Тому admin отримує на GRANT ту саму 403, що й сторонній (тест `test_only_the_subject_can_grant_not_a_stranger_and_not_even_admin`).
* **REVOKE власник або admin.** Відкликати можна за прохання клієнта; помилкове відкликання шкоди не завдає. Якщо відкликає admin, сервер сам ставить `source = SUPPORT` (клієнт не може підробити канал).
* **Розсилку ініціює admin**, але Gate перевіряє згоду **цільового користувача**, а не актора.
* Для чужого й неіснуючого `id` не-адмін бачить **однакову** 403 (немає перебору профілів); admin отримує 404.
* Команди зі зміною стану приймають лише `application/json`: HTML-форма з чужого сайту (CSRF) не може надати згоду від імені користувача (тест `test_grant_requires_json_...`).

**Валідація:** невідома мета 400; невідомий канал 400; версія політики не збігається з чинною 409 (прийняти «якусь іншу» версію неможливо); назва кампанії `^[A-Z0-9_]{3,40}$`; подія аналітики лише з білого списку (`LOGIN`, `PAGE_VIEW`, `FEATURE_USED`). Вільний текст не проходить, тож PII не потрапляє в таблиці залежних дій.

**Ідемпотентність:**

| Команда | Повторно | Результат |
|---|---|---|
| GRANT тієї самої версії | `unchanged` | `granted_at` не «оновлюється», нового рядка історії немає |
| GRANT нової версії | `granted` | нова згода (нова `granted_at`, нова подія GRANT) |
| REVOKE, коли згода вже відкликана | `unchanged` | `withdrawn_at` не «пересувається», нової події немає |
| REVOKE, коли згоди ніколи не було | `unchanged` | **жодного рядка не створюється** (відкликати нічого) |

## 4. Policy Gate (`privacy/consent.py`, `gate()`)

| Умова (перевіряється в такому порядку) | Рішення | `reason` |
|---|---|---|
| мета невідома | DENY | `UNKNOWN_PURPOSE` |
| суб'єкта немає | DENY | `SUBJECT_NOT_FOUND` |
| суб'єкта анонімізовано | DENY | `SUBJECT_ANONYMIZED` |
| рядка згоди немає | DENY | `NO_CONSENT_RECORD` |
| згоду відкликано | DENY | `CONSENT_WITHDRAWN` |
| версія політики не чинна | DENY | `POLICY_VERSION_OUTDATED` |
| інакше | **ALLOW** | `CONSENT_GRANTED` |

Закрито за замовчуванням: усе, що не є явним ALLOW, це DENY. Відповідь HTTP на DENY: `403 {"decision": "DENY", "reason": "...", "purpose": "..."}`.

### Де викликається Gate (залежні дії, `privacy/actions.py`)

| Дія | Мета | Побічний ефект при ALLOW |
|---|---|---|
| `queue_marketing_email` | MARKETING_EMAIL | рядок у `marketing_outbox` (QUEUED) |
| `process_marketing_queue` (фонове завдання) | MARKETING_EMAIL | QUEUED → SENT і виклик відправки; при DENY → CANCELLED з причиною |
| `record_analytics_event` | OPTIONAL_ANALYTICS | рядок у `analytics_events` |
| **вхід у систему** (`app.py`, `login`) | OPTIONAL_ANALYTICS | подія `LOGIN`; без згоди нічого не пишеться, а збій аналітики **ніколи** не ламає вхід |

Останній рядок це вбудовування в **реальний потік застосунку**: згода впливає на роботу сайту, а не лише на окремий тестовий ендпоінт.

### Гонка «перевірили, а потім відкликали» (TOCTOU)

Gate і побічний ефект виконуються в **одній транзакції**, а Gate **тримає блокування** до її кінця. Усі, хто торкається згоди, беруть блокування в одному порядку (спершу рядок `keys`, потім рядок `user_consents`):

| Хто | Блокування |
|---|---|
| Gate | `keys FOR KEY SHARE` → `user_consents FOR SHARE` |
| REVOKE / GRANT | `keys FOR NO KEY UPDATE` → `user_consents FOR UPDATE` |
| Анонімізація | `keys FOR UPDATE` → зміна згод |

Наслідок: якщо дія вже отримала ALLOW, REVOKE **чекає**, поки вона завершиться; якщо REVOKE встиг першим, дія отримує DENY. Однаковий порядок блокувань виключає взаємні блокування (deadlock). Це доводить `test_revoke_waits_for_an_action_that_already_received_allow`.

## 5. Взаємодія з правом на видалення (Завд.3)

* Перед анонімізацією `consent.withdraw_all` **знімає всі діючі згоди** (`source = ERASURE`) і дописує REVOKE в історію.
* `user_consents` і `user_consent_history` лишаються (**RETAIN**): це доказ згоди й відкликання, прямих PII там немає.
* `marketing_outbox` і `analytics_events` **видаляються** (**DELETE**): поведінкові дані без підстави зберігання.
* Після анонімізації Gate повертає DENY (`SUBJECT_ANONYMIZED`), надати згоду анонімізованому суб'єкту неможливо.

## 6. Тести (`tests/test_consent.py`, 43 інтеграційних тести на справжній БД)

```text
pytest tests/test_consent.py -v          # усі 43
pytest tests/test_consent.py -k scenario -v   # GRANT -> ALLOW -> REVOKE -> DENY (маркетинг, аналітика) і ізоляція цілей: 3 тести
```

| Вимога лабораторної | Тести |
|---|---|
| Початковий стан DENY | `test_marketing_scenario_...` (крок 0), `test_gate_reasons` |
| GRANT → ALLOW + побічний ефект у БД | `test_marketing_scenario_grant_allow_revoke_deny`, `test_analytics_scenario_...` |
| REVOKE → DENY без побічного ефекту | ті самі + `test_gate_denial_has_no_side_effect` (знімок усіх таблиць до/після) |
| Згода на одну мету не діє на іншу | `test_scenario_consent_to_one_purpose_does_not_allow_another`, `test_marketing_consent_does_not_enable_login_analytics` |
| Згода одного користувача не діє на іншого | `test_consent_of_one_user_does_not_apply_to_another` |
| Версія політики | `test_outdated_policy_version_denies_until_reconsent` |
| Доказ: політика, час, канал, історія | `test_grant_stores_evidence_metadata`, `test_revoke_records_...`, `test_regrant_after_revoke_...` |
| Ідемпотентність | `test_repeated_grant_...`, `test_repeated_revoke_...`, `test_revoke_without_prior_consent_...` |
| Авторизація | 8 тестів розділу 6 файлу (401, стороннім, admin на GRANT, enumeration, оператор, аналітика, 2 тести аудиту) |
| Фонове завдання й негайне відкликання | 5 тестів розділу 7 |
| Гонка між перевіркою й дією | `test_revoke_waits_for_an_action_that_already_received_allow` |
| Реальний потік (вхід) | 4 тести розділу 9 |
| Право на видалення | 3 тести розділу 10 |
| Обмеження на рівні БД | `test_database_rejects_...`, `test_consent_history_is_append_only` |
| Журнал без PII | `test_consent_events_are_logged_without_pii` |

**Мутаційна перевірка** (плагіни pytest, код проєкту не змінювався): кожен механізм навмисно ламався, і тести мусили впасти.

| Навмисне порушення | Результат |
|---|---|
| Gate завжди дозволяє | **падає 17 тестів** |
| Gate ігнорує мету (згода на одну діє на всі) | **падає 5 тестів** |
| Gate ігнорує версію політики | **падає 2 тести** |
| REVOKE не пишеться в історію | **падає 7 тестів** |
| Фонове завдання не перевіряє згоду знову | **падає 3 тести** |
| Admin може надати згоду за користувача | **падає 2 тести** |
| REVOKE не ідемпотентний (кожен повтор пише подію) | **падає 2 тести** |
| Gate без блокування (гонка TOCTOU) | **падає 1 тест**: саме тест гонки |
| Анонімізація не знімає згоди | **падає 1 тест** |
| Подія аналітики при вході без перевірки Gate | **падає 2 тести** |
| GRANT приймає будь-яку версію політики | **падає 2 тести** |
| Відкликання admin не маркується каналом SUPPORT | **падає 1 тест** |

## 7. Відтворення (жива демонстрація)

```text
python scripts/demo_db.py                                          # скинути демо-БД (обов'язково перед кожним прогоном)
$env:DB_NAME = "computer_store_demo"; python app.py                # сервер (термінал 1)
.\scripts\consent_demo.ps1                                         # клієнт (термінал 2)
$env:DB_NAME = $null
pytest tests/test_consent.py -k scenario -v                        # завершення: інтеграційний тест
```

Клієнт показує 13 кроків: стан до, DENY без згоди, відмова стороннім та admin на GRANT, GRANT, ALLOW (лист у черзі), ізоляція цілей, REVOKE, DENY, фонове завдання скасовує лист, повторний REVOKE, стан після (історія GRANT+REVOKE, лист CANCELLED).

## 8. Відомі межі (поза програмною реалізацією)

* **Правова підстава й текст політики.** Код фіксує, що користувач прийняв версію `2026-10`; **що саме написано в цій версії**, якою мовою, чи зрозуміла вона, це організаційне рішення. Версії політики мають зберігатися окремо (тут лише ідентифікатор).
* **Інтерфейс згоди.** Тут API; банер, чекбокси й заборона заздалегідь позначених полів (Art. 7, Recital 32) це фронтенд.
* **Канал `source` декларується клієнтом.** Сервер не може довести, що це справді мобільний застосунок; доказову вагу має зв'язка `actor_id` + `correlation_id` + журнал сервера.
* **Відправка листа змодельована.** `_dispatch` лише логує числовий id; реальний SMTP/провайдер поза межами лабораторної. Але порядок «Gate → відправка» та скасування черги працюють по-справжньому.
* **Інші підстави обробки.** Згода тут одна з підстав; договірні й законні підстави (виконання замовлення, облік) Gate не стосуються навмисно.
* **Rate limiting та повторна автентифікація** перед зміною згоди не реалізовані.
* **Робоча БД:** перед використанням виконайте `python scripts/migrate.py` (міграція `002_consent.sql`).

## Пов'язані у базі знань

[[0002-privacy-by-design-module]] · [[sdd]] · [[consent]] · [[pii_inventory]] #architecture
