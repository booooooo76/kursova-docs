# Changelog

Формат — [Keep a Changelog](https://keepachangelog.com/uk/1.1.0/); версія контракту API — за SemVer
(`info.version` у `docs/api/openapi.yaml`), версії документації — теги `docs-vX.Y`.

## [1.1.0] — 2026-11-27

Реліз застосунку за [RFC-001](docs/change/RFC-001.md) (CCB-2026-11-27), усуває причину інциденту INC-001.

### Виправлено

- Приймання поставки (`POST /deliveries/{id}/receive`) виконується в одній транзакції з блокуванням рядка поставки й
  змінює залишки лише для статусу `expected`. Повторне натискання більше не додає поставку до складу вдруге, а збій БД
  не лишає частково збільшених залишків (CAPA-1, ADR-0003).
- Оператор більше не бачить тексту винятку БД; замість нього — загальне повідомлення.

### Додано

- Подія журналу `delivery_receive_failed`, алерт A5 і runbook RB-002.
- `scripts/migrate.py` виконує міграції з `lock_timeout` 5 с (змінна `MIGRATION_LOCK_TIMEOUT`, CAPA-2).
- Pre-commit, етап 3: перевірка атомарності `tools/atomicity_check.py` з базовою лінією `.atomicity-baseline` (CAPA-3).
- Експлуатаційний пакет: резервне копіювання й restore drill (`scripts/ops/`), `docs/slo.yaml`, `tools/error_budget.py`,
  `tools/ops_check.py`, RB-001.

### Змінено

- Контракт API (`docs/api/openapi.yaml`, 1.0.1) не змінювався: зачеплений маршрут — HTML-форма поза `/api`.

## [docs-v2.0] — 2026-11-22

### Додано

- База знань MkDocs Material з чотирирівневою пірамідою (README → Developer → API → Architecture), сайт на GitHub Pages.
- Контракт OpenAPI 3.0 (`docs/api/openapi.yaml`, API 1.0.1): `GET /api/health`, `GET /api/cart/count`,
  `GET /api/users/{user_id}/consents`, `POST /api/users/{user_id}/consents/{purpose}/grant`.
- Swagger UI працюючого екземпляра: `GET /api/docs`, контракт: `GET /api/openapi.yaml`.
- Конвеєр `docs.yml`: markdownlint, Spectral, аудит `review_date`, `mkdocs build --strict`, деплой.
- Front matter-паспорти сторінок, `CODEOWNERS`, чек-лист docs-or-don't-merge.

### Змінено

- Паспорт SDD / ISD / регламент / handover перенесено в `docs/architecture/` (старі адреси переспрямовуються).
- JSON-маршрути `/api/...` повертають помилки 404 / 403 / 500 єдиним об'єктом `Error`, а не HTML-сторінкою.

### Виправлено

- API 1.0.1: у контракті `GET /api/cart/count` прибрано оголошену, але не перевірювану cookie-автентифікацію
  (знайдено контрактним тестом Schemathesis).

## [docs-v1.0] — 2026-11-22

### Додано

- Архітектурний паспорт Лаб.10: README, SDD, ISD, ADR-0001, ADR-0002, регламент, handover.
