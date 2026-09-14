# SUBMISSION.md

Submission for the Ajaia LLC "AI-Native Full Stack Developer" take-home assignment.

**Candidate:** Benjamin Flatz (beni.flatz@gmail.com)

## What's included in this folder/repo

| File | Purpose |
|---|---|
| [`README.md`](README.md:1) | Local setup and run instructions (backend + frontend), seeded test users, supported file types, known limitations |
| [`ARCHITECTURE.md`](ARCHITECTURE.md:1) | Architecture note: stack choices, layering, data model, sharing/permission model, and what was prioritized/cut and why |
| [`AI_WORKFLOW.md`](AI_WORKFLOW.md:1) | AI workflow note: which AI tools were used, where they sped things up, what was changed/rejected, how correctness was verified |
| [`RAILWAY.md`](RAILWAY.md:1) | Deployment guide for the two-service Railway setup (backend + frontend) via the committed Infrastructure-as-Code file, including the CORS/API-URL circular-dependency resolution |
| `backend/` | FastAPI + SQLModel + SQLite backend, DDD-lite layered (`domain/`, `application/`, `infrastructure/`, `api/`), with `backend/tests/` (pytest, 21 tests) |
| `frontend/` | React + TypeScript + Vite frontend, feature-based structure (`src/features/auth`, `src/features/documents`, `src/shared`), TipTap rich-text editor |
| `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf` | Production container images for both services |
| [`.railway/railway.ts`](.railway/railway.ts:1) | Infrastructure-as-Code definition (Railway's `railway/iac` SDK) provisioning both services, the SQLite volume, health checks, restart policies, and domains — `railway config apply` replaces manual dashboard setup |
| `requirements.md` | The original assignment brief, kept for reference |

## Live deployment

This build was implemented and verified entirely in a sandboxed development
environment that has no Railway account credentials and no outbound network
access from within Docker containers (confirmed while testing the backend
image — `pip install` could not reach `pypi.org` from inside a container,
while the host itself has network access). As a result, **no live Railway
URL was generated as part of this submission** — there was no way to
authenticate against Railway's API/CLI or push a build from this
environment.

The application is deployment-ready:

- Both `backend/Dockerfile` and `frontend/Dockerfile` build standard,
  single-purpose production images (FastAPI/uvicorn on `python:3.11-slim`;
  a Vite static build served by `nginx:1.27-alpine` with `envsubst`
  templating for Railway's dynamic `$PORT`).
- [`.railway/railway.ts`](.railway/railway.ts:1) is a committed
  Infrastructure-as-Code definition (Railway's official `railway/iac` SDK)
  that provisions both services, a persistent volume for SQLite, health
  checks, restart policies, and public domains — `railway config apply`
  stands up the whole environment without any manual dashboard
  configuration.
- [`RAILWAY.md`](RAILWAY.md:1) documents the CLI steps (`railway config
  plan` / `railway config apply`), and the one-time manual step to resolve
  the two services' circular public-URL dependency (`CORS_ORIGINS` /
  `VITE_API_BASE_URL`), which can't be known before the first apply.

Given Railway credentials, standing this up end-to-end is expected to take
a few minutes by running `railway config apply` and following the short
one-time manual step in `RAILWAY.md`. If a live URL is required before
review, I can deploy this on request and share the link.

## Local run (fastest way to evaluate this submission)

```bash
# Backend
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`. Full details, including seeded users and
supported upload file types, are in [`README.md`](README.md:1).

## Seeded test users (for exercising the sharing flow)

The backend seeds four mock users on startup (no passwords — "log in as"
dropdown on the login page). Exact names/ids are listed in
[`README.md`](README.md:1) and [`AI_WORKFLOW.md`](AI_WORKFLOW.md:1). To
demonstrate sharing: log in as one seeded user, create or import a document,
share it with a second seeded user via the share panel, then log out and
log in as that second user to confirm the document appears under "Shared
with me."

## Status against the requirements checklist

**Working end to end:**
- Document creation, rename, edit, save/reopen (persisted in SQLite)
- Rich-text formatting via TipTap: bold, italic, underline, headings,
  bulleted and numbered lists
- File upload: `.txt` and `.md` files are parsed and converted into a new
  editable document (headings, paragraphs, and lists are inferred from
  Markdown-like structure); unsupported file types are rejected with a
  clear error message in the UI and documented in the README
- Sharing: owner can grant another seeded user view or edit access; document
  list UI visually separates "Owned by me" from "Shared with me"; access
  control is enforced server-side (a non-owner/non-shared user gets a 403/404,
  not just a hidden UI element)
- Persistence: documents and shares survive a browser refresh and a backend
  restart (SQLite file on disk / Railway volume in production)
- Validation & error handling: Pydantic schema validation on all endpoints,
  domain-level exceptions mapped to appropriate HTTP status codes, frontend
  surfaces API errors instead of failing silently
- Automated tests: 21 pytest tests covering document CRUD, sharing access
  control (owner/shared/unauthorized), and file-import conversion logic
- Docs: README, ARCHITECTURE.md, AI_WORKFLOW.md, RAILWAY.md all present

**Intentionally deprioritized / not built** (per the assignment's explicit
invitation to scope down and explain tradeoffs):
- Real authentication/authorization provider — replaced with mocked
  "log in as" seeded users, as explicitly permitted by the assignment brief
- `.docx` upload support — only `.txt`/`.md`, clearly stated in the UI and
  README
- Any of the optional stretch features (real-time collaboration indicators,
  commenting, version history, PDF export, granular role-based permissions
  beyond view/edit) — explicitly out of scope per the assignment's "do not
  sacrifice core functionality to pursue stretch work" guidance
- Postgres/managed database — SQLite was chosen as sufficient for this
  scope and timebox; the tradeoff is documented in ARCHITECTURE.md

**What I would build next with another 2-4 hours:**
1. Actually provision the Railway services and obtain a live URL (blocked
   in this environment only by lack of network/credentials, not by missing
   code or config)
2. Real password-based or magic-link auth in place of the mocked
   "log in as" flow
3. `.docx` upload support (would need a parsing library such as
   `python-docx` on the backend)
4. Optimistic concurrency / conflict handling if two collaborators edit the
   same document at once (currently last-write-wins on autosave)
5. One stretch feature — most likely document version history, since the
   content model (versioned JSON blobs) already lends itself to storing
   snapshots with minimal schema change

## Walkthrough video

Not recorded as part of this automated session. A 3-5 minute Loom/YouTube
walkthrough covering the main user flow, what works end to end, what was
deprioritized, key implementation decisions, and AI usage should accompany
the final Google Drive submission per the assignment's deliverables list,
with its URL placed in a plain text file alongside this folder.
