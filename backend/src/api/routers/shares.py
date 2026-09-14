"""Sharing endpoints: grant access to another seeded user, list
current shares for a document, and revoke access."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...domain.entities import Permission
from ...domain.exceptions import (
    AccessDeniedError,
    DocumentNotFoundError,
    UserNotFoundError,
    ValidationError,
)
from ..deps import CurrentUserIdDep, DocumentServiceDep
from ..schemas import ShareDocumentIn, ShareOut

router = APIRouter(prefix="/documents/{document_id}/shares", tags=["shares"])


def _share_to_out(dto) -> ShareOut:
    return ShareOut(
        user_id=dto.user_id,
        user_name=dto.user_name,
        user_email=dto.user_email,
        permission=dto.permission,
    )


@router.get("", response_model=list[ShareOut])
def list_shares(
    document_id: str, service: DocumentServiceDep, user_id: CurrentUserIdDep
) -> list[ShareOut]:
    try:
        shares = service.list_shares(document_id, user_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return [_share_to_out(dto) for dto in shares]


@router.post("", response_model=ShareOut, status_code=201)
def share_document(
    document_id: str,
    body: ShareDocumentIn,
    service: DocumentServiceDep,
    user_id: CurrentUserIdDep,
) -> ShareOut:
    permission = Permission.EDIT if body.permission == "edit" else Permission.VIEW
    try:
        dto = service.share_document(document_id, user_id, body.email, permission)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _share_to_out(dto)


@router.delete("/{target_user_id}", status_code=204)
def revoke_share(
    document_id: str,
    target_user_id: str,
    service: DocumentServiceDep,
    user_id: CurrentUserIdDep,
) -> None:
    try:
        service.revoke_share(document_id, user_id, target_user_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
