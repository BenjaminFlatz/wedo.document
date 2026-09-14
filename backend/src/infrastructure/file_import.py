"""Converts uploaded .txt / .md files into TipTap-compatible ProseMirror JSON.

Kept intentionally simple: a lightweight Markdown-ish parser that recognizes
headings (#, ##, ###), bullet lists (-, *), numbered lists (1.), and plain
paragraphs. Good enough to demonstrate a real, product-relevant import flow
without pulling in a heavy Markdown AST dependency.
"""
from __future__ import annotations

import re

from ..domain.exceptions import UnsupportedFileTypeError

SUPPORTED_EXTENSIONS = {".txt", ".md"}

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
_BULLET_RE = re.compile(r"^[-*]\s+(.*)$")
_NUMBERED_RE = re.compile(r"^\d+\.\s+(.*)$")


def _text_node(text: str) -> dict:
    return {"type": "text", "text": text}


def _paragraph(text: str) -> dict:
    if not text.strip():
        return {"type": "paragraph"}
    return {"type": "paragraph", "content": [_text_node(text)]}


def _heading(level: int, text: str) -> dict:
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [_text_node(text)] if text.strip() else [],
    }


def _list_item(text: str) -> dict:
    return {"type": "listItem", "content": [_paragraph(text)]}


def parse_filename_extension(filename: str) -> str:
    idx = filename.rfind(".")
    return filename[idx:].lower() if idx != -1 else ""


def convert_text_to_document_json(raw_text: str, filename: str) -> dict:
    """Parses raw text content into a ProseMirror `doc` JSON structure.

    Raises UnsupportedFileTypeError if the filename extension is not
    among SUPPORTED_EXTENSIONS (checked by the caller before invoking this,
    but re-validated here as a guard clause).
    """
    ext = parse_filename_extension(filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(filename)

    lines = raw_text.splitlines()
    content: list[dict] = []

    pending_bullets: list[str] = []
    pending_numbered: list[str] = []

    def flush_bullets() -> None:
        nonlocal pending_bullets
        if pending_bullets:
            content.append(
                {"type": "bulletList", "content": [_list_item(t) for t in pending_bullets]}
            )
            pending_bullets = []

    def flush_numbered() -> None:
        nonlocal pending_numbered
        if pending_numbered:
            content.append(
                {"type": "orderedList", "content": [_list_item(t) for t in pending_numbered]}
            )
            pending_numbered = []

    for line in lines:
        heading_match = _HEADING_RE.match(line)
        bullet_match = _BULLET_RE.match(line)
        numbered_match = _NUMBERED_RE.match(line)

        if heading_match:
            flush_bullets()
            flush_numbered()
            level = len(heading_match.group(1))
            content.append(_heading(level, heading_match.group(2)))
        elif bullet_match:
            flush_numbered()
            pending_bullets.append(bullet_match.group(1))
        elif numbered_match:
            flush_bullets()
            pending_numbered.append(numbered_match.group(1))
        elif line.strip() == "":
            flush_bullets()
            flush_numbered()
        else:
            flush_bullets()
            flush_numbered()
            content.append(_paragraph(line))

    flush_bullets()
    flush_numbered()

    if not content:
        content = [{"type": "paragraph"}]

    return {"type": "doc", "content": content}


def derive_title_from_filename(filename: str) -> str:
    ext = parse_filename_extension(filename)
    base = filename[: -len(ext)] if ext else filename
    return base.replace("_", " ").replace("-", " ").strip() or "Untitled Document"
