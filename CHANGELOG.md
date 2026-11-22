# Changelog

Формат — [Keep a Changelog](https://keepachangelog.com/uk/1.1.0/); версія контракту API — за SemVer
(`info.version` у `docs/api/openapi.yaml`), версії документації — теги `docs-vX.Y`.

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
