---
title: Pre-commit хук
owner: Загребенюк Б. (booooooo76)
status: published
review_date: 2027-02-20
tags:
  - ops
---

# Лаб.6, Завдання 3. Локальний «воротар якості»: pre-commit хук складності

## 1. Де лежить хук і чому не в `.git/hooks/`

Хук це файл `.githooks/pre-commit` (без розширення, виконуваний: `git update-index --chmod=+x`). У репозиторії з Лаб.3
налаштовано `git config core.hooksPath .githooks`: Git шукає хуки в цій теці, а не в `.git/hooks/`. Перевага: хук
версіонується разом із кодом і однаковий у всіх клонах (`.git/hooks/` не потрапляє в репозиторій). Файл у `.git/hooks/`
при такому налаштуванні Git просто проігнорував би.

Хук має два етапи: 1) секрети (gitleaks, Лаб.3); 2) **складність** (Лаб.6).

## 2. Що робить етап складності

1. Бере **лише staged-файли** Python: `git diff --cached --name-only --diff-filter=ACMR -- '*.py'`.
2. Вивантажує саме їхні **staged-версії** (`git checkout-index --prefix=<тимчасова тека>`): у коміт піде вміст індексу,
   а не робоча копія, тому перевіряється саме він.
3. Запускає lizard з лімітом: `python -m lizard -l python -C 10 -w <файли>`. Код виходу 0 означає «порушень немає»,
   тоді коміт проходить одразу.
4. Інакше розбирає вивід (`файл:рядок: warning: функція has … N CCN …`) і для кожного порушення перевіряє
   `.complexity-baseline`:
   * функція є в базовій лінії і її CC не більший за записаний → старий борг, коміт не блокується;
   * функції немає в базовій лінії (нова) **або** її CC став більшим → **порушення**.
5. Є порушення: червоне повідомлення з файлом, рядком, функцією і CC, **код виходу 1**, і Git скасовує коміт.
   Немає: код 0, коміт створюється.
6. Якщо сканер упав не через складність (наприклад, синтаксична помилка у файлі), хук теж блокує коміт (fail closed).

**Базова лінія (`.complexity-baseline`).** У проєкті до появи хука вже було 19 функцій із CC > 10 (зокрема `edit_news` 21,
`sql_console` 20, `sanitize_value` 17, а також кілька службових скриптів Лаб.5–6). Без базової лінії будь-яка правка в
таких файлах блокувалася б. Тому борг зафіксовано поіменно з поточним CC і діє правило «храповика»: стара функція може
лише покращуватись, а все нове мусить бути ≤ 10. Генерація: `python tools/complexity_baseline.py > .complexity-baseline`.

## 3. Перевірки поведінки хука (без коміту)

| Сценарій | Очікування | Результат |
|---|---|---|
| новий файл без порушень | PASS, код 0 | PASS: «every function in staged files has CC <= 10» |
| правка у файлі зі старим боргом, CC не змінився (`slo_decision.decide` 19) | PASS, код 0 | PASS: «1 legacy function(s) within baseline» |
| стару функцію погіршено (`decide` 19 → 20) | BLOCK, код 1 | «COMPLEXITY VIOLATION … CC = 20 (got worse: baseline CC 19)» |

## 4. Демонстрація FAIL → PASS

Сценарій методички: нова функція з CC = 12 не комітиться; після Data-Driven рефакторингу (CC 1..2) комітиться.
Скріншоти: `Лаб 6\screenshots\t3_*`.

## 5. Результати демонстрації

**FAIL (краш-тест).** У `models/delivery.py` додано функцію `delivery_days(delivery_type, region, express)` (термін
доставки замовлення в робочих днях) з глибокою вкладеністю умов: **CC = 12** (radon `C (12)`, lizard 12).
`git add models/delivery.py` + `git commit -m "feat: add messy code"`:

```text
pre-commit: lizard, cyclomatic complexity limit CC <= 10, staged files:
  models/delivery.py
  COMPLEXITY VIOLATION: models/delivery.py:4  delivery_days()  CC = 12  (limit CC 10)

pre-commit: COMMIT BLOCKED - 1 function(s) exceed the architectural limit CC <= 10.
git exit code: 1
```

Коміт не створено: `git log` не змінився (скріншот `t3_1_hook_FAIL_blocked.png`).

**PASS (відновлення).** Функцію переписано через довідник даних, як у Завд.2:

```python
REGION_GROUP = {'Chernivtsi': 'Chernivtsi', 'Kyiv': 'Kyiv'}
DELIVERY_DAYS = {
    ('pickup',  'Chernivtsi', False): 0, ('pickup',  'Chernivtsi', True): 0,
    ...                                       # 18 рядків: 3 способи × 3 групи регіонів × 2 значення терміновості
    ('post',    'other',      False): 4, ('post',    'other',      True): 2,
}

def delivery_days(delivery_type, region, express):
    try:
        return DELIVERY_DAYS[(delivery_type, REGION_GROUP.get(region, 'other'), bool(express))]
    except KeyError:
        raise ValueError(f'unknown delivery type: {delivery_type}') from None
```

**CC = 2** (radon `A (2)`; одиниця за `except`, що зберігає стару поведінку з `ValueError` для невідомого способу доставки).
Еквівалентність перевірено на 180 комбінаціях вхідних даних (зокрема невідомі міста, невідомі способи, «truthy» значення
`express`): результати старої й нової версії однакові. Тести: `tests/test_delivery.py` (16).
Коміт пройшов: `pre-commit: PASS - every function in staged files has CC <= 10`, `git exit code: 0`
(скріншот `t3_2_hook_PASS_committed.png`).

**«Храповик» (додатково).** Стару функцію з базової лінії `slo_decision.decide` штучно погіршено з CC 19 до 20: хук
заблокував коміт з поясненням `got worse: baseline CC 19` (скріншот `t3_3_hook_ratchet_legacy_worse.png`); зміну скасовано.

## 6. Висновок

Хук прибирає людський фактор: заплутаний код фізично не може потрапити в історію без явного `--no-verify`. Він дивиться
лише на те, що йде в коміт (staged-версії файлів), читає код виходу lizard і розбирає його вивід, а старий борг не
блокує роботу, але й не дає йому рости. Ліміт 10 узгоджено з рефакторингом Завд.2: обидві функції, переписані через
довідники даних, мають CC 1 і 2.

## Пов'язані у базі знань

[[isd]] · [[code-standards]] · [[secrets_prevention]] #ops
