/**
 * Railway Infrastructure-as-Code definition for this project.
 *
 * This file is the single source of truth for the Railway environment it
 * manages (see .roo/rules/05-deploy.md). Anything not declared here that
 * exists live in the linked environment will be REMOVED on the next
 * `railway config apply` — never hand-configure resources in the dashboard
 * once this file is in use.
 *
 * Usage:
 *   cd .railway && npm install        # once, to pull in the `railway` package
 *   railway link                      # link the CLI to the target project/environment
 *   RAILWAY_IAC_ENV=production railway config plan    # dry-run — always do this first
 *   RAILWAY_IAC_ENV=production railway config apply   # apply the plan
 *
 * See ../RAILWAY.md for the full walkthrough, including how to resolve the
 * one-time circular dependency between the two services' public domains.
 */
import { defineRailway, service, volume, preserve } from "railway/iac";

// Fail closed: this file only knows how to manage explicitly named
// environments. Running `railway config plan/apply` without setting
// RAILWAY_IAC_ENV to one of these (or against a different environment)
// throws instead of silently guessing, per .roo/rules/05-deploy.md section 3.
const MANAGED_ENVIRONMENTS = ["production"] as const;

export default defineRailway((ctx, project) => {
  const targetEnv = process.env.RAILWAY_IAC_ENV;

  if (!targetEnv || !MANAGED_ENVIRONMENTS.includes(targetEnv as (typeof MANAGED_ENVIRONMENTS)[number])) {
    throw new Error(
      `RAILWAY_IAC_ENV must be set to one of: ${MANAGED_ENVIRONMENTS.join(", ")}. ` +
        `Got: ${targetEnv ?? "(unset)"}. Refusing to plan/apply against an unconfirmed environment.`
    );
  }

  if (!ctx.isEnvironment(targetEnv)) {
    throw new Error(
      `The linked Railway environment does not match RAILWAY_IAC_ENV="${targetEnv}". ` +
        `Run \`railway status\` and \`railway environment\` to confirm you are linked to the right ` +
        `project/environment before planning or applying.`
    );
  }

  // Persistent volume for the backend's SQLite database file. Without this,
  // /app/data (and app.db) is wiped on every redeploy — see
  // .roo/rules/05-deploy.md section 5.
  const backendData = volume("backend-data");

  const backend = service("docs-backend", {
    root: "backend",
    build: {
      builder: "DOCKERFILE",
      dockerfilePath: "Dockerfile",
    },
    healthcheckPath: "/health",
    healthcheckTimeout: 20,
    deploy: {
      restartPolicyType: "ON_FAILURE",
      restartPolicyMaxRetries: 3,
    },
    volumeMounts: {
  "/app/data": backendData,
},
networking: { serviceDomains: { "docs-backend": {} } },
env: {
  // Points the app at the file living on the mounted volume above.
  // backend/src/infrastructure/db_models.py reads DATABASE_URL (default:
  // sqlite:///./data/app.db, which is NOT on the volume) — this override
  // is required per .roo/rules/05-deploy.md section 2, or the SQLite
  // file would live outside /app/data and be lost on every redeploy.
  DATABASE_URL: "sqlite:////app/data/app.db",
  // The frontend's public URL is not known until it has been deployed
  // at least once (its RAILWAY_PUBLIC_DOMAIN doesn't exist yet on a
  // fresh project). Declared as preserve() so the first apply leaves it
  // untouched; set the real value once by hand after both services have
  // a domain, then confirm with a follow-up `railway config plan` that
  // reports no pending changes. See RAILWAY.md.
  CORS_ORIGINS: preserve(),
},
});

  const frontend = service("docs-frontend", {
    root: "frontend",
    build: {
      builder: "DOCKERFILE",
      dockerfilePath: "Dockerfile",
    },
    deploy: {
      restartPolicyType: "ON_FAILURE",
      restartPolicyMaxRetries: 3,
    },
    networking: { serviceDomains: { "docs-frontend": {} } },
    env: {
      // Build-time Vite variable (baked into the bundle via the Dockerfile's
      // ARG/ENV pair). Same circular-dependency situation as CORS_ORIGINS
      // above: the backend's public domain doesn't exist before the first
      // apply, so this starts as preserve() and is set once by hand.
      VITE_API_BASE_URL: preserve(),
    },
  });

  return project("wedo-document", {
    resources: [backend, frontend],
    environments: [...MANAGED_ENVIRONMENTS],
  });
});
