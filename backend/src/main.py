"""FastAPI application entry point: wires routers, sets up CORS,
initializes the SQLite database, seeds mock users, and maps domain
exceptions to HTTP responses at the boundary."""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .domain.exceptions import (
    AccessDeniedError,
    DocumentNotFoundError,
    UnsupportedFileTypeError,
    UserNotFoundError,
    ValidationError,
)
from .infrastructure.db_models import init_db
from .infrastructure.seed import seed_users
from .api.routers import auth, documents, shares, upload

app = FastAPI(title="Collaborative Document Editor API", version="0.1.0")

_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_users()


@app.exception_handler(DocumentNotFoundError)
def _document_not_found_handler(request, exc: DocumentNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UserNotFoundError)
def _user_not_found_handler(request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(AccessDeniedError)
def _access_denied_handler(request, exc: AccessDeniedError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
def _validation_error_handler(request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(UnsupportedFileTypeError)
def _unsupported_file_type_handler(request, exc: UnsupportedFileTypeError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(shares.router)
app.include_router(upload.router)
