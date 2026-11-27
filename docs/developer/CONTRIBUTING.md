---
title: Як зробити внесок
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-02-20
tags:
  - developer
  - ops
---

# Як зробити внесок (CONTRIBUTING)

Рівень 2 піраміди: **як приєднатися до розробки**. Спершу підніміть середовище за
[інструкцією](local-setup.md), стандарти коду — у [стандартах](code-standards.md).

## Потік роботи

1. Гілка від актуальної: `feat/<тема>`, `fix/<тема>`, `docs/<тема>`.
2. Коміти в стилі Conventional Commits: `feat(api): add health endpoint`, `docs(ci): ...`; без апострофів.
3. Перед комітом спрацює хук (`git config core.hooksPath .githooks`): gitleaks + складність lizard CC ≤ 10.
4. Pull request за шаблоном `.github/pull_request_template.md`; рев'ю власника з `.github/CODEOWNERS`.
5. Злиття лише після зеленого CI: `quality-metrics` (код) і `docs` (документація).

## Definition of Done: docs-or-don't-merge

Pull request, що змінює **публічну поведінку** (новий або змінений ендпоінт, формат відповіді, конфігурація,
змінна оточення, порядок розгортання), не зливається, поки не виконано **всі** пункти:

- [ ] оновлено документацію в `docs/` (SDD — компоненти й контракти, ISD — запуск і конфігурація);
- [ ] оновлено контракт `docs/api/openapi.yaml`, версія `info.version` піднята за SemVer;
- [ ] `spectral lint docs/api/openapi.yaml` — 0 errors;
- [ ] `markdownlint` і `mkdocs build --strict` проходять (у CI це робить `docs.yml`);
- [ ] додано запис у `CHANGELOG.md`;
- [ ] у зачеплених сторінках оновлено `review_date` у front matter;
- [ ] `python tools/doc_currency.py` показує `RESULT: PASS`;
- [ ] операція з кількома записами в БД виконується в одній транзакції `transaction()`, а повторний запит
      (подвійне натискання, повтор проксі) не змінює дані вдруге ([ADR-0003](../architecture/adr/0003-atomic-multi-write.md),
      перевіряє pre-commit, етап 3 `tools/atomicity_check.py`).

| Перевірка DoD | Інструмент | Що ловить |
|---|---|---|
| Контракти | Spectral | операція без опису, схема без прикладу, неузгоджені помилки |
| Розмітка | markdownlint | зламані списки, заголовки, блоки коду |
| Посилання | `mkdocs build --strict` | мертве посилання, сторінка поза навігацією, зламаний синтаксис |
| Актуальність | `tools/doc_review_dates.py` | прострочений `review_date` |
| Атомарність | `tools/atomicity_check.py` (pre-commit) | нова функція з ≥ 2 записами поза транзакцією (клас дефекту INC-001) |

## Життєвий цикл сторінки

`status` у front matter: `draft` → `in-review` → `published` → `deprecated`. Застарілу сторінку не видаляють:
ставлять `status: deprecated`, додають банер із посиланням на актуальний документ і переспрямування в `mkdocs.yml`
(плагін `redirects`). Мажорні зміни документації позначаються тегом `docs-vX.Y`.

## Пов'язані

[[local-setup]] · [[code-standards]] · [[maintenance]] · [[openapi-contract]] #developer
