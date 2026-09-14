# AI Workflow Note

This document describes how AI assistance was used to build this project,
per the assignment's requirement for a short note on AI tool usage.

## Tools Used

- **Roo Code (agentic coding assistant, Claude-based model)** for the vast
  majority of implementation: architecture planning, writing backend and
  frontend code, running commands (installs, builds, tests, dev servers),
  and iterating on errors.

## Workflow

1. **Requirements analysis & architecture planning first.** Before writing
   any code, I had the AI read `requirements.md` in full and propose a
   concrete architecture: tech stack choice (FastAPI + SQLModel/SQLite
   backend, React + TypeScript + Vite frontend with TipTap), layering
   convention (DDD-lite: domain/application/infrastructure/api), the
   mocked-auth approach, and an explicit list of what to skip (stretch
   features, real auth, real-time collaboration) given the timebox. This
   plan was reviewed and approved before implementation began, so the AI
   wasn't making unreviewed architectural decisions mid-stream.

2. **Backend built and tested layer-by-layer.** The AI implemented the
   domain entities and exceptions first (framework-free), then the
   application service (`DocumentService`) expressing every use case, then
   the infrastructure layer (SQLModel rows + repositories translating
   to/from domain objects), then the API layer (routers, schemas, DI). At
   each step, the AI ran the app (`uvicorn`) to smoke-test that it booted
   before moving on, rather than writing all layers blind and debugging
   everything at once.

3. **Tests written against real behavior.** After the backend endpoints
   were working, the AI wrote pytest tests covering document CRUD, the
   sharing/permission model (including the 403-on-view-only-edit case),
   and the file-import Markdown→ProseMirror conversion — then ran the
   suite (21 passing) as a checkpoint before moving to the frontend.

4. **Frontend built feature-by-feature.** Following the same
   plan-then-implement rhythm: auth (mocked login + current-user context)
   first, then the document list, then the TipTap editor with a toolbar,
   then sharing UI, then file upload UI, then styling. The AI ran
   `npm run build` (`tsc -b && vite build`) repeatedly to catch TypeScript
   errors early rather than deferring type-checking to the end.

5. **End-to-end verification before writing documentation.** Rather than
   trusting that each piece worked in isolation, the AI started both the
   backend and frontend dev servers together and ran a scripted `curl`
   sequence exercising the full user story: create a document as one
   user, edit its content, share it with a second user with view-only
   permission, confirm the second user sees it in "Shared with me",
   confirm that user's attempt to edit is correctly rejected with 403, and
   confirm a `.md` file upload correctly converts into a new document.
   This caught the real, integrated behavior rather than relying on unit
   tests alone.

## What the AI Did Autonomously vs. What Required Review

- **Autonomous**: writing all source code, running installs/builds/tests,
  fixing TypeScript/Python errors it encountered along the way, choosing
  specific implementation details within the approved architecture (e.g.
  exact CSS class names, exact DTO shapes, exact test cases).
- **Reviewed/approved by the developer**: the overall architecture and
  stack choice, the explicit scope cuts (no real auth, no real-time
  collaboration, `.txt`/`.md`-only import), and the sharing/permission
  model design — these were presented as a plan and approved before
  implementation started, rather than the AI unilaterally deciding scope.

## Why This Approach

Given the 4-6 hour timebox, the goal was to maximize the fraction of time
spent on code that directly satisfies the assignment's grading criteria
(working app, tests, docs, deployment) rather than on architecture debates
or premature scope expansion. Front-loading a short planning/approval step
meant the AI could then move through implementation, testing, and
verification with minimal back-and-forth, while still keeping a human
checkpoint on the decisions that matter most (stack, scope, data model).
