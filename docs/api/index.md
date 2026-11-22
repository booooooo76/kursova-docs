---
title: API
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-02-20
tags:
  - api
---

# Рівень 3. API: як інтегруватися

Підхід **API-first**: спочатку пишеться і погоджується контракт `docs/api/openapi.yaml`, потім код, що його
виконує. Контракт — єдине джерело істини (Single Source of Truth), з якого виходять:

| Що | Як отримується з контракту |
|---|---|
| [Інтерактивна довідка](openapi-contract.md) на цьому сайті | плагін `swagger-ui-tag` рендерить `openapi.yaml` під час збирання |
| Довідка працюючого екземпляра `/api/docs` | Flask віддає той самий файл на `/api/openapi.yaml` і Swagger UI |
| Клієнтський SDK (Python) | `openapi-generator-cli generate -g python` |
| Контрактні тести | `tests/test_api_contract.py`: відповіді коду перевіряються схемами контракту |
| Лінтинг якості | Spectral, правила `.spectral.yaml`, поріг 0 errors |

Описані маршрути (версія контракту 1.0.0):

| Метод і шлях | Призначення | Автентифікація |
|---|---|---|
| `GET /api/health` | готовність екземпляра: БД і міграції | не потрібна |
| `GET /api/cart/count` | кількість позицій у кошику | необов'язкова |
| `GET /api/users/{user_id}/consents` | стан згод суб'єкта й історія | cookie, сам або admin |
| `POST /api/users/{user_id}/consents/{purpose}/grant` | надати згоду | cookie, лише сам |

Усі помилки повертають спільний об'єкт `Error` (`{"error": "<код>"}`); виняток — штатна відповідь 503 перевірки
готовності, яка повертає звіт `HealthStatus`. Повний перелік JSON-маршрутів системи — у [SDD](../architecture/sdd.md).
Внутрішні функції, що реалізують контракт, — у [довіднику коду](reference.md).

## Пов'язані у базі знань

[[openapi-contract]] · [[reference]] · [[sdd]] · [[CONTRIBUTING]] #api
