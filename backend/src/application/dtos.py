"""Application-layer DTOs returned to the API layer.

Plain dataclasses so the application layer stays framework-agnostic; the API
layer maps these to Pydantic response models.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..domain.entities import Permission


@dataclass
class DocumentSummaryDTO:
    id: str
    title: str
    owner_id: str
    owner_name: str
    created_at: datetime
    updated_at: datetime
    relationship: str  # "owned" | "shared"
    permission: str  # "owner" | "view" | "edit"


@dataclass
class DocumentDetailDTO:
    id: str
    title: str
    content: dict
    owner_id: str
    owner_name: str
    created_at: datetime
    updated_at: datetime
    can_edit: bool
    can_manage_shares: bool


@dataclass
class ShareDTO:
    user_id: str
    user_name: str
    user_email: str
    permission: Permission
