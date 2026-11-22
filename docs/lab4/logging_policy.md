---
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-04-16
tags:
  - architecture
---

# Лаб.4, Завд.1: Secure Logging та маскування PII

Усі значення в документі синтетичні (`example.test`, `203.0.113.x`, вигадані паролі).

## 1. Вихідна проблема

До Лаб.4 застосунок не використовував модуль `logging`: діагностика складалась із 57 викликів
`print(f"Error ...: {e}")` у 7 файлах, глобального `print(f"GLOBAL ERROR: {e}")` і трейсбеків `traceback.print_exc()`.
Головний канал витоку: **текст винятку**. Повідомлення СУБД цитують значення рядка, і локалізований Postgres робить це так
(це реальний фрагмент помилки з наших власних тестів):

```text
Помилковий рядок містить (1, 1, Control Person 1, +380500000001, demo_u1@example.test, laptop, null, ...)
```

Кореляції запитів не було, а тіла запитів ніде не логувались (перевірено; тепер це закріплено тестом).

## 2. Політика логування

Політика живе в `privacy/policy.py` і є **кодом, який виконується**, а не описом: тести проходять по кожному ключу реєстру.

| Рівень | Що робимо | Ключі |
|---|---|---|
| **Дозволено як є** | Технічні поля без PII, потрібні для діагностики | `actor_id`, `correlation_id`, `duration_ms`, `error_type`, `event`, `event_type`, `method`, `operation`, `path`, `policy_version`, `purpose`, `record_id`, `request_id`, `result`, `role`, `status`, `status_code`, `subject_id`, `table`, `timestamp`, `user_id` |
| **Редагується повністю** `[REDACTED]` | Паролі, токени, ключі, сесії, адреси: часткове розкриття не має сенсу | `access_token`, `address`, `api_key`, `apikey`, `authorization`, `confirm_password`, `cookie`, `csrf_token`, `delivery_address`, `passwd`, `password`, `password_hash`, `pwd`, `refresh_token`, `reset_token`, `secret`, `secret_key`, `session`, `session_id`, `set-cookie`, `token`, `verification_token`; а також будь-який ключ, що **містить** `password`, `secret`, `token`, `api_key`, `authorization`, `cookie` (наприклад `new_password`, `resetToken`) |
| **Маскується частково** | Корисно для діагностики, але не ідентифікує особу | таблиця нижче |
| **Заборонено** | Повні тіла запитів і відповідей (`request.form`, `request.json`, `request.data`, файли); сирий текст винятків із цитованими значеннями рядків БД; логін чи email у подіях безпеки | перевіряє тест `test_code_never_logs_whole_request_bodies` |

Правила часткового маскування:

| Тип | Приклад | Результат |
|---|---|---|
| `email` | `demo.user@example.test` | `d***@example.test` (перший символ і домен) |
| `phone` | `+380500000001` | `+380*******01` (код країни й дві останні цифри) |
| `name` | `Demo Person` | `D***` |
| `ip` | `203.0.113.7` | `203.0.113.x` (усічено останній октет) |

Ключі, що маскуються:

| Ключ | Тип |
|---|---|
| `client_email` | email |
| `email` | email |
| `user_email` | email |
| `ip` | ip |
| `ip_address` | ip |
| `client_name` | name |
| `first_name` | name |
| `full_name` | name |
| `guest_login` | name |
| `last_name` | name |
| `login` | name |
| `surname` | name |
| `client_phone` | phone |
| `phone` | phone |

Події безпеки (реєстрація, вхід) містять лише **факт**, `actor_id`, `subject_id`, `result`, час і correlation ID. Сигнатура
`security_event(logger, event, *, actor_id, subject_id, result)` навмисно закрита: вільного тексту або PII-полів у ній немає,
тож продублювати PII в такому записі неможливо. Невдалий вхід не містить введеного логіну.

## 3. Централізований механізм: захист у три шари

Ручне маскування в окремому контролері не повторюється в інших місцях, тому механізм **один**, і він діє на виході, а не в бізнес-коді:

| Шар | Файл / клас | Що робить |
|---|---|---|
| 1. Фільтр обробника | `privacy/secure_logging.py`, `PIISanitizingFilter` | Знеособлює повідомлення, аргументи (`%s`), поля `extra=`, текст винятку, трейсбек. Вішається на **обробник** (handler), бо фільтр logger-а не діє на записи, що прийшли від дочірніх логерів |
| 2. Форматери | `SanitizingFormatter`, `JsonFormatter` | Знеособлюють уже готовий рядок: якщо десь забули фільтр, PII усе одно не вийде |
| 3. Потік виводу | `SanitizingStream`, `install_stream_guard()` | Обгортка над `sys.stdout/stderr`: старі `print(...)` теж проходять через рушій, і жоден із 57 викликів не довелось переписувати |

Рушій `privacy/sanitizer.py` загальний для всіх шарів. **Fail closed:** якщо знеособлення саме впало, у лог іде повідомлення
`[log record dropped: sanitizer error]`, а не сирий запис. Рушій **ідемпотентний**: повторне застосування нічого не псує.

Точки інтеграції:

| Де | Що |
|---|---|
| `app.py` після `app.config.from_object(Config)` | `configure_logging(app)`, `init_request_context(app)`, `logger = logging.getLogger('kursova.app')` |
| `app.py`, `register()` | `print` + `traceback.print_exc()` замінено на `logger.exception('registration_failed')`; подія `USER_REGISTERED` |
| `app.py`, `login()` | події `LOGIN` (SUCCESS/FAILURE) |
| `app.py`, глобальний обробник помилок | `logger.error('unhandled_exception', exc_info=e)` замість `print(f"GLOBAL ERROR: {e}")` |
| `app.py`, запуск сервера | `install_stream_guard()` перед `app.run(...)` |
| Flask / Werkzeug | `configure_logging(app)` прибирає незахищений обробник Flask; access-лог Werkzeug (IP, URL із query) іде через ті самі правила |

**Correlation ID.** Кожен запит отримує ідентифікатор: з заголовка `X-Request-ID`, якщо він у безпечному форматі
(`[A-Za-z0-9._-]`, 8–64 символи), інакше генерується випадковий. Він додається в кожен рядок логу й повертається клієнту в
`X-Correlation-ID`. Чужий ідентифікатор не приймається «як є» для захисту від підробки рядків логу (log injection).

## 4. Приклади одного й того самого повідомлення до та після

Усі дані синтетичні. Виведено командою `python scripts/logging_demo.py`.

**До** (як було б, якби повідомлення надрукували як є):

```text
profile update: email=demo.user@example.test phone=+380500000001 password=synthetic-password-value token=synthetic-session-token-value ip=203.0.113.7
```

**Після, текстовий формат:**

```text
2026-10-10 23:00:01,460 INFO kursova.demo [-] profile update: email=d***@example.test phone=+380*******01 password=[REDACTED] token=[REDACTED] ip=203.0.113.x
```

**Після, структурований JSON** (формат не зруйновано, `operation` і `user_id` збережено, є `correlation_id`):

```text
{"timestamp": "2026-10-10T20:00:01.460+00:00", "level": "INFO", "logger": "kursova.demo", "correlation_id": "-", "message": "profile_update", "email": "d***@example.test", "phone": "+380*******01", "password": "[REDACTED]", "operation": "PROFILE_UPDATE", "user_id": 7}
```

**Події безпеки зі справжнього застосунку** (БД підмінено, жодного PII):

```text
2026-10-10 23:00:01,637 INFO kursova.app [1bdc3596df224535] security_event event=USER_REGISTERED actor_id=None subject_id=7 result=SUCCESS
2026-10-10 23:00:01,637 INFO kursova.app [0a7ce4804ae44ebb] security_event event=LOGIN actor_id=None subject_id=12 result=FAILURE
```

**Повідомлення винятку** (`Key (email)=(...)` цитує значення, рядок БД теж):

```text
2026-10-10 23:00:01,460 ERROR kursova.demo [-] save_failed
Traceback (most recent call last):
  ...
RuntimeError: DETAIL: Key (email)=([REDACTED]) already exists. password=[REDACTED]
```

**Старий `print(...)`** (шар 3):

```text
Error in legacy handler: email=d***@example.test password=[REDACTED] phone=+380*******01
```

## 5. Тести (`tests/test_secure_logging.py`, 74 тести)

```text
python -m pytest tests/test_secure_logging.py -q
```

| Група | Що доводить |
|---|---|
| Окремі маскувальники й формати тексту | форма маски, JSON лишається валідним JSON, Bearer/JWT, повідомлення БД (англ. і укр.) |
| **Діагностика не руйнується** | час, id, correlation ID, коди статусу, суми проходять без змін |
| Ідемпотентність | повторне знеособлення нічого не змінює |
| **Політика як код** | кожен ключ із `LOG_REDACTED_KEYS` та `LOG_MASKED_KEYS` справді обробляється |
| **Фактичний вивід логера (позитивні)** | текст, `%s`-аргументи, `extra=`, JSON-лог, виняток із трейсбеком |
| **Негативний сценарій** | PII у **вкладеному DTO** (аргумент, f-string, `repr`, `extra`) та в **повідомленні винятку** |
| **Мета-тест** | той самий запис без захисту робить `assert_no_leak` червоним: перевірка справді вміє падати |
| Другий шар і fail closed | форматер без фільтра теж захищає; збій рушія не виводить сирий запис |
| **Формат лога не руйнується охоронцем** | рядки JSON-логу, що проходять через `SanitizingStream`, лишаються окремими валідними JSON-рядками (регресійний тест, див. нижче) |
| Через справжній застосунок | реєстрація (помилка й успіх), вхід (невдалий), глобальний обробник, Flask-logger, access-лог Werkzeug, correlation ID |
| **Не логувати зайве** | AST-перевірка: жоден `print` чи виклик логера в `app.py`, `routers/`, `models/` не містить `request.form/json/data/files`; мета-тест на порушенні |

**Мутаційна перевірка.** Якщо вимкнути фільтр, форматери й рушій (окремим pytest-плагіном, без змін коду), **12 тестів «фактичного виводу» падають**
(текст, `%s`, JSON, виняток, вкладений DTO, виняток із DTO, шар 2, Werkzeug/Flask, шар 3, формат JSON-логу через охоронець, реєстрація, глобальний обробник). Із увімкненим захистом усі зелені.
Це доводить, що тести ловлять витік, а не просто «проходять».

**Знайдена й виправлена вада (під час підготовки до захисту).** Охоронець виводу (шар 3) перезбирав кожен записаний рядок, що є цілим JSON-об'єктом,
через `json.dumps` і при цьому втрачав символ кінця рядка. У справжньому сервері з `LOG_FORMAT=json` рядки логу склеювались в один,
тобто формат лога руйнувався, а методичка вимагає цього не допускати. Тести цього не ловили: формат перевірявся з `StringIO` без охоронця. Тепер `SanitizingStream.write`
відокремлює кінцеві переводи рядка до санітизації, а регресійний тест `test_stream_guard_keeps_json_log_lines_separate` падає на старому коді
і проходить на виправленому. Перевірено на сервері: `LOG_FORMAT=json` дає окремі валідні JSON-рядки.

## 6. Відомі межі (чесно)

* **Ім'я в довільному тексті без ключа не знайти.** Ім'я розпізнається за *ключем* (`full_name`, `login`, `client_name`...). У рядку на кшталт `user=Іван`
  автоматично його не виявити, тому політика вимагає логувати `user_id`, а не імена.
* **Адреси**: редагуються за ключем (`address`, `delivery_address`), у вільному тексті не розпізнаються.
* **Чотирикомпонентні версії** (`8.3.3.1`) схожі на IPv4 і маскуються (`8.3.3.x`): свідомий вибір на користь приватності.
* Рядки коду всередині трейсбеку теж проходять знеособлення, тому цитований вихідний код може трохи змінитись: це безпечна поведінка.
* Регулярні вирази ловлять відомі шаблони (email, телефони у типових форматах, Bearer, JWT). Це не гарантія для довільного нового формату.

## Пов'язані у базі знань

[[0002-privacy-by-design-module]] · [[sdd]] · [[consent]] · [[pii_inventory]] #architecture
