"""Лаб.11: безперервний аудит актуальності бази знань за front matter (стадія CI docs.yml).

Для кожної опублікованої сторінки читає паспорт owner / status / review_date і виводить:
  * прострочені сторінки (review_date < сьогодні) — анотація ::warning:: у GitHub Actions;
  * сторінки зі status: deprecated (не видаляються, мають банер і переспрямування);
  * сторінки без паспорта — помилка DoD (код виходу 1).
Прострочення за замовчуванням не зупиняє збірку (це сигнал власнику), з --fail-on-overdue — зупиняє.

Запуск:  python tools/doc_review_dates.py [--today 2026-11-22] [--fail-on-overdue]
"""
import argparse
import glob
import sys
from datetime import date
from pathlib import Path

import yaml

PAGES = ["docs/index.md", "docs/developer/**/*.md", "docs/api/**/*.md", "docs/architecture/**/*.md", "docs/lab4/*.md",
         "docs/lab3/secrets_prevention.md", "docs/lab6/precommit.md", "docs/archive/README.md"]
STATUSES = ("draft", "in-review", "published", "deprecated")


def front_matter(path):
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    return yaml.safe_load(text.split("---\n", 2)[1]) or {}


def passport_problem(fm, status, review):
    if not fm.get("owner") or status not in STATUSES:
        return "немає паспорта owner/status"
    if status != "deprecated" and review is None:
        return "немає review_date"
    return None


def page_row(path, today):
    fm = front_matter(path)
    raw = fm.get("review_date")
    review = date.fromisoformat(str(raw)) if raw else None
    status = fm.get("status")
    return {"page": path.replace("\\", "/"), "owner": fm.get("owner", "-"), "status": status or "-",
            "review": review, "days": (review - today).days if review else None,
            "problem": passport_problem(fm, status, review)}


def audit(today):
    return [page_row(path, today) for pattern in PAGES for path in sorted(glob.glob(pattern, recursive=True))]


def is_overdue(r):
    return r["days"] is not None and r["days"] < 0 and r["status"] != "deprecated"


def print_table(rows, today):
    print(f"Аудит review_date на {today}: сторінок {len(rows)}")
    print(f"{'сторінка':<52} {'status':<11} {'review_date':<11} днів")
    for r in rows:
        days = "-" if r["days"] is None else str(r["days"])
        print(f"{r['page']:<52} {r['status']:<11} {str(r['review'] or '-'):<11} {days}")


def print_findings(rows):
    """Друкує прострочені, deprecated і сторінки без паспорта; повертає (overdue, broken)."""
    overdue = [r for r in rows if is_overdue(r)]
    deprecated = [r["page"] for r in rows if r["status"] == "deprecated"]
    broken = [r for r in rows if r["problem"]]
    print(f"\nПрострочено: {len(overdue)}")
    for r in overdue:
        print(f"::warning file={r['page']}::review_date {r['review']} прострочено на {-r['days']} дн., власник {r['owner']}")
    print(f"Deprecated: {len(deprecated)} ({', '.join(deprecated) or '-'})")
    for r in broken:
        print(f"::error file={r['page']}::{r['problem']}")
    return overdue, broken


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--today", default=date.today().isoformat())
    p.add_argument("--fail-on-overdue", action="store_true")
    args = p.parse_args(argv)
    today = date.fromisoformat(args.today)
    rows = audit(today)
    print_table(rows, today)
    overdue, broken = print_findings(rows)
    failed = bool(broken) or (args.fail_on_overdue and bool(overdue))
    print("RESULT: FAIL" if failed else "RESULT: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
