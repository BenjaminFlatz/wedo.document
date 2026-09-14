"""FastAPI dependency wiring: DB session, repositories, services, current user.

Mocked identity: the frontend sends the seeded user's id in the
`X-User-Id` header (analogous in spirit to the gateway-injected
X-Internal-User-Id header pattern used for real auth providers, but
implemented directly here since there is no gateway/PropelAuth in this
assignment's scope).
"""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from ..application.document_service import DocumentService
from ..domain.exceptions import UserNotFoundError
from ..infrastructure.db_models import get_session
from ..infrastructure.repositories import DocumentRepository, UserRepository

SessionDep = Annotated[Session, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_document_repository(session: SessionDep) -> DocumentRepository:
    return DocumentRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]
DocumentRepoDep = Annotated[DocumentRepository, Depends(get_document_repository)]


def get_document_service(documents: DocumentRepoDep, users: UserRepoDep) -> DocumentService:
    return DocumentService(documents=documents, users=users)


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


def get_current_user_id(
    users: UserRepoDep,
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header. Please log in.")
    try:
        users.get(x_user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=401, detail="Unknown user identity") from exc
    return x_user_id


CurrentUserIdDep = Annotated[str, Depends(get_current_user_id)]
