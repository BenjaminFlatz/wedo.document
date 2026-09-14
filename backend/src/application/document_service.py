"""Application layer: document use cases.

Orchestrates domain rules and repositories. Depends only on repository
interfaces (concrete SQLModel repos are injected by the API layer's
dependency wiring) and the domain layer's pure access-control predicates.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..domain.entities import Document, Permission, can_edit_document, can_manage_shares, can_read_document
from ..domain.exceptions import AccessDeniedError, ValidationError
from ..infrastructure.file_import import convert_text_to_document_json, derive_title_from_filename
from ..infrastructure.repositories import DocumentRepository, UserRepository
from .dtos import DocumentDetailDTO, DocumentSummaryDTO, ShareDTO

EMPTY_DOCUMENT_CONTENT = {"type": "doc", "content": [{"type": "paragraph"}]}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocumentService:
    def __init__(self, documents: DocumentRepository, users: UserRepository) -> None:
        self._documents = documents
        self._users = users

    # ---- Queries -----------------------------------------------------

    def list_my_documents(self, requester_id: str) -> list[DocumentSummaryDTO]:
        owned = self._documents.list_owned(requester_id)
        shared = self._documents.list_shared_with(requester_id)

        summaries: list[DocumentSummaryDTO] = []
        for doc in owned:
            owner = self._users.get(doc.owner_id)
            summaries.append(
                DocumentSummaryDTO(
                    id=doc.id,
                    title=doc.title,
                    owner_id=doc.owner_id,
                    owner_name=owner.name,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                    relationship="owned",
                    permission="owner",
                )
            )
        for doc in shared:
            owner = self._users.get(doc.owner_id)
            my_share = next((s for s in doc.shares if s.user_id == requester_id), None)
            permission = my_share.permission.value if my_share else Permission.VIEW.value
            summaries.append(
                DocumentSummaryDTO(
                    id=doc.id,
                    title=doc.title,
                    owner_id=doc.owner_id,
                    owner_name=owner.name,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at,
                    relationship="shared",
                    permission=permission,
                )
            )
        summaries.sort(key=lambda s: s.updated_at, reverse=True)
        return summaries

    def get_document(self, document_id: str, requester_id: str) -> DocumentDetailDTO:
        doc = self._documents.get(document_id)
        if not can_read_document(doc, requester_id):
            raise AccessDeniedError("You do not have access to this document")
        owner = self._users.get(doc.owner_id)
        return DocumentDetailDTO(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            owner_id=doc.owner_id,
            owner_name=owner.name,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            can_edit=can_edit_document(doc, requester_id),
            can_manage_shares=can_manage_shares(doc, requester_id),
        )

    def list_shares(self, document_id: str, requester_id: str) -> list[ShareDTO]:
        doc = self._documents.get(document_id)
        if not can_manage_shares(doc, requester_id):
            raise AccessDeniedError("Only the owner can view sharing settings")
        shares = self._documents.list_shares(document_id)
        result = []
        for share in shares:
            user = self._users.get(share.user_id)
            result.append(
                ShareDTO(
                    user_id=user.id,
                    user_name=user.name,
                    user_email=user.email,
                    permission=share.permission,
                )
            )
        return result

    # ---- Commands ------------------------------------------------------

    def create_document(self, requester_id: str, title: str) -> DocumentDetailDTO:
        title = title.strip()
        if not title:
            raise ValidationError("Document title cannot be empty")

        now = _utcnow()
        doc = Document(
            id=str(uuid.uuid4()),
            title=title,
            content=EMPTY_DOCUMENT_CONTENT,
            owner_id=requester_id,
            created_at=now,
            updated_at=now,
        )
        created = self._documents.create(doc)
        return self.get_document(created.id, requester_id)

    def create_document_from_import(self, requester_id: str, filename: str, raw_text: str) -> DocumentDetailDTO:
        content = convert_text_to_document_json(raw_text, filename)
        title = derive_title_from_filename(filename)

        now = _utcnow()
        doc = Document(
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            owner_id=requester_id,
            created_at=now,
            updated_at=now,
        )
        created = self._documents.create(doc)
        return self.get_document(created.id, requester_id)

    def rename_document(self, document_id: str, requester_id: str, new_title: str) -> DocumentDetailDTO:
        new_title = new_title.strip()
        if not new_title:
            raise ValidationError("Document title cannot be empty")

        doc = self._documents.get(document_id)
        if not can_edit_document(doc, requester_id):
            raise AccessDeniedError("You do not have permission to rename this document")

        self._documents.update(document_id, title=new_title)
        return self.get_document(document_id, requester_id)

    def update_content(self, document_id: str, requester_id: str, content: dict) -> DocumentDetailDTO:
        doc = self._documents.get(document_id)
        if not can_edit_document(doc, requester_id):
            raise AccessDeniedError("You do not have permission to edit this document")

        self._documents.update(document_id, content=content)
        return self.get_document(document_id, requester_id)

    def delete_document(self, document_id: str, requester_id: str) -> None:
        doc = self._documents.get(document_id)
        if doc.owner_id != requester_id:
            raise AccessDeniedError("Only the owner can delete this document")
        self._documents.delete(document_id)

    def share_document(
        self, document_id: str, requester_id: str, target_email: str, permission: Permission
    ) -> ShareDTO:
        doc = self._documents.get(document_id)
        if not can_manage_shares(doc, requester_id):
            raise AccessDeniedError("Only the owner can share this document")

        target_user = self._users.get_by_email(target_email.strip().lower())
        if target_user is None:
            raise ValidationError(f"No user found with email '{target_email}'")
        if target_user.id == doc.owner_id:
            raise ValidationError("Cannot share a document with its own owner")

        self._documents.add_share(document_id, target_user.id, permission)
        return ShareDTO(
            user_id=target_user.id,
            user_name=target_user.name,
            user_email=target_user.email,
            permission=permission,
        )

    def revoke_share(self, document_id: str, requester_id: str, target_user_id: str) -> None:
        doc = self._documents.get(document_id)
        if not can_manage_shares(doc, requester_id):
            raise AccessDeniedError("Only the owner can modify sharing settings")
        self._documents.remove_share(document_id, target_user_id)
