"""SQLModel ORM models and database session management.

This is the only module that knows about SQLite/SQLModel. Domain and
application layers depend on repository interfaces, not on these models
directly (kept lightweight here given the assignment's timebox: the
repositories in `repositories.py` translate between these ORM rows and the
domain dataclasses).
"""
import json
import os
from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRow(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)


class DocumentRow(SQLModel, table=True):
    __tablename__ = "documents"

    id: str = Field(primary_key=True)
    title: str
    content_json: str = Field(default="{}")
    owner_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    shares: List["DocumentShareRow"] = Relationship(
        back_populates="document",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def content(self) -> dict:
        return json.loads(self.content_json) if self.content_json else {}

    def set_content(self, value: dict) -> None:
        self.content_json = json.dumps(value)


class DocumentShareRow(SQLModel, table=True):
    __tablename__ = "document_shares"

    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: str = Field(foreign_key="documents.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    permission: str = Field(default="edit")

    document: Optional[DocumentRow] = Relationship(back_populates="shares")


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=_connect_args)


def init_db() -> None:
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "", 1)
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
