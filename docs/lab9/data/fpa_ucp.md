# FPA / UCP — Staff Review (bcgov/lear)

## FPA (IFPUG)

| ID | Тип | Функція | DET | RET/FTR | Складність | FP |
|---|---|---|---:|---:|---|---:|
| D1 | ILF | Рецензія з історією рішень (reviews + review_results) | 13 | 2 | Простий | 7 |
| D2 | EIF | Заява (filings) модуля Filing | 7 | 1 | Простий | 5 |
| D3 | EIF | Користувач-рецензент (users) | 3 | 1 | Простий | 5 |
| D4 | EIF | Name Request сервісу NameX | 2 | 1 | Простий | 5 |
| T1 | EI | Подати заяву continuation-in на рецензію | 7 | 2 | Середній | 4 |
| T2 | EI | Повторно подати після CHANGE_REQUESTED | 7 | 2 | Середній | 4 |
| T3 | EI | Зберегти рішення рецензента | 5 | 3 | Складний | 6 |
| T4 | EO | Черга рецензій із фільтрами, сортуванням і строком дії NR | 21 | 3 | Складний | 7 |
| T5 | EO | Картка рецензії з обчисленим filingLink | 13 | 3 | Середній | 5 |
| T6 | EQ | Останній коментар рецензента в заяві | 3 | 2 | Простий | 3 |

**UFP = 51 FP** (VAF = 1,0)

## UCP (Карнер)

| Актор | Інтерфейс | Вага |
|---|---|---:|
| Staff-рецензент BC Registries | людина через GUI (staff UI) | 3 |
| Заявник (бізнес-клієнт) | людина через GUI (Business Registry UI) | 3 |
| NameX API | REST по HTTP | 2 |
| Business Emailer | API черги GCP Pub/Sub (publish_to_queue) | 1 |

| UC | Прецедент | Актор | Транзакцій | Вага |
|---|---|---|---:|---:|
| UC1 | Подати заяву на рецензію | Заявник | 6 | 10 |
| UC2 | Повторно подати після запиту змін | Заявник | 7 | 10 |
| UC3 | Переглянути чергу рецензій | Staff-рецензент | 8 | 15 |
| UC4 | Відкрити картку рецензії | Staff-рецензент | 5 | 10 |
| UC5 | Ухвалити рішення (схвалити / запросити зміни / відхилити) | Staff-рецензент | 10 | 15 |
| UC6 | Побачити коментар рецензента | Заявник | 3 | 5 |

UAW = 9, UUCW = 65, UUCP = 74, TCF = 1.0, ECF = 1.0
**UCP = 74**

## Калібрування
Трудовитрати з Git: 92.9 людино-год
**PF = 92.9 / 74 = 1.26 людино-год / UCP** (1.82 год / FP)

## Джерела DET / RET / FTR

- **D1** `models/review.py :: Review; models/review_result.py :: ReviewResult`: DET = id, nr_number, identifier, contact_email, status, submission_date, creation_date, filing_id, result.status, result.comments, result.reviewer_id, result.creation_date, result.submission_date; RET/FTR = Review, ReviewResult
- **D2** `Filing.find_by_id, set_review_decision, submit_filing_to_awaiting_review`: DET = id, temp_reg, filing_type, status, nameRequest.nrNumber, foreignJurisdiction.identifier, contactPoint.email; RET/FTR = Filing
- **D3** `User.get_or_create_user_by_jwt, reviewer.display_name`: DET = id, username, display_name; RET/FTR = User
- **D4** `namex.query_nr_numbers -> POST {NAMEX_SVC_URL}/requests/search`: DET = nrNum, expirationDate; RET/FTR = NameRequest
- **T1** `POST /api/v2/businesses/<id>/filings -> submit_filing_for_review (DRAFT)`: DET = identifier, filing_id, filing_type, nrNumber, foreignJurisdiction.identifier, contactPoint.email, isPaymentActionRequired; RET/FTR = Review, Filing
- **T2** `POST /api/v2/businesses/<id>/filings/<fid> -> submit_filing_for_review (CHANGE_REQUESTED)`: DET = identifier, filing_id, nrNumber, foreignJurisdiction.identifier, contactPoint.email, result.submission_date, isPaymentActionRequired; RET/FTR = Review, Filing
- **T3** `POST /api/v2/admin/reviews/<review_id> -> save_review`: DET = review_id, status, comment, reviewer_id, message; RET/FTR = Review, Filing, User
- **T4** `GET /api/v2/admin/reviews -> get_reviews, Review.get_paginated_reviews`: DET = startDate, endDate, sortBy, sortDesc, id, nrNumber, identifier, contactEmail, status, submissionDate, creationDate, filingId, results.status, results.comments, results.reviewer, results.submissionDate, results.creationDate, nrExpiryDate, page, limit, total; RET/FTR = Review, User, NameRequest
- **T5** `GET /api/v2/admin/reviews/<review_id> -> get_review`: DET = id, nrNumber, identifier, contactEmail, status, submissionDate, creationDate, filingId, results.status, results.comments, results.reviewer, results.creationDate, filingLink; RET/FTR = Review, Filing, User
- **T6** `GET /api/v2/businesses/<id>/filings/<fid> -> header.latestReviewComment`: DET = identifier, filing_id, latestReviewComment; RET/FTR = Review, Filing

## Транзакції прецедентів

- **UC1** `submit_filing_for_review (DRAFT)`: 1) перевірити staffApprovalRequired і статус DRAFT; 2) створити Review(AWAITING_REVIEW); 3) скопіювати nrNumber, identifier, contactEmail із заяви; 4) зберегти Review; 5) перевести Filing в AWAITING_REVIEW; 6) надіслати подію листа в Emailer
- **UC2** `submit_filing_for_review (CHANGE_REQUESTED)`: 1) перевірити статус CHANGE_REQUESTED; 2) знайти Review за filing_id; 3) встановити RESUBMITTED; 4) оновити submission_date останнього ReviewResult; 5) оновити поля й зберегти Review; 6) перевести Filing в AWAITING_REVIEW; 7) надіслати подію листа в Emailer
- **UC3** `get_reviews`: 1) перевірити роль staff; 2) зібрати ReviewFilter із 10 параметрів; 3) зіставити колонку сортування; 4) відфільтрувати, відсортувати, розбити на сторінки; 5) вибрати NR в активних статусах; 6) запитати строки дії NR у NameX; 7) додати nrExpiryDate до рецензій; 8) повернути сторінку JSON
- **UC4** `get_review`: 1) перевірити роль staff; 2) знайти Review або 404; 3) завантажити Filing; 4) побудувати filingLink; 5) повернути JSON з історією рішень
- **UC5** `save_review`: 1) перевірити роль staff; 2) отримати або створити User з JWT; 3) знайти Review або 404; 4) перевірити, що статус ще можна змінити; 5) перевірити новий статус; 6) вимагати коментар для CR і REJECTED; 7) створити ReviewResult; 8) оновити статус Review і зберегти; 9) встановити рішення у Filing; 10) надіслати подію листа в Emailer
- **UC6** `get_single_filing`: 1) перевірити статус заяви CR / APPROVED / REJECTED; 2) взяти останній ReviewResult; 3) додати latestReviewComment у відповідь
