"""CRUD endpoints for documents: list, create, get, rename,
update content (autosave), and delete."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...domain.exceptions import (
    AccessDeniedError,
    DocumentNotFoundError,
    ValidationError,
)
from ..deps import CurrentUserIdDep, DocumentServiceDep
from ..schemas import (
    CreateDocumentIn,
    DocumentDetailOut,
    DocumentSummaryOut,
    RenameDocumentIn,
    UpdateContentIn,
)

router = APIRouter(prefix="/documents", tags=["documents"])


def _summary_to_out(dto) -> DocumentSummaryOut:
    return DocumentSummaryOut(
        id=dto.id,
        title=dto.title,
        owner_id=dto.owner_id,
        owner_name=dto.owner_name,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        relationship=dto.relationship,
        permission=dto.permission,
    )


def _detail_to_out(dto) -> DocumentDetailOut:
    return DocumentDetailOut(
        id=dto.id,
        title=dto.title,
        content=dto.content,
        owner_id=dto.owner_id,
        owner_name=dto.owner_name,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        can_edit=dto.can_edit,
        can_manage_shares=dto.can_manage_shares,
    )


@router.get("", response_model=list[DocumentSummaryOut])
def list_my_documents(
    service: DocumentServiceDep, user_id: CurrentUserIdDep
) -> list[DocumentSummaryOut]:
    return [_summary_to_out(dto) for dto in service.list_my_documents(user_id)]


@router.post("", response_model=DocumentDetailOut, status_code=201)
def create_document(
    body: CreateDocumentIn,
    service: DocumentServiceDep,
    user_id: CurrentUserIdDep,
) -> DocumentDetailOut:
    try:
        dto = service.create_document(user_id, body.title)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _detail_to_out(dto)


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(
    document_id: str, service: DocumentServiceDep, user_id: CurrentUserIdDep
) -> DocumentDetailOut:
    try:
        dto = service.get_document(document_id, user_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return _detail_to_out(dto)


@router.patch("/{document_id}", response_model=DocumentDetailOut)
def rename_document(
    document_id: str,
    body: RenameDocumentIn,
    service: DocumentServiceDep,
    user_id: CurrentUserIdDep,
) -> DocumentDetailOut:
    try:
        dto = service.rename_document(document_id, user_id, body.title)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _detail_to_out(dto)


@router.put("/{document_id}/content", response_model=DocumentDetailOut)
def update_content(
    document_id: str,
    body: UpdateContentIn,
    service: DocumentServiceDep,
    user_id: CurrentUserIdDep,
) -> DocumentDetailOut:
    try:
        dto = service.update_content(document_id, user_id, body.content)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return _detail_to_out(dto)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: str, service: DocumentServiceDep, user_id: CurrentUserIdDep
) -> None:
    try:
        service.delete_document(document_id, user_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
