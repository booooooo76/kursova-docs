"""Хук MkDocs (Лаб.11): [[wikilinks]] Obsidian -> звичайні посилання сайту.

[[sdd]] або [[sdd|SDD]] шукає сторінку з таким ім'ям файлу; якщо збігів кілька (index.md), перевага тій, що в тій
самій теці. Невідомий wikilink -> попередження, яке в `mkdocs build --strict` зупиняє збірку (мертве посилання).
"""
import logging
import posixpath
import re

log = logging.getLogger("mkdocs.hooks.wikilinks")
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:\|([^\]]+))?\]\]")
_index = {}


def on_files(files, config):
    _index.clear()
    for f in files.documentation_pages():
        stem = posixpath.splitext(posixpath.basename(f.src_uri))[0]
        _index.setdefault(stem.lower(), []).append(f.src_uri)
    return files


def _resolve(name, page_uri):
    name = name.strip()
    if "/" in name:  # [[adr/index]]: шлях без розширення, як в Obsidian
        suffix = name.lower() + ".md"
        return next((u for uris in _index.values() for u in uris if u.lower().endswith(suffix)), None)
    candidates = _index.get(name.lower(), [])
    if len(candidates) > 1:
        here = posixpath.dirname(page_uri)
        candidates = [c for c in candidates if posixpath.dirname(c) == here] or candidates
    return candidates[0] if candidates else None


def on_page_markdown(markdown, page, config, files):
    def replace(m):
        target = _resolve(m.group(1), page.file.src_uri)
        label = m.group(2) or m.group(1)
        if target is None:
            log.warning("Doc file '%s' contains an unknown wikilink [[%s]]", page.file.src_uri, m.group(1))
            return label
        rel = posixpath.relpath(target, posixpath.dirname(page.file.src_uri) or ".")
        return f"[{label}]({rel})"
    # блоки коду (```...```) не чіпаємо: у Mermaid [[текст]] означає вузол-підпрограму, а не посилання
    parts = FENCE.split(markdown)
    return "".join(p if p.startswith("```") else WIKILINK.sub(replace, p) for p in parts)


FENCE = re.compile(r"(```.*?```)", re.S)
