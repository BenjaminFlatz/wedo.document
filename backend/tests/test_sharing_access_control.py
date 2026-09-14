"""API-level tests for the sharing model and access-control enforcement:
owner grants access, a shared view-only user can read but not edit, and
a shared edit user can both read and edit."""
from __future__ import annotations

from .conftest import ADA, ALAN, GRACE, auth_headers


def _create_document(client, owner: str, title: str) -> str:
    response = client.post("/documents", json={"title": title}, headers=auth_headers(owner))
    assert response.status_code == 201
    return response.json()["id"]


def test_owner_can_share_document_with_another_user(client):
    doc_id = _create_document(client, ADA, "Shared Doc")

    share_resp = client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "alan@example.com", "permission": "view"},
        headers=auth_headers(ADA),
    )
    assert share_resp.status_code == 201
    body = share_resp.json()
    assert body["user_id"] == ALAN
    assert body["permission"] == "view"


def test_non_owner_cannot_share_document(client):
    doc_id = _create_document(client, ADA, "Not Yours To Share")

    share_resp = client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "grace@example.com", "permission": "view"},
        headers=auth_headers(ALAN),
    )
    assert share_resp.status_code == 403


def test_view_only_share_can_read_but_not_edit(client):
    doc_id = _create_document(client, ADA, "View Only Doc")
    client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "alan@example.com", "permission": "view"},
        headers=auth_headers(ADA),
    )

    get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(ALAN))
    assert get_resp.status_code == 200
    assert get_resp.json()["can_edit"] is False

    update_resp = client.put(
        f"/documents/{doc_id}/content",
        json={"content": {"type": "doc", "content": []}},
        headers=auth_headers(ALAN),
    )
    assert update_resp.status_code == 403


def test_edit_share_can_read_and_edit(client):
    doc_id = _create_document(client, ADA, "Edit Share Doc")
    client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "grace@example.com", "permission": "edit"},
        headers=auth_headers(ADA),
    )

    get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(GRACE))
    assert get_resp.status_code == 200
    assert get_resp.json()["can_edit"] is True

    new_content = {"type": "doc", "content": [{"type": "paragraph"}]}
    update_resp = client.put(
        f"/documents/{doc_id}/content",
        json={"content": new_content},
        headers=auth_headers(GRACE),
    )
    assert update_resp.status_code == 200


def test_shared_document_appears_in_recipient_shared_list(client):
    doc_id = _create_document(client, ADA, "Appears In List")
    client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "alan@example.com", "permission": "view"},
        headers=auth_headers(ADA),
    )

    list_resp = client.get("/documents", headers=auth_headers(ALAN))
    assert list_resp.status_code == 200
    shared_entry = next((doc for doc in list_resp.json() if doc["id"] == doc_id), None)
    assert shared_entry is not None
    assert shared_entry["relationship"] == "shared"
    assert shared_entry["permission"] == "view"


def test_revoke_share_removes_access(client):
    doc_id = _create_document(client, ADA, "Revocable Doc")
    client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "alan@example.com", "permission": "view"},
        headers=auth_headers(ADA),
    )

    revoke_resp = client.delete(
        f"/documents/{doc_id}/shares/{ALAN}", headers=auth_headers(ADA)
    )
    assert revoke_resp.status_code == 204

    get_resp = client.get(f"/documents/{doc_id}", headers=auth_headers(ALAN))
    assert get_resp.status_code == 403


def test_sharing_with_unknown_email_returns_400(client):
    doc_id = _create_document(client, ADA, "Bad Share Target")

    share_resp = client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "nobody@example.com", "permission": "view"},
        headers=auth_headers(ADA),
    )
    # Unknown recipient email is a validation problem (bad input), not a
    # "document not found" — the DocumentService raises ValidationError.
    assert share_resp.status_code == 400


def test_sharing_with_own_email_is_rejected(client):
    doc_id = _create_document(client, ADA, "Cannot Share With Self")

    share_resp = client.post(
        f"/documents/{doc_id}/shares",
        json={"email": "ada@example.com", "permission": "view"},
        headers=auth_headers(ADA),
    )
    assert share_resp.status_code == 400
