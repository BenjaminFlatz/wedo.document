"""Domain entities and pure business rules.

This module has zero external framework dependencies (no FastAPI, no
SQLModel, no DB). It represents the core concepts of the document editor:
users, documents, and sharing, plus the access-control predicate that
decides who may read/write a document.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Permission(str, Enum):
    """Access level granted to a non-owner user on a document."""

    VIEW = "view"
    EDIT = "edit"


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str


@dataclass
class DocumentShare:
    document_id: str
    user_id: str
    permission: Permission = Permission.EDIT


@dataclass
class Document:
    id: str
    title: str
    content: dict
    owner_id: str
    created_at: datetime
    updated_at: datetime
    shares: list[DocumentShare] = field(default_factory=list)


def can_read_document(document: Document, requester_id: str) -> bool:
    """A user may read a document if they own it or have any share on it."""
    if document.owner_id == requester_id:
        return True
    return any(share.user_id == requester_id for share in document.shares)


def can_edit_document(document: Document, requester_id: str) -> bool:
    """A user may edit a document if they own it or have an EDIT share."""
    if document.owner_id == requester_id:
        return True
    return any(
        share.user_id == requester_id and share.permission == Permission.EDIT
        for share in document.shares
    )


def can_manage_shares(document: Document, requester_id: str) -> bool:
    """Only the owner may grant/revoke access to a document."""
    return document.owner_id == requester_id
