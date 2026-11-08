# Лаб.8, Завдання 1. ООП-паспорт системного дизайну через SonarQube REST Web API

## 1. Зріз і запити

* SonarQube Community **9.9.8 LTS** у Docker (`sonarqube-server/docker-compose.yml`, порт 9000), проєкт `kursova-pcshop`.
* Свіжий зріз: `.\scan.ps1` (офіційний образ `sonarsource/sonar-scanner-cli`, конфіг `sonar-project.properties`).
* Запити: `.\scripts\lab8_sonar_api.ps1` виконує `curl -u $SONAR_TOKEN: <url>` до `api/measures/component` і зберігає
  **сирий JSON** у `docs/lab8/data/<тег>/`. Токен береться зі змінної середовища або файлу поза репозиторієм.

Запит методички для трьох файлів Лаб.6 (Core Domain `privacy/consent.py`, Infrastructure `models/database.py`,
Utility/DTO `privacy/policy.py`):

```
curl -u $SONAR_TOKEN: "http://localhost:9000/api/measures/component?component=kursova-pcshop%3Aprivacy%2Fconsent.py&metricKeys=class_complexity,coupling_between_objects,lcom4"
{"errors":[{"msg":"The following metric keys are not found: coupling_between_objects, lcom4"}]}

curl -u $SONAR_TOKEN: "http://localhost:9000/api/measures/component?component=kursova-pcshop%3Aprivacy%2Fconsent.py&metricKeys=class_complexity"
{"component":{"key":"kursova-pcshop:privacy/consent.py", ..., "language":"py","measures":[]}}

curl -u $SONAR_TOKEN: "http://localhost:9000/api/measures/component?component=kursova-pcshop&metricKeys=method_hiding_factor,attribute_hiding_factor,coupling_factor"
{"errors":[{"msg":"The following metric keys are not found: method_hiding_factor, attribute_hiding_factor, coupling_factor"}]}
```

**Висновок з JSON:** SonarQube Community для Python не має метрик CBO, LCOM і MOOD (ключів немає в `api/metrics/search`),
а `class_complexity` є лише як прихована (`"hidden":true`) і для Python повертає порожній `measures`. Тому з сервера
береться те, що він рахує (`complexity`, `cognitive_complexity`, `classes`, `functions`, `ncloc`), а CK і MOOD
рахуються `tools/oo_metrics.py` з синтаксичного дерева за класичними визначеннями (формули в docstring інструмента).

```
curl -u $SONAR_TOKEN: "http://localhost:9000/api/measures/component?component=kursova-pcshop%3Aprivacy%2Fconsent.py&metricKeys=complexity,cognitive_complexity,classes,functions,ncloc,code_smells,sqale_rating"
{"component":{"key":"kursova-pcshop:privacy/consent.py",...,"measures":[{"metric":"cognitive_complexity","value":"23"},
 ...,{"metric":"functions","value":"17"},{"metric":"classes","value":"4"},{"metric":"complexity","value":"41"},{"metric":"ncloc","value":"195"}]}}
```

## 2. Зведена таблиця CK для трьох шарів

| Шар | Файл | Sonar: complexity / cognitive / functions / classes / ncloc | Класи | WMC | CBO | RFC | LCOM* | DIT |
|---|---|---|---|---|---|---|---|---|
| Core Domain | `privacy/consent.py` | 41 / 23 / 17 / 4 / 195 | `Decision`, `ConsentChange`, `GateFacts`, `ConsentValidationError` | 3 / 0 / 0 / 1 | 1 / 2 / 2 / 0 | 3 / 1 / 1 / 2 | 1,00 / 0 / 0 / 0 | 1 / 1 / 1 / 3 |
| Infrastructure | `models/database.py` | 18 / 22 / 7 / 1 / 78 | `DependencyUnavailableError` | 0 | 0 | 0 | 0 | 3 |
| Utility / DTO | `privacy/policy.py` | 5 / 2 / 3 / 1 / 279 | `EntityPolicy` | 1 | 2 | 3 | 0 | 1 |

Модульний розріз (процедурний код, де живе основна логіка):

| Модуль | Функцій | Класів | Fan-out (різні зовнішні сутності) | Fan-in (модулів проєкту, що від нього залежать) |
|---|---|---|---|---|
| `app` | **47** | 1 | **106** | 0 |
| `routers.operator` | 32 | 1 | 26 | 1 |
| `privacy.consent_api` | 10 | 0 | 24 | 1 |
| `privacy.consent` (Core) | 14 | 4 | 10 | 3 |
| `models.database` (Infra) | 7 | 1 | 12 | **11** |
| `privacy.policy` (DTO) | 2 | 1 | 2 | 3 |

## 3. MOOD (увесь код застосунку)

| Коефіцієнт | Значення | Як рахується |
|---|---|---|
| MHF (Method Hiding Factor) | **0,0 %** | приховані методи (`_name`) / усі методи класів (16) |
| AHF (Attribute Hiding Factor) | **2,4 %** | приховані атрибути / усі атрибути (41) |
| COF (Coupling Factor) | **0,26 %** | зв'язки між класами (1) / (TC² − TC), TC = 20 класів |

Глобально з Sonar: 664 функції, 29 класів (разом зі скриптами й тестами), complexity 1 978, ncloc 20 473.

## 4. Первинний архітектурний вердикт

1. **ООП-дизайн незрілий і анемічний.** На 664 функції лише 29 класів; у коді застосунку 20 класів, і майже всі вони
   або dataclass-контейнери даних (WMC 0–3), або винятки. Класи-мутанти у класичному сенсі відсутні: максимальний CBO 6
   (`JsonFormatter`, `PIISanitizingFilter`), далеко до порогу 15.
2. **Інкапсуляції фактично немає:** MHF 0 % і AHF 2,4 % означають, що всі методи й поля публічні. COF 0,26 % показує,
   що класи майже не взаємодіють: логіка живе не в об'єктах, а в процедурах модулів.
3. **Ознаки спагеті-коду на рівні модулів.** `app.py` це «God Module»: 47 функцій, fan-out 106, залежить від 7 модулів
   проєкту (він же Hotspot №1 у Лаб.7: CC 13 і 8 комітів за 90 днів). Логіка оформлення замовлення (кошик із сесії й БД,
   підсумок, доставка, запис замовлення, залишки) розпорошена по його функціях і напряму звертається до БД.
4. **Шари Лаб.6 здорові:** `consent.py` згуртований (лише `Decision` має LCOM* 1,0, бо це dataclass з двома незалежними
   властивостями), `database.py` має найбільший fan-in (11), як і належить інфраструктурі, `policy.py` це чистий DTO.

Наслідок для Завдання 2: класу з CBO > 15 у проєкті немає, тому застосовано шлях методички «метод штучної агрегації»:
розпорошену логіку замовлень з `app.py` зібрано в монолітний клас (God Object), який потім декомпозовано через інтерфейси.

## 5. Відтворення

```powershell
$env:SONAR_TOKEN = (Get-Content "$env:USERPROFILE\.sonar_token_lab8" -Raw).Trim()
.\scan.ps1
.\scripts\lab8_sonar_api.ps1
.\venv\Scripts\python.exe tools\oo_metrics.py app.py config.py models routers privacy --mood --modules --json docs\lab8\data\baseline\oo_metrics.json
```
