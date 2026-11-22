---
title: Стандарти коду
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-05-21
tags:
  - developer
---

# Стандарти коду

Правила, що виросли з лабораторних робіт і перевіряються автоматично.

| Правило | Звідки | Як перевіряється |
|---|---|---|
| Quality Gate «Sonar way»: нових багів і вразливостей 0, дублікати < 3 % | Лаб.1 | SonarQube, `scan.ps1`, `sonar-project.properties` |
| Жодних секретів у коді; конфігурація лише з оточення (`config.py`) | Лаб.3 | gitleaks у pre-commit, `.gitleaks.toml` |
| Персональні дані не потрапляють у журнали | Лаб.4 | `privacy/sanitizer.py`, тести безпечного журналу |
| Цикломатична складність нової функції ≤ 10 | Лаб.6 | lizard у pre-commit, борг у `.complexity-baseline` |
| Таблиця правил замість довгих `if/elif` | Лаб.6 | рев'ю |
| Незмінні Value Objects для параметрів складних операцій | Лаб.7 | рев'ю, `services/values.py` |
| Залежність від контрактів (`typing.Protocol`), а не від реалізацій; композиція замість успадкування | Лаб.8 | рев'ю, `services/contracts.py` |
| SQL лише параметризований через `models/database.py` | ADR-0001 | рев'ю |
| Файли в UTF-8, `.ps1` з BOM, 4 пробіли в Python | Лаб.5 | `.editorconfig` |
| Conventional Commits, без апострофів у повідомленнях | Лаб.3 | рев'ю історії |
| Зміна коду = зміна документації | Лаб.10 | `tools/doc_currency.py`, CI `docs.yml` |

## Пов'язані

[[CONTRIBUTING]] · [[0001-postgresql-psycopg2]] · [[sdd]] #developer
