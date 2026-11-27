---
title: Реєстр ADR
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-05-21
tags:
  - architecture
---

# Architecture Decision Records

Кожне архітектурне рішення записується окремим файлом `NNNN-назва.md` за шаблоном: номер, статус, контекст,
розглянуті альтернативи, рішення, наслідки. Записане рішення **не переписується заднім числом**: якщо його замінено,
старий ADR отримує статус `Superseded by ADR-NNNN`, а нове рішення отримує новий номер.

| № | Рішення | Статус | Дата рішення |
|---|---|---|---|
| [0001](0001-postgresql-psycopg2.md) | PostgreSQL і чистий SQL через psycopg2 без ORM | Accepted | 2025-10-17 |
| [0002](0002-privacy-by-design-module.md) | Приватність як окремий модуль: анонімізація, згоди за цілями, аудит без PII | Accepted | 2026-10-10 |
| [0003](0003-atomic-multi-write.md) | Операції з кількома записами — в одній транзакції, ідемпотентно | Accepted | 2026-11-27 |

Статуси: `Proposed` → `Accepted` → (`Deprecated` | `Superseded by ADR-NNNN`).

Власник реєстру: Загребенюк Б. · цикл перегляду 180 днів · переглянуто 2026-11-27.

## Пов'язані у базі знань

[[0001-postgresql-psycopg2]] · [[0002-privacy-by-design-module]] · [[0003-atomic-multi-write]] · [[sdd]] #architecture
