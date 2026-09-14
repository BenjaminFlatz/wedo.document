"""API-level tests for document creation, retrieval, and validation."""
from __future__ import annotations

from .conftest import ADA, ALAN, auth_headers


def test_requires_auth_header(client):
    response = client.get("/documents")
    assert response.status_code == 401


def test_rejects_unknown_user(client):
    response = client.get("/documents", headers=auth_headers("no-such-user"))
    assert response.status_code == 401


def test_create_document_returns_detail(client):
    response = client.post(
        "/documents", json={"title": "My First Doc"}, headers=auth_headers(ADA)
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "My First Doc"
    assert body["owner_id"] == ADA
    assert body["can_edit"] is True
    assert body["can_manage_shares"] is True
    assert body["content"] == {"type": "doc", "content": [{"type": "paragraph"}]}


def test_create_document_rejects_blank_title(client):
    response = client.post("/documents", json={"title": ""}, headers=auth_headers(ADA))
    assert response.status_code == 422  # pydantic min_length validation


def test_created_document_appears_in_owned_list(client):
    create_resp = client.post(
        "/documents", json={"title": "Owned Doc"}, headers=auth_headers(ADA)
    )
    doc_id = create_resp.json()["id"]

    list_resp = client.get("/documents", headers=auth_headers(ADA))
    assert list_resp.status_code == 200
    ids = [doc["id"] for doc in list_resp.json()]
    assert doc_id in ids
    owned_entry = next(doc for doc in list_resp.json() if doc["id"] == doc_id)
    assert owned_entry["relationship"] == "owned"


def test_other_user_cannot_read_private_document(client):
    create_resp = client.post(
        "/documents", json={"title": "Private Doc"}, headers=auth_headers(ADA)
    )
    doc_id = create_resp.json()["id"]

    get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(ALAN))
    assert get_resp.status_code == 403


def test_get_missing_document_returns_404(client):
    response = client.get("/documents/does-not-exist", headers=auth_headers(ADA))
    assert response.status_code == 404


def test_update_content_and_rename(client):
    create_resp = client.post(
        "/documents", json={"title": "Editable Doc"}, headers=auth_headers(ADA)
    )
    doc_id = create_resp.json()["id"]

    new_content = {
        "type": "doc",
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": "hello"}]}],
    }
    update_resp = client.put(
        f"/documents/{doc_id}/content",
        json={"content": new_content},
        headers=auth_headers(ADA),
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["content"] == new_content

    rename_resp = client.patch(
        f"/documents/{doc_id}",
        json={"title": "Renamed Doc"},
        headers=auth_headers(ADA),
    )
    assert rename_resp.status_code == 200
    assert rename_resp.json()["title"] == "Renamed Doc"


def test_delete_document(client):
    create_resp = client.post(
        "/documents", json={"title": "Doomed Doc"}, headers=auth_headers(ADA)
    )
    doc_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/documents/{doc_id}", headers=auth_headers(ADA))
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(ADA))
    assert get_resp.status_code == 404
