# Deploying to Railway

This project deploys as two independent Railway services from the same
GitHub repo, each built from its own Dockerfile. There is no shared
database between them — the backend persists to a local SQLite file on a
mounted volume.

Deployment is defined as **Infrastructure as Code (IaC)** in
[`.railway/railway.ts`](.railway/railway.ts:1), using Railway's official
`railway/iac` SDK. That file is the single source of truth for both
services — do not hand-configure resources in the Railway dashboard once
it's in use; anything not declared there will be removed on the next apply.

## 1. One-time setup

```bash
# Install the Railway CLI (v5.42.1+), if not already installed.
# See https://docs.railway.com/guides/cli for platform-specific instructions.

# Install the IaC file's own dependencies (the `railway` npm package that
# provides types + the plan/apply engine). This is a separate, isolated
# Node project — it is not part of the frontend app.
cd .railway
npm install
cd ..

# Link the CLI to the target Railway project/environment.
railway link
```

## 2. Plan and apply

The IaC file (`.railway/railway.ts`) refuses to run unless `RAILWAY_IAC_ENV`
is explicitly set to a managed environment name (currently just
`production`), and cross-checks it against the environment the CLI is
actually linked to. This is a deliberate fail-closed guard rail — it will
throw rather than silently guess or apply against the wrong environment.

```bash
# Always dry-run first. Read the plan output before applying anything.
RAILWAY_IAC_ENV=production railway config plan

# Apply once the plan looks correct.
RAILWAY_IAC_ENV=production railway config apply

# Re-run plan afterwards to confirm it reports no pending changes.
RAILWAY_IAC_ENV=production railway config plan
```

This provisions, from a fresh project:

- **`docs-backend`**: built from `backend/Dockerfile` (root `backend/`), a
  persistent volume mounted at `/app/data` for the SQLite database, a health
  check on `/health`, an `ON_FAILURE` restart policy, and a generated public
  domain.
- **`docs-frontend`**: built from `frontend/Dockerfile` (root `frontend/`,
  multi-stage Vite build → nginx runtime), the same restart policy, and a
  generated public domain.

## 3. Resolving the circular domain dependency (one-time, manual)

Two environment variables can't be computed by the IaC file on a **fresh**
project, because each depends on the other service's generated public
domain, which doesn't exist until after the first apply:

| Variable | Service | Needs |
|---|---|---|
| `CORS_ORIGINS` | `docs-backend` | The frontend's generated public URL |
| `VITE_API_BASE_URL` (build-time) | `docs-frontend` | The backend's generated public URL |

Both are declared as `preserve()` in `.railway/railway.ts`, so the first
apply provisions both services (and their domains) without touching these
two variables. After that first apply:

1. Note both services' generated domains (Railway dashboard → each service
   → Settings → Networking, or `railway domain` per service).
2. Set the real values once, out-of-band:
   ```bash
   railway variables set --service docs-backend \
     CORS_ORIGINS=https://<docs-frontend-domain>

   railway variables set --service docs-frontend \
     VITE_API_BASE_URL=https://<docs-backend-domain>
   ```
   (`VITE_API_BASE_URL` is build-time — setting it triggers a rebuild of the
   frontend image since Railway forwards it as a Docker build arg.)
3. Redeploy `docs-backend` if it doesn't pick up the new `CORS_ORIGINS`
   automatically.
4. Confirm both services are wired correctly: visit the frontend URL, check
   the login page loads and lists the seeded users (proves the frontend can
   reach the backend and CORS is configured correctly).
5. Run `RAILWAY_IAC_ENV=production railway config plan` again — because
   both variables are `preserve()`, it should report no pending changes even
   though the dashboard now holds real values.

## 4. Notes

- Both services listen on Railway's dynamically-injected `$PORT`:
  - Backend: `uvicorn` is started with `--port ${PORT:-8000}` directly in
    the Dockerfile `CMD`.
  - Frontend: nginx can't read environment variables in its config file
    natively, so `frontend/nginx.conf` uses a `${PORT}` placeholder that is
    substituted via `envsubst` at container start (see the `CMD` in
    `frontend/Dockerfile`).
- `DATABASE_URL` is set explicitly to `sqlite:////app/data/app.db` in the
  IaC file's backend `env` block, overriding the app's own default
  (`sqlite:///./data/app.db`) so the database file actually lives on the
  mounted volume and survives redeploys.
- Neither service needs a database add-on beyond the backend's own mounted
  volume — this project intentionally uses SQLite rather than Postgres to
  keep the take-home's infrastructure surface minimal (see
  `ARCHITECTURE.md` for the trade-off discussion).
- The legacy `backend/railway.json` / `frontend/railway.json` per-service
  config files have been removed now that `.railway/railway.ts` is the
  single source of truth — Config-as-Code and the IaC file must not coexist
  (see `.roo/rules/05-deploy.md`).
