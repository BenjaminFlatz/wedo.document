"""Concrete repository implementations backed by SQLModel/SQLite.

Translates between ORM rows (db_models.py) and domain dataclasses
(domain/entities.py) so the application layer never touches SQLModel
directly.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from ..domain.entities import Document, DocumentShare, Permission, User
from ..domain.exceptions import DocumentNotFoundError, UserNotFoundError
from .db_models import DocumentRow, DocumentShareRow, UserRow


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _row_to_share(row: DocumentShareRow) -> DocumentShare:
    return DocumentShare(
        document_id=row.document_id,
        user_id=row.user_id,
        permission=Permission(row.permission),
    )


def _row_to_document(row: DocumentRow) -> Document:
    return Document(
        id=row.id,
        title=row.title,
        content=row.content(),
        owner_id=row.owner_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        shares=[_row_to_share(s) for s in row.shares],
    )


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: str) -> User:
        row = self._session.get(UserRow, user_id)
        if row is None:
            raise UserNotFoundError(user_id)
        return User(id=row.id, name=row.name, email=row.email)

    def get_by_email(self, email: str) -> User | None:
        row = self._session.exec(select(UserRow).where(UserRow.email == email)).first()
        return User(id=row.id, name=row.name, email=row.email) if row else None

    def list_all(self) -> list[User]:
        rows = self._session.exec(select(UserRow)).all()
        return [User(id=r.id, name=r.name, email=r.email) for r in rows]

    def exists(self, user_id: str) -> bool:
        return self._session.get(UserRow, user_id) is not None


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, document_id: str) -> Document:
        row = self._session.get(DocumentRow, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        return _row_to_document(row)

    def create(self, document: Document) -> Document:
        row = DocumentRow(
            id=document.id,
            title=document.title,
            owner_id=document.owner_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        row.set_content(document.content)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return _row_to_document(row)

    def update(self, document_id: str, *, title: str | None = None, content: dict | None = None) -> Document:
        row = self._session.get(DocumentRow, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        if title is not None:
            row.title = title
        if content is not None:
            row.set_content(content)
        row.updated_at = _utcnow()
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return _row_to_document(row)

    def delete(self, document_id: str) -> None:
        row = self._session.get(DocumentRow, document_id)
        if row is None:
            raise DocumentNotFoundError(document_id)
        self._session.delete(row)
        self._session.commit()

    def list_owned(self, owner_id: str) -> list[Document]:
        rows = self._session.exec(
            select(DocumentRow).where(DocumentRow.owner_id == owner_id)
        ).all()
        return [_row_to_document(r) for r in rows]

    def list_shared_with(self, user_id: str) -> list[Document]:
        rows = self._session.exec(
            select(DocumentRow)
            .join(DocumentShareRow, DocumentShareRow.document_id == DocumentRow.id)
            .where(DocumentShareRow.user_id == user_id)
        ).all()
        return [_row_to_document(r) for r in rows]

    def add_share(self, document_id: str, user_id: str, permission: Permission) -> DocumentShare:
        existing = self._session.exec(
            select(DocumentShareRow).where(
                DocumentShareRow.document_id == document_id,
                DocumentShareRow.user_id == user_id,
            )
        ).first()
        if existing:
            existing.permission = permission.value
            self._session.add(existing)
            self._session.commit()
            self._session.refresh(existing)
            return _row_to_share(existing)

        row = DocumentShareRow(document_id=document_id, user_id=user_id, permission=permission.value)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return _row_to_share(row)

    def remove_share(self, document_id: str, user_id: str) -> None:
        row = self._session.exec(
            select(DocumentShareRow).where(
                DocumentShareRow.document_id == document_id,
                DocumentShareRow.user_id == user_id,
            )
        ).first()
        if row:
            self._session.delete(row)
            self._session.commit()

    def list_shares(self, document_id: str) -> list[DocumentShare]:
        rows = self._session.exec(
            select(DocumentShareRow).where(DocumentShareRow.document_id == document_id)
        ).all()
        return [_row_to_share(r) for r in rows]
