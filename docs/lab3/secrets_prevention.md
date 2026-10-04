# Лаб.3 Завд.3 — Secrets Leak Prevention

Реальних секретів у цьому документі немає. Усі значення в логах приховані (`--redact`), а токен у краш-тесті синтетичний.

## 1. Інструмент і команди

| | |
|---|---|
| Secret scanner | `Gitleaks 8.30.1` (встановлення: `winget install Gitleaks.Gitleaks`) |
| Конфігурація | `.gitleaks.toml`: стандартні правила (`useDefault = true`) і 2 власні |
| Автоматичний бар'єр | git hook `.githooks/pre-commit` (підключається `git config core.hooksPath .githooks`) |
| Ручна перевірка | `.\scripts\secrets_scan.ps1` (staged) і `.\scripts\secrets_scan.ps1 -History` (усі гілки) |
| Основна команда | `gitleaks git . --config .gitleaks.toml --staged --redact --no-banner -v` |
| Код завершення | `0` — чисто, `1` — знайдено секрет. Саме ненульовий код скасовує `git commit` |

Hook перевіряє **staged-зміни**, тобто те, що саме збирається потрапити в коміт. Якщо gitleaks не знайдено, hook блокує коміт (fail closed), а не пропускає його мовчки.

## 2. Початковий стан: що було в репозиторії

У першому коміті `a68b439` (2025-10-17) були реальні `DB_PASSWORD` і `SECRET_KEY`: двічі в `config.py` (запасні значення `os.environ.get('X') or '...'`) і двічі в закоміченому тоді `.env`. `.env` прибрали з відстеження пізніше (коміт `7ab8346`), але з історії значення нікуди не зникли.

Важливе спостереження: **Gitleaks зі стандартними правилами по всій історії (усі гілки) не знайшов нічого.** Типові правила тримаються на форматі відомих токенів та ентропії, тому не бачать короткий пароль і конструкцію `os.environ.get(...) or '...'`. Відсутність знахідок не доводить відсутності секретів.

Тому додано два власні правила (`.gitleaks.toml`):

| Правило | Що ловить |
|---|---|
| `hardcoded-config-fallback` | секрет, захардкоджений як запасне значення: `…PASSWORD/SECRET/TOKEN/KEY… = os.environ.get('X') or '…'` |
| `dotenv-secret-value` | файл з іменем `.env` зі значенням секрету (`.env.example` з плейсхолдерами не підпадає) |

З власними правилами скан історії дає **4 знахідки, усі в `a68b439`**: `config.py` рядки 7 і 14, `.env` рядки 1 і 6.

## 3. Контрольне порушення: FAIL

У спеціальному файлі `secrets_trap.py` створено синтетичне значення у форматі GitHub-токена (`ghp_` + 36 випадкових символів, згенерованих під час демо; воно не відкриває доступу до жодного сервісу). Файл додано в staging і виконано коміт:

```
> git commit -m 'test: secrets trap'; "exit: $LASTEXITCODE"
Finding:     API_TOKEN = 'REDACTED
Secret:      REDACTED
RuleID:      github-pat
Entropy:     5.171928
File:        secrets_trap.py
Line:        1
Fingerprint: secrets_trap.py:github-pat:1

6:23PM INF 0 commits scanned.
6:23PM INF scanned ~55 bytes (55 bytes) in 114ms
6:23PM WRN leaks found: 1

pre-commit: COMMIT BLOCKED - a secret was found in staged changes (see above).
Fix: read the value from an environment variable, keep it in .env (gitignored),
and leave only an empty placeholder in .env.example.
exit: 1
```

Коміт не створено: `git log --oneline -1` лишився на `db2b707`. Секрет не потрапив в історію.

Додатково (в ізольованому клоні) перевірено ще три порушення: повернення запасного пароля в `config.py`, примусово додане `git add -f .env`, відсутність gitleaks на машині. Усі три блокують коміт.

## 4. Безпечна конфігурація

**Читання з Environment Variable (`config.py`).** Секрети беруться лише зі змінних середовища, запасних значень у коді немає. Якщо змінну не задано, застосунок не стартує:

```python
def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Не задано змінну середовища {name}. "
                           "Скопіюйте .env.example у .env і заповніть значення.")
    return value

class Config:
    SECRET_KEY = _require_env('SECRET_KEY')
    DB_PASSWORD = _require_env('DB_PASSWORD')
```

**`.gitignore`.** Локальний файл зі значеннями не відстежується git:

```
# Environment variables / secrets
.env
```

**`.env.example`.** Шаблон без реальних значень. Секрети порожні навмисно: з порожнім значенням застосунок не стартує, тож забути їх заповнити неможливо:

```
SECRET_KEY=
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=
```

**Тести.** `conftest.py` задає явно неробочі тестові значення (`os.environ.setdefault`), тому pytest не залежить від локального `.env` і не потребує реальних секретів. Перевірено у свіжому клоні без `.env`: `17 passed`.

## 5. Усунення порушення і PASS

Токен із файлу-пастки замінено на читання зі змінної середовища, у `.env.example` додано порожній плейсхолдер `API_TOKEN=`, значення передано через `$env:API_TOKEN`:

```
> $env:API_TOKEN = $tok; python -c "import secrets_trap; print('token from env:', bool(secrets_trap.API_TOKEN))"
token from env: True
> git add secrets_trap.py .env.example
> git diff --cached | Select-String 'ghp_'          # порожньо: у staged-змінах токена немає
> git commit -m 'fix: trap - token from environment'; "exit: $LASTEXITCODE"
6:26PM INF 0 commits scanned.
6:26PM INF scanned ~62 bytes (62 bytes) in 105ms
6:26PM INF no leaks found
[demo/secrets-trap 2535167] fix: trap - token from environment
exit: 0
```

**Очищення Git-стану.** Токена немає ні в staged, ні в історії жодної гілки:

```
> git log --all --oneline -S'ghp_'                  # порожньо
> git diff --cached --name-only                     # порожньо
> .\scripts\secrets_scan.ps1 -History; "exit: $LASTEXITCODE"
6:26PM INF 23 commits scanned.
6:26PM INF no leaks found
exit: 0
```

Краш-тест виконувався на одноразовій гілці `demo/secrets-trap`, яку після демо видалено, тому файли-пастки в основній історії немає. Під час `git add` токен у фазі FAIL git записав як недосяжний блоб у `.git/objects`. Він не належить жодному коміту чи гілці, і збирач сміття git його видалить. До історії він не потрапив саме тому, що hook зупинив коміт.

## 6. Реальні секрети з історії: відкликання

Вимога методички: реальний секрет у такій ситуації необхідно негайно відкликати й замінити. Виконано **2026-10-04**:

- пароль користувача Postgres змінено командою `ALTER USER … WITH PASSWORD …` (нове значення згенеровано криптостійким генератором, у чат і файли не потрапляло) і перевірено входом;
- `SECRET_KEY` згенеровано заново (`secrets.token_hex(32)`), що також інвалідує старі сесії;
- нові значення лежать лише в локальному `.env` (він у `.gitignore`).

Тому старі значення з історії **недійсні**. Історію git навмисно не переписували: це змінило б хеші всіх комітів і потребувало б force-push, а ризик усунено відкликанням.

Через це 4 історичні знахідки внесено в `.gitleaksignore` як вузький виняток: лише 4 відбитки (`коміт:файл:правило:рядок`), не правило і не файл цілком. Перевірено на клоні: без `.gitleaksignore` скан історії дає 4 знахідки (`exit 1`), з ним — 0. Нові знахідки, навіть у тих самих файлах, лишаються активними. Підстава винятку: значення відкликані, обґрунтування лежить у заголовку файлу.

## 7. Обмеження

- Hook локальний і налаштовується один раз на клон (`git config core.hooksPath .githooks`). Його можна обійти через `git commit --no-verify`. Для цього є ручний повний скан (`scripts/secrets_scan.ps1 -History`). CI-перевірку свідомо не додавали.
- Сканер евристичний. Власні правила написані під реальний патерн цього проєкту й не замінюють відкликання секретів.

## 8. Відтворення на чистому клоні

```
winget install Gitleaks.Gitleaks            # один раз
git config core.hooksPath .githooks         # підключити hook
copy .env.example .env                      # і заповнити свої значення
.\scripts\secrets_scan.ps1 -History         # exit 0 = чисто
```

## 9. Підсумок за шаблоном методички

| Показник | Початковий стан | Контрольне порушення | Фінальний стан |
|---|---|---|---|
| Secret scan, staged (hook) | PASS (змін немає) | **FAIL**: `github-pat`, `secrets_trap.py:1`, exit 1 | **PASS**, exit 0 |
| Secret scan, уся історія | стандартні правила: 0 знахідок (хибно); власні правила: **FAIL, 4** | — | **PASS**, exit 0 (4 відкликані відбитки в `.gitleaksignore`) |
| Git repository state | реальні секрети в історії (`a68b439`) | коміт заблоковано, `HEAD` не змінився | без секретів у коді, `.env` в `.gitignore`, значення відкликані |
