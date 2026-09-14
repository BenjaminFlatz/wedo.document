"""Tests for the .txt/.md file upload -> document conversion flow."""
from __future__ import annotations

from .conftest import ADA, auth_headers


def test_import_markdown_file_creates_document(client):
    file_content = b"# Hello\nThis is a test file.\n"
    response = client.post(
        "/documents/import",
        files={"file": ("notes.md", file_content, "text/markdown")},
        headers=auth_headers(ADA),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "notes"
    nodes = body["content"]["content"]
    assert nodes[0]["type"] == "heading"
    assert nodes[0]["attrs"]["level"] == 1
    assert nodes[1]["type"] == "paragraph"


def test_import_plain_text_file_creates_document(client):
    file_content = b"Just a plain line of text.\n"
    response = client.post(
        "/documents/import",
        files={"file": ("plain.txt", file_content, "text/plain")},
        headers=auth_headers(ADA),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "plain"
    assert body["content"]["type"] == "doc"


def test_import_rejects_unsupported_extension(client):
    response = client.post(
        "/documents/import",
        files={"file": ("evil.exe", b"not text", "application/octet-stream")},
        headers=auth_headers(ADA),
    )
    assert response.status_code == 400


def test_import_rejects_non_utf8_bytes(client):
    response = client.post(
        "/documents/import",
        files={"file": ("bad.txt", b"\xff\xfe\x00\x00", "text/plain")},
        headers=auth_headers(ADA),
    )
    assert response.status_code == 400
