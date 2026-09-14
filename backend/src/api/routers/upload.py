"""File upload endpoint: accept .txt/.md files and convert them
into a brand-new editable document."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile

from ...domain.exceptions import UnsupportedFileTypeError, ValidationError
from ..deps import CurrentUserIdDep, DocumentServiceDep
from ..schemas import DocumentDetailOut

router = APIRouter(prefix="/documents", tags=["upload"])


@router.post("/import", response_model=DocumentDetailOut, status_code=201)
async def import_document(
    file: UploadFile,
    service: DocumentServiceDep,
    user_id: CurrentUserIdDep,
) -> DocumentDetailOut:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    raw_bytes = await file.read()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400, detail="File must be UTF-8 encoded text"
        ) from exc

    try:
        dto = service.create_document_from_import(user_id, file.filename, raw_text)
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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
