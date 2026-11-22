---
title: Довідник коду (з docstring-ів)
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-02-20
tags:
  - api
---

# Довідник коду (згенеровано з docstring-ів)

!!! note "Згенерована сторінка"
    Не редагуйте вручну: `python tools/gen_api_reference.py` будує її з docstring-ів модулів.
    Контракт HTTP описує [OpenAPI](openapi-contract.md); тут — внутрішні функції й класи, що його реалізують.

## Перевірка стану (GET /api/health)

`routers/health.py` — Перевірка стану застосунку для моніторингу й розгортання: GET /api/health.

| Ім'я | Тип | Опис |
|---|---|---|
| `check_database()` | функція | Повертає (БД доступна, список відсутніх таблиць міграцій). |
| `health()` | функція | без опису |

## Довідка API працюючого екземпляра

`routers/api_docs.py` — Інтерактивна довідка API працюючого екземпляра (Лаб.11).

| Ім'я | Тип | Опис |
|---|---|---|
| `openapi_spec()` | функція | без опису |
| `api_docs()` | функція | без опису |

## REST API згод

`privacy/consent_api.py` — HTTP-шар Consent Management Engine (Лаб.4, Завд.4).

| Ім'я | Тип | Опис |
|---|---|---|
| `list_consents(user_id)` | функція | без опису |
| `grant_consent(user_id, purpose)` | функція | без опису |
| `revoke_consent(user_id, purpose)` | функція | без опису |
| `marketing_send(user_id)` | функція | Тіло: {"campaign": "AUTUMN_SALE"}. ALLOW → лист у черзі (побічний ефект); DENY → нічого не записано. |
| `marketing_process_queue()` | функція | Фонове опрацювання черги, запущене оператором. Згода перевіряється ЗНОВУ для кожного листа. |
| `analytics_event(user_id)` | функція | Тіло: {"event_name": "PAGE_VIEW"}. Подія аналітики про користувача, тож її записує лише він сам. |

## REST API експорту й анонімізації

`privacy/api.py` — HTTP-шар функцій приватності (Лаб.4): Personal Data Export (Завд.2) та Anonymization (Завд.3).

| Ім'я | Тип | Опис |
|---|---|---|
| `json_response(payload, status)` | функція | без опису |
| `record_audit(event_type, actor_id, subject_id, result)` | функція | Privacy-safe audit: лише коди й числові id, жодного PII. Збій аудиту не ламає відповідь, але гучно логується. |
| `is_allowed(subject_id, allow_admin)` | функція | Власник або (якщо allow_admin) роль із явним повноваженням. Порівнюємо principal із subject id, а не довіряємо URL. |
| `check_access(subject_id, event, allow_admin)` | функція | None, якщо доступ дозволено; інакше готова відповідь (401 або однакова для всіх чужих 403). allow_admin=False: операція лише для самого суб'єкта (наприклад, надання згоди: це воля людини, а не оператора). |
| `check_admin(event, subject_id)` | функція | Операції оператора (розсилка, обробка черги): лише роль admin. None, якщо дозволено. |
| `personal_data(user_id)` | функція | без опису |
| `anonymize(user_id)` | функція | Тіло: {"confirm": "ANONYMIZE"} з Content-Type: application/json. |

## Контракти оформлення замовлення (typing.Protocol)

`services/contracts.py` — Абстрактні контракти оформлення замовлення (Лаб.8, Завд.2, PASS).

| Ім'я | Тип | Опис |
|---|---|---|
| `CartStore` | клас | Де лежать позиції кошика (сесія гостя або таблиця cart). |
| `Catalog` | клас | Звідки беруться назви, ціни й залишки товарів. |
| `PricingPolicy` | клас | без опису |
| `DeliveryEstimator` | клас | без опису |
| `OrderRepository` | клас | без опису |

## Пов'язані у базі знань

[[openapi-contract]] · [[sdd]] #api
