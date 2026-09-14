"""Mocked auth: lists seeded users so the frontend can offer a
'log in as' picker, and echoes back the chosen identity."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...domain.exceptions import UserNotFoundError
from ..deps import UserRepoDep
from ..schemas import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/users", response_model=list[UserOut])
def list_seeded_users(users: UserRepoDep) -> list[UserOut]:
    return [UserOut(id=u.id, name=u.name, email=u.email) for u in users.list_all()]


@router.get("/me/{user_id}", response_model=UserOut)
def get_user(user_id: str, users: UserRepoDep) -> UserOut:
    try:
        user = users.get(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return UserOut(id=user.id, name=user.name, email=user.email)
