# Лаб.11, Завд.3 — Протокол краш-тесту «не збирається — не їде»

Публічний репозиторій: <https://github.com/booooooo76/kursova-docs>, сайт: <https://booooooo76.github.io/kursova-docs/>.
Kursova приватний, тому `scripts/publish_docs.ps1` переносить туди лише файли бази знань (git filter-repo, історія й
повідомлення комітів зберігаються, автори — noreply). Конвеєр `.github/workflows/docs.yml`.

| Запуск | Коміт (Kursova → kursova-docs) | Результат | Що сталося |
|---|---|---|---|
| #1 45029400914 | `51eb266` review README and SDD | ❌ | непланований: markdownlint MD036 у README (курсив замість заголовка) — конвеєр зловив дефект, внесений після локального лінту |
| #2 45029493818 | `3a882ef` fix README passport line | ✅ build + deploy | перша публікація сайту |
| #3 45029668763 | `03b316a` → `5c90bd5` **docs(ci): inject broken reference into strict build, FAIL** | ❌ build, deploy пропущено | `mkdocs build --strict`: посилання `rollback-runbook.md` не знайдено, `Aborted with 1 warnings in strict mode!`, Exit Code 1; сайт лишився попередньої версії |
| #4 45029806721 | `eab75fd` → `0738475` **docs(ci): restore strict build pipeline, PASS** | ✅ build + deploy | посилання замінено якорем на порядок підняття; сайт оновлено, дата редагування сторінок проставлена плагіном |

Текст помилки з журналу запуску #3: `docs/lab11/data/ci_fail_run_45029668763.log`.

Теги версій документації: `docs-v1.0` (паспорт Лаб.10, `b498b3b`) і `docs-v2.0` (база знань Лаб.11, `eab75fd`)
опубліковані в `kursova-docs`; знімок документації відновлюється `git checkout docs-v1.0`.
