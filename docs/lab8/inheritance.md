# Лаб.8, Завдання 3. Вертикальний аудит успадкування (Лоренц-Кід) і Replace Inheritance with Composition

## 1. Baseline (коміт `ab6df23`)

Власних ієрархій у коді застосунку немає (класи проєкту успадковують лише бібліотечні: `logging.Formatter`, `Exception`,
`UserMixin`), тому за приміткою методички створено трирівневу ієрархію калькуляторів ціни, що продовжує ціноутворення
Завд.2 (`services/promotions.py`):

```
PriceCalculator                          звичайна ціна, підсумок, бали, чек         (14 публічних методів)
  └─ LoyaltyPriceCalculator              + знижка за рівнем лояльності, бонус балів  (+4, перевизначає 3)
       └─ HolidayLoyaltyPriceCalculator  + святкова знижка, ×2 бали, до гривні       (+3, перевизначає 6)
```

| Клас | DIT | NOC | PIM (публічний інтерфейс з успадкованим) | NMO (перевизначено) | NMA (додано) | WMC | LCOM* |
|---|---|---|---|---|---|---|---|
| PriceCalculator | 1 | 1 | 14 | 0 | 15 | 19 | 0,81 |
| LoyaltyPriceCalculator | 2 | 1 | 18 | 3 | 5 | 13 | 0,83 |
| **HolidayLoyaltyPriceCalculator** | **3** | 0 | **21** | **6** | 3 | 15 | 0,98 |

Перевизначені в листовому класі: `item_discount`, `order_discount`, `loyalty_points`, `rounding`, `describe`, `receipt`,
кожен через `super()`. Тобто поведінка `total()` листового класу розмазана по трьох рівнях. Орієнтири аномалії
методички (DIT ≥ 3, PIM > 20, масове перевизначення) виконано всі три. DIT і PIM/NMO рахує `tools/oo_metrics.py`:
SonarQube 9.9 Community для Python метрики DIT не має (див. Завд.1).

## 2. FAIL: каскадний злам (коміт `arch(audit): capture inheritance fragility crash, FAIL`)

Бізнес просить купони. Зміна лише на верхньому рівні: `PriceCalculator.__init__(lines, coupon=None)`, а
`order_discount(subtotal)` стає `order_discount(subtotal, coupon)`, і `total()` викликає `self.order_discount(subtotal,
self.coupon)`. Базовий клас працює (купон SALE5 дає 11 000 − 5 % = 10 450), але `self` у нащадків вказує на їхні
перевизначення зі старою сигнатурою:

```
TypeError: LoyaltyPriceCalculator.order_discount() takes 2 positional arguments but 3 were given
TypeError: HolidayLoyaltyPriceCalculator.order_discount() takes 2 positional arguments but 3 were given
```

**3 failed, 3 passed**: падають усі тести обох нащадків, хоча їхній код ніхто не чіпав. Щоб «полагодити», довелося б
аварійно правити `order_discount` і `__init__` (купон треба прокинути через `super().__init__`) на двох нижчих рівнях.
Це і є крихкий базовий клас (Fragile Base Class): нащадок залежить від деталей реалізації батька.

## 3. PASS: композиція (коміт `refactor(audit): replace inheritance with composition pattern, PASS`)

Ключового слова успадкування в калькуляторах більше немає. Колишній батьківський клас тепер **приватне поле** колишнього
нащадка, отримане через конструктор, а нащадок **делегує** йому виклики:

```python
# ДО: успадкування                                    # ПІСЛЯ: композиція + DI
class HolidayLoyaltyPriceCalculator(                  class HolidayLoyaltyPriceCalculator:
        LoyaltyPriceCalculator):                          def __init__(self, loyal, holiday, lines):
    def order_discount(self, subtotal):                       self._loyal, self._holiday = loyal, holiday
        extra = ...                                           self._lines = list(lines)
        return super().order_discount(subtotal) + extra
    def loyalty_points(self, total):                      def loyalty_points(self, total):
        return super().loyalty_points(total) * 2              return self._loyal.loyalty_points(total) * 2
```

* Правила акцій, які нащадки вливали через `super()`, винесено в окремі політики `LoyaltyDiscount` і `HolidayDiscount` з
  контрактом `DiscountPolicy` (`typing.Protocol`). Базовий рушій `PriceCalculator(lines, coupon, discounts=(...),
  whole_hryvnia=...)` просто питає кожну впроваджену політику про її знижку.
* Ланцюжок делегування: `HolidayLoyaltyPriceCalculator._loyal → LoyaltyPriceCalculator._price → PriceCalculator`.
  Збирання в одному місці: фабрики `regular_calculator`, `loyalty_calculator`, `holiday_calculator`.

| Клас | DIT | NOC | PIM | NMO |
|---|---|---|---|---|
| PriceCalculator | 1 | 0 | 13 | **0** |
| LoyaltyPriceCalculator | **1** | 0 | 7 | **0** |
| HolidayLoyaltyPriceCalculator | **1** | 0 | **6** | **0** |
| LoyaltyDiscount / HolidayDiscount (політики) | 1 | 0 | 4 / 3 | 0 |

**DIT листового класу 3 → 1, перевизначених методів 6 → 0, PIM 21 → 6.** Контракт `DiscountPolicy` має DIT 3 лише через
`typing.Protocol`; політики його не успадковують.

Той самий купон тепер працює **для всіх** калькуляторів без жодної правки в обгортках (тест
`test_coupon_now_works_on_every_calculator`: лояльність gold 11 000 − 7 % − 5 % = 9 680; свято 9 500). Бізнес-результати
Baseline збереглися: ті самі тести `tests/test_promotions.py` зелені (7 passed), увесь набір **283 passed**.
Sonar API для файлу: 6 класів, complexity 51, ncloc 110.
