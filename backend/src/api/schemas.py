"""Pydantic request/response schemas for the API layer."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: str
    name: str
    email: str


class DocumentSummaryOut(BaseModel):
    id: str
    title: str
    owner_id: str
    owner_name: str
    created_at: datetime
    updated_at: datetime
    relationship: str
    permission: str


class DocumentDetailOut(BaseModel):
    id: str
    title: str
    content: dict[str, Any]
    owner_id: str
    owner_name: str
    created_at: datetime
    updated_at: datetime
    can_edit: bool
    can_manage_shares: bool


class ShareOut(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    permission: str


class CreateDocumentIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class RenameDocumentIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class UpdateContentIn(BaseModel):
    content: dict[str, Any]


class ShareDocumentIn(BaseModel):
    email: str = Field(min_length=3)
    permission: str = Field(default="edit", pattern="^(view|edit)$")


class ErrorOut(BaseModel):
    detail: str
