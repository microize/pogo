---
name: de-env-check
description: Workspace readiness check for Databricks data engineering, per environment (dev / staging / prod) and per team. Use when starting a new project or track, when the user says "check the environment", "workspace readiness", "what compute do I have", "can I run pipelines here", "prerequisites", "onboard this workspace", "is prod ready", or when a run fails for an environment reason (no compute, quota exceeded, waiting for resources, insufficient privileges, catalog cannot be created). Read-only probe of compute, quota signals, Unity Catalog, system tables and tooling; writes the environment index in specs/project-profile.md and specs/env/<env>-<team>.md with an admin checklist. Never changes settings, grants or clusters.
metadata:
  version: "0.4.1"
---

# de-env-check: know what this workspace can run before designing

Every design choice (serverless or classic, pipeline or warehouse, lineage-based impact analysis) depends on what
the workspace allows. Probe once per project, record it, and re-check when it is older than 30 days or a run fails
for an environment reason.

## Many teams, many environments

Organizations run several workspaces (dev, staging, prod, sometimes per team or region) and each team has its own
clusters, warehouses, policies and quota share. So:

- **One record per environment.** Key every check by workspace host, environment (dev / staging / prod / sandbox)
  and team. A Genie Code session can only probe the workspace it runs in; other environments are probed by someone
  opening Genie Code in that workspace and running this skill there (`references/checks.md`, "Other environments"). Never
  copy one environment's findings to another: serverless, system tables and quotas often differ between dev and prod.
- **Only the team's own compute.** Record which warehouses, cluster policies and clusters this team may use (owner,
  tags, `CAN_ATTACH_TO` / `CAN_USE`). Another team's running cluster is not available capacity, and stopping it is
  never an option for the agent.
- **Shared quota.** Regional vCPU quota is per subscription, shared by every team in it. Record the team's agreed
  share (or "unknown, ask the platform team") and design for it, for example one classic pipeline at a time.
- **Bundle targets match environments.** Each `databricks.yml` target's `workspace.host` must equal the host of the
  environment record it relies on; flag a target that points at an environment never checked.

## Rules

- **Read-only.** Only `SELECT`, `SHOW`, `DESCRIBE` and read API calls (list, get, cluster events). Never start,
  stop, create or resize compute; never create catalogs or schemas; never grant. Anything that needs a change goes to
  the admin checklist, written for a human to run.
- **Do not spend to probe.** Use a running SQL warehouse if there is one. If none is running, ask before starting one;
  never start a cluster just to look.
- **Counts and settings only.** No row values from data tables.
- Stop at the first missing prerequisite that blocks the user's goal and say what is needed (see `de-sdd-implement`,
  "Missing prerequisite").
- **Workspace-only alternatives.** Never suggest the `databricks` CLI, a laptop or CI as a workaround: the method runs
  inside the workspace. No Deployments panel (no serverless) means: the agent creates **dev** jobs and pipelines with
  the Python SDK / Jobs API on allowed classic compute, or an admin enables serverless; non-dev deploys stay user-run.
- **Run SQL where Unity Catalog works.** A cluster in access mode `NONE` (no isolation) cannot read Unity Catalog
  (`UC_NOT_ENABLED`). Use the compute the user names; otherwise a Unity Catalog-capable one (Dedicated or Standard
  cluster, or the team's warehouse), and say which.

## Procedure

1. **Project root and profile.** Find the folder holding `AGENTS.md`; read `specs/project-profile.md`. If its
   `## Environment (de-env-check)` section is younger than 30 days and nothing failed since, show it and stop unless
   asked to refresh.
2. **Run the checks** in `references/checks.md`, in order: identity and admin rights; SQL warehouses; clusters
   (state, node type, cores, **access mode**, auto-stop, owner from the creator field); cluster policies the user can
   use and whether they allow single-node job clusters; serverless for notebooks, jobs and pipelines (no serverless
   is **Blocking** for the default Deployments-panel route); quota signals; design-changing workspace previews
   (yes / no / unknown); Unity Catalog (catalogs, metastore storage root, external locations, create rights, shallow
   clone for zero-copy dev data); system tables (lineage,
   billing, query history); landing volumes; tooling (Git folder, bundle Deployments panel, official skills installed).
3. **Classify each workload** as OK, LIMITED or MISSING with the evidence: SQL, Python notebooks, jobs, Lakeflow
   pipelines, streaming, lineage-based impact analysis, cost reporting, bundle deployment.
4. **Translate into design consequences** using the consequences table in `references/checks.md` (for example: no
   serverless pipelines means classic compute, materialized views always fully recompute and about 10 minutes of
   cluster start per update, so pre-check logic on the warehouse first).
5. **Write**:
   - `specs/project-profile.md`: in the `## Environment (de-env-check)` section, keep one row per environment in the
     environment index (host, env, team, checked date, status) and replace only the row and summary for the
     environment just checked. Never rewrite other sections or other teams' rows.
   - `specs/env/<env>-<team>.md` from `templates/env-readiness.md`: capability table, the team's compute, and the
     admin checklist for that environment (each item with why, who, and the exact statement or setting for a human).
     Mark items that block the current goal as **Blocking**.
   Read both files back after writing.
6. **Report** in chat: the capability table, the blocking items, the environments not yet checked, and what the
   agent will do differently because of them. Offer: "Ask your admin to work through specs/env/<env>-<team>.md, then
   say `recheck`."

## On an environment failure during a track

When `de-run-diagnose` or `de-sdd-implement` hits an environment error (`references/checks.md`, "Error
signatures"), re-run only the affected checks, update the Environment section, add the item to `env-readiness.md`,
and log a challenge through `de-sdd-tracking`.

## Changelog
- 0.4.1: live test fixes: never suggest the CLI as a workaround (it advised "use the command-line tool" when the
  Deployments panel needs serverless); run SQL on Unity Catalog-capable compute (`UC_NOT_ENABLED` on a no-isolation
  cluster).
- 0.4.0: QA and gap-analysis fixes: no serverless is Blocking for the Deployments-panel route (alternatives recorded),
  cluster policies and single-node, design-changing previews, owners from the creator field, shallow clone for dev data.
- 0.3.0: workspace-only: Pipelines Editor, SDK, Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.2.0: per-environment and per-team records (environment index plus specs/env/<env>-<team>.md), team-owned compute
  only, shared quota, bundle target to environment match, other-environment probe.
- 0.1.0: initial, from live tests in a workspace with no serverless pipelines, a 10-vCPU quota, a no-isolation
  cluster, no metastore storage root and no system.access grant.
