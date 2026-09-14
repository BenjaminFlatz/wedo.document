# Architecture Notes

This document explains the key design decisions behind the collaborative
document editor, the trade-offs made given the assignment's 4-6 hour
timebox, and how the system could evolve beyond this scope.

## 1. High-Level Overview

```
┌─────────────────┐        HTTP (JSON)        ┌──────────────────────┐
│  React SPA       │ ────────────────────────▶ │  FastAPI backend      │
│  (Vite, TipTap)  │ ◀──────────────────────── │  (SQLModel + SQLite)  │
└─────────────────┘                            └──────────────────────┘
```

Two independently deployable services, communicating over a small JSON
REST API. There is no real-time collaboration layer (e.g. WebSockets/CRDT)
— out of scope per the assignment's core requirements — but the boundary
is drawn so that could be added later without restructuring the domain
model (see "Future Work" below).

## 2. Backend: DDD-lite Layering

The backend follows a simplified Domain-Driven Design layout, scoped down
from the repo's full microservices/DDD conventions (no RabbitMQ, no
separate bounded-context services) since this is a single, small
application, not a distributed system:

```
backend/src/
├── domain/          Framework-free entities & exceptions
│   ├── entities.py      User, Document, DocumentShare, Permission
│   └── exceptions.py    DocumentNotFoundError, AccessDeniedError, ...
├── application/     Use-case orchestration
│   ├── document_service.py   DocumentService (all document/share use cases)
│   └── dtos.py                Plain DTOs returned to the API layer
├── infrastructure/  SQLite/SQLModel + file-import concerns
│   ├── db_models.py     SQLModel ORM rows, engine/session setup
│   ├── repositories.py  UserRepository, DocumentRepository (row ⇄ domain)
│   ├── file_import.py   .txt/.md → ProseMirror JSON conversion
│   └── seed.py           Seeds 4 mock users on startup
├── api/             FastAPI routers, Pydantic schemas, DI wiring
│   ├── routers/          auth, documents, shares, upload
│   ├── schemas.py        Request/response Pydantic models
│   └── deps.py           Session, repositories, service, X-User-Id dependency
└── main.py          App wiring, CORS, exception→HTTP mapping, startup hooks
```

**Why this split matters even at this scale**: the `domain` layer has zero
framework dependencies — it's plain Python dataclasses/enums/exceptions.
`DocumentService` (application layer) expresses every use case
(`create_document`, `share_document`, `update_content`, ...) purely in
terms of domain objects and repository interfaces, so it can be unit
tested without spinning up FastAPI or a database. The `api` layer is a
thin adapter: routers call the service and translate DTOs to Pydantic
response models — no business logic lives in a route handler.

**Permission checks live in the domain/application boundary.** Ownership
and share-permission checks (`can_read`, `can_edit`) are evaluated in
`DocumentService`, using the domain entities' own fields (`owner_id`,
`shares: list[DocumentShare]`), and raise `AccessDeniedError` /
`DocumentNotFoundError`. `main.py`'s exception handlers map these to
403/404 HTTP responses uniformly, so every endpoint gets consistent error
semantics for free instead of duplicating `try/except` → status-code logic
per route.

## 3. Data Model

- **User**: `id`, `name`, `email` — seeded, no password.
- **Document**: `id`, `title`, `content` (ProseMirror/TipTap JSON, stored as
  a JSON-serialized text column via SQLModel), `owner_id`, `created_at`,
  `updated_at`.
- **DocumentShare**: join between a document and a user it's shared with,
  carrying a `permission` (`view` | `edit`). A document's owner always has
  implicit full access and never appears as a share row.

Content is stored as TipTap/ProseMirror JSON (not raw HTML or Markdown) so
the frontend editor can load and re-serialize it losslessly, and so
imported `.txt`/`.md` files can be converted directly into the same
structure the editor produces (see `infrastructure/file_import.py`).

## 4. Mocked Authentication

Per the assignment's explicit scope reduction, there is no real identity
provider. On startup, the backend seeds four fixed users (Ada, Alan,
Grace, Linus). The frontend's login screen simply lists them (via
`GET /auth/users`) and lets the user "become" one by storing that user's
id in `localStorage`. Every subsequent API request carries that id in an
`X-User-Id` header; `api/deps.py` resolves it into the current
`User` domain entity via `get_current_user_id`, raising 401-equivalent
domain errors if the header is missing/invalid. This keeps the auth
concern completely isolated to one dependency function — swapping it for
a real provider later (e.g. PropelAuth, per this repo's usual convention)
would only touch `deps.py` and the login page, not `DocumentService` or
any route logic.

## 5. Sharing & Permission Model

- A document's **owner** can rename it, edit its content, delete it, and
  manage (add/revoke) shares.
- A user with a **view** share can open and read the document but cannot
  edit content or manage shares; the frontend disables the editor and
  hides share-management controls, and the backend independently enforces
  this (a direct API call from a view-only user to `PUT .../content`
  returns 403 regardless of what the UI allows).
- A user with an **edit** share can edit content but cannot rename,
  delete, or manage shares — that remains owner-only.
- The documents list endpoint (`GET /documents`) returns two implicit
  groups by joining owned documents and shared-with-me documents,
  which the frontend renders as separate "Owned by me" / "Shared with me"
  sections.

This is a deliberately simple two-tier permission model (view/edit),
matching the assignment's "simple sharing model" requirement rather than
building out a full ACL/roles system.

## 6. Frontend: Feature-Based Structure

```
frontend/src/
├── App.tsx / main.tsx        Router setup, providers
├── features/
│   ├── auth/                 Login page, CurrentUserProvider/hook, authApi
│   └── documents/            List page, editor page, editor/toolbar/share
│       ├── api/               documentsApi, sharesApi (axios calls)
│       ├── components/        DocumentEditor, EditorToolbar, SharePanel, ...
│       ├── hooks/              useDebouncedCallback (autosave)
│       └── pages/              DocumentListPage, DocumentEditorPage
└── shared/
    ├── components/            AppLayout, ProtectedRoute
    ├── lib/apiClient.ts       Axios instance, X-User-Id injection, error helper
    └── types/                 Shared TS types (User, DocumentSummary, ...)
```

Each feature owns its API calls, components, and pages; `shared/` holds
only what's genuinely cross-cutting (the authenticated axios client, the
route guard, and shared TypeScript types). `CurrentUserProvider` holds the
mocked-auth session state and is the single source of truth the rest of
the app reads via `useCurrentUser()`.

**Autosave**: `DocumentEditorPage` debounces content changes (via
`useDebouncedCallback`) before calling `updateDocumentContent`, so typing
doesn't trigger a network request per keystroke, while still persisting
changes automatically without an explicit "Save" button — satisfying the
"persistence across refresh" requirement without extra UI.

## 7. Validation & Error Handling

- **Backend**: domain exceptions (`ValidationError`,
  `UnsupportedFileTypeError`, `DocumentNotFoundError`, `AccessDeniedError`,
  `UserNotFoundError`) are raised from the application layer and mapped to
  appropriate HTTP status codes in `main.py`'s global exception handlers —
  route handlers never construct `HTTPException` themselves, keeping error
  semantics centralized and consistent.
- **Frontend**: `extractErrorMessage()` in `apiClient.ts` normalizes axios
  errors into a human-readable string (using the backend's `detail` field
  when present), and pages/components render an `.error-text` element
  rather than crashing or silently failing.

## 8. Testing

21 pytest tests (`backend/tests/`) cover:
- Document CRUD via the API (`test_documents_api.py`)
- Sharing and access-control enforcement, including the 403 case for
  view-only users attempting to edit (`test_sharing_access_control.py`)
- File-import Markdown/text → ProseMirror JSON conversion
  (`test_file_import.py`)

Given the timebox, frontend tests were not prioritized in favor of a
thorough backend test suite plus a full manual/curl-driven end-to-end
smoke test of the whole user flow (create → edit → share → permission
enforcement → import) exercised against both running services together.

## 9. Trade-offs & Scope Cuts (given the 4-6 hour timebox)

- **No real-time collaboration** (no WebSockets/CRDT/OT) — each save is a
  full-document `PUT`, last-write-wins. Fine for a single-editor-at-a-time
  assignment scope; would need a CRDT library (e.g. Yjs) and a WebSocket
  transport to support concurrent editors safely.
- **No real auth provider** — mocked per the assignment's explicit
  guidance, isolated behind one dependency for easy future replacement.
- **SQLite, not Postgres** — appropriate for a small single-instance app
  and trivial to deploy without provisioning a managed database; would
  move to Postgres for multi-instance/production scaling.
- **No pagination** on the documents list — acceptable given the small,
  demo-scale seeded dataset.
- **Frontend bundle is a single chunk** (~700KB) — no code-splitting was
  set up given the app's small number of routes; would add
  `React.lazy`/route-based splitting for a larger app.

## 10. Future Work

- Real-time co-editing via CRDT (Yjs) over WebSockets, replacing the
  autosave-on-debounce model
- Real identity provider (e.g. PropelAuth) behind the same `deps.py`
  seam
- Version history / undo-to-a-point for documents
- Comments/suggestions mode in the editor
- Migrate SQLite → Postgres and add Alembic migrations for schema
  evolution
