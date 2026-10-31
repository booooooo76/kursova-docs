# Лаб.7, Завдання 1. Інформаційний семантичний аудит `anonymize_subject` за Чепіним

## 1. Об'єкт аналізу

| | |
|---|---|
| Метод | `privacy/erasure.py :: anonymize_subject(subject_id, actor_id)` |
| Архітектурна роль | транзакційний сервіс права на видалення (GDPR ст. 17, Лаб.4): в одній транзакції блокує суб'єкта, відкликає згоди, знеособлює або видаляє його дані у 18 таблицях за реєстром політик і пише подію аудиту |
| Контур | інтеграційний: робота з PostgreSQL через з'єднання, курсор, `SELECT ... FOR UPDATE` і `COMMIT` |
| Цикломатична складність | **CC = 4** (radon `A (4)`, lizard `CCN 4`): два `if` + один `for` + 1 |
| Чому саме він | майже лінійний (Мак-Кейб «сліпий»: CC 4 ≤ 5), але інтенсивно працює з даними: 2 аргументи, 8 локальних змінних, два змінюваних словники, які передаються в інші підсистеми |

```python
def anonymize_subject(subject_id, actor_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT login, anonymized_at FROM keys WHERE user_id = %(uid)s FOR UPDATE', {'uid': subject_id})
            subject = cur.fetchone()
            if subject is None:
                return ErasureResult(NOT_FOUND)
            if subject['anonymized_at'] is not None:
                return ErasureResult(ALREADY_ANONYMIZED, subject['anonymized_at'])

            params = {
                'uid': subject_id,
                'login': subject['login'],
                'new_login': new_anonymous_login(),
                'unusable': secrets.token_hex(32),
            }
            affected = {'user_consents': len(consent.withdraw_all(cur, subject_id, actor_id))}
            for entity in processing_order():
                count = _apply_entity(cur, entity, params)
                affected[entity.table] = affected.get(entity.table, 0) + count

            cur.execute('INSERT INTO privacy_audit_log (...) VALUES (...)',
                        {'event': EVENT, 'actor': actor_id, 'uid': subject_id, 'result': 'SUCCESS', 'cid': get_correlation_id()})
            cur.execute('SELECT anonymized_at FROM keys WHERE user_id = %(uid)s', {'uid': subject_id})
            done_at = cur.fetchone()['anonymized_at']
        conn.commit()
    return ErasureResult(ANONYMIZED, done_at, affected)
```

## 2. Правила класифікації

| Клас | Вага | Коли присвоюється |
|---|---|---|
| **C** керуюча | 3 | змінна стоїть в умові `if` / `while` або керує циклом `for` (від неї залежить, яким шляхом піде виконання) |
| **M** модифікована | 2 | значення перезаписується (повторне присвоєння, присвоєння в тілі циклу), змінюється вміст (`d[k] = ...`) або стан об'єкта (`execute`, `fetchone`, `commit`) |
| **P** вхідна | 1 | значення лише читається в обчисленнях |
| **T** транзитна | 0,5 | змінна без змін передається далі: аргументом виклику іншої підсистеми або в складі параметрів SQL |

Ієрархія пріоритету: **C > M > P > T**, тобто змінна з кількома ролями отримує найважчу. Константи модуля (`EVENT`,
`NOT_FOUND`, `ANONYMIZED` ...), імена функцій і модулів не є змінними методу: їхнє значення фіксоване.

Факти використання кожної змінної (у яких рядках вона в умові, змінюється, передається чи читається) збирає з
синтаксичного дерева `tools/chapin_vars.py`; він застосовує ті самі правила й рахує Cch:

```powershell
.\venv\Scripts\python.exe tools\chapin_vars.py privacy\erasure.py anonymize_subject
```

## 3. Семантична матриця Чепіна (Baseline)

| № | Змінна | Тип даних | Клас | Інженерне обґрунтування ролі | Вага |
|---|---|---|---|---|---|
| 1 | `subject` | `RealDictRow \| None` (рядок `keys`) | **C** | від неї залежать обидві умови (`is None`, `anonymized_at is not None`), тобто вибір між трьома результатами; далі з неї читається логін (P), але C вища | 3 |
| 2 | `entity` | `EntityPolicy` (frozen dataclass реєстру) | **C** | змінна циклу `for`: керує тим, скільки разів і для яких таблиць виконується SQL; також передається в `_apply_entity` (T) | 3 |
| 3 | `cur` | `RealDictCursor` | **M** | стан курсора змінюється в самому методі: `execute` × 3, `fetchone` × 2 (буфер результату й `rowcount` перезаписуються); також передається в `withdraw_all` і `_apply_entity` (T) | 2 |
| 4 | `conn` | `psycopg2.connection` | **M** | `conn.commit()` змінює стан транзакції (фіксує всі зміни); також створює курсор | 2 |
| 5 | `affected` | `dict[str, int]` | **M** | словник-накопичувач: вміст змінюється на кожній ітерації (`affected[table] = ... + count`) | 2 |
| 6 | `count` | `int` | **M** | перезаписується на кожній ітерації циклу новою кількістю рядків | 2 |
| 7 | `subject_id` | `int` | **T** | аргумент, який без змін іде в параметри SQL, у `withdraw_all` і в аудит; у жодній умові не бере участі | 0,5 |
| 8 | `actor_id` | `int` | **T** | аргумент, який без змін прокидається у `withdraw_all` і в запис аудиту | 0,5 |
| 9 | `params` | `dict[str, int \| str]` | **T** | створюється один раз і лише передається в `_apply_entity`; **але це змінюваний словник**: будь-яка підсистема, що його отримала, може змінити його вміст для всіх наступних кроків | 0,5 |
| 10 | `done_at` | `datetime` | **T** | читається з БД один раз і без змін передається в `ErasureResult` | 0,5 |

## 4. Розрахунок

P = 0, M = 4 (`cur`, `conn`, `affected`, `count`), C = 2 (`subject`, `entity`), T = 4 (`subject_id`, `actor_id`, `params`, `done_at`).

**Cch = 1·P + 2·M + 3·C + 0,5·T = 1·0 + 2·4 + 3·2 + 0,5·4 = 0 + 8 + 6 + 2 = 16**

## 5. Аналіз ризику

Cch = 16 > 10: за Enterprise-критерієм для лінійних методів це **архітектурний хаос у даних**, хоча за Мак-Кейбом метод
простий (CC = 4). Різниця показує, що Мак-Кейб рахує лише розгалуження, а Чепін бачить, скільки змінних і в яких ролях
доводиться тримати в голові.

* 50% ваги (8 із 16) дають чотири M-змінні. Кожна з них це місце, де значення може бути перезаписане не тоді або не тим:
  накопичувач `affected` і лічильник `count` живуть усередині циклу, а `cur` і `conn` несуть стан транзакції.
* Найнебезпечніша змінна має найменшу вагу: `params` формально T (0,5), бо метод її не змінює. Але це звичайний `dict`,
  який метод віддає в `_apply_entity` на кожній із 18 ітерацій. Ніщо не заважає підсистемі, що отримала словник
  (або «копії» `x = params`, яка насправді є тим самим об'єктом), змінити `params['login']`. Тоді всі наступні SQL
  шукатимуть записи за чужим логіном, а таблиця `registration_requests` (шукається саме за старим логіном, 8-ма в
  черзі) лишиться з персональними даними. Це дефект мутації, і в Завданні 2 його змодельовано.
* Ризик підсилює роль методу: це незворотна операція GDPR. Пропущений рядок означає витік персональних даних, а
  повторний запуск його не виправить, бо після першого запуску старого логіна вже ніде немає.
