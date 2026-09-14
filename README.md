# Collaborative Document Editor

A lightweight, Google-Docs-inspired collaborative document editor built for
the Ajaia LLC "AI-Native Full Stack Developer" take-home assignment.

- **Backend**: FastAPI + SQLModel (SQLite), DDD-lite layering
- **Frontend**: React 19 + TypeScript + Vite, TipTap rich-text editor
- **Auth**: mocked — seeded users, no passwords, "log in as" dropdown

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for design decisions and
[`AI_WORKFLOW.md`](AI_WORKFLOW.md) for how AI tools were used to build this.

## Features

- Create and edit rich-text documents (bold, italic, underline, headings,
  bulleted/numbered lists) via a TipTap-based editor with a formatting
  toolbar
- Import `.txt` / `.md` files as new editable documents (Markdown headings,
  paragraphs and lists are converted to rich-text structure)
- Share a document you own with another seeded user, granting either
  **view** or **edit** permission; revoke access at any time
- Documents list distinguishes **Owned by me** vs **Shared with me**
- Autosave while editing, plus inline title rename
- Content persists in SQLite and survives a full page refresh
- Server-side validation and permission enforcement (403 on unauthorized
  edits, 404 on missing resources, etc.)

## Project Structure

```
backend/     FastAPI application (domain / application / infrastructure / api layers)
frontend/    React + TypeScript SPA (feature-based structure)
```

## Prerequisites

- Python 3.11+
- Node.js 20+ and npm
- (optional) [`uv`](https://github.com/astral-sh/uv) for faster Python installs

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run the dev server (auto-reload)
uvicorn src.main:app --reload --port 8000
```

The backend seeds 4 mock users on startup (Ada, Alan, Grace, Linus) into a
local SQLite database at `backend/data/app.db`. No login credentials are
required — the frontend sends an `X-User-Id` header identifying "who you're
logged in as".

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Running backend tests

```bash
cd backend
pytest
```

21 tests cover document CRUD, sharing/access-control, and file-import
conversion logic.

### Backend environment variables

| Variable       | Default                  | Purpose                                   |
|----------------|---------------------------|--------------------------------------------|
| `CORS_ORIGINS` | `http://localhost:5173`   | Comma-separated list of allowed origins    |
| `DATABASE_URL` | `sqlite:///./data/app.db` | SQLite connection string                   |

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Pick one of the seeded users from the login
screen to get started — no password needed.

### Frontend environment variables

Create a `.env` file in `frontend/` (or set the variable in your shell)
if the backend isn't running on the default URL:

| Variable              | Default                  | Purpose                       |
|-----------------------|---------------------------|--------------------------------|
| `VITE_API_BASE_URL`   | `http://localhost:8000`   | Base URL of the backend API    |

### Building for production

```bash
cd frontend
npm run build
```

Outputs a static bundle to `frontend/dist/`, which can be served by any
static file host (or a container, see below).

## Running Both Together Locally

1. Start the backend: `cd backend && uvicorn src.main:app --reload --port 8000`
2. Start the frontend: `cd frontend && npm run dev`
3. Visit http://localhost:5173, log in as one of the seeded users, and
   create, edit, share, or import a document.

## Deployment

Both services are containerized (see `backend/Dockerfile` and
`frontend/Dockerfile`) and deployed on [Railway](https://railway.app). See
`SUBMISSION.md` for the live deployment URL and additional deployment notes.

## Seeded Users

| Name  | Email               |
|-------|---------------------|
| Ada   | ada@example.com     |
| Alan  | alan@example.com    |
| Grace | grace@example.com   |
| Linus | linus@example.com   |

Use these to test sharing: log in as one user, create a document, share it
with another, then log in as that user (via the login screen) to see the
shared document appear under "Shared with me".
