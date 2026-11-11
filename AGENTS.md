# AGENTS.md: data engineering on Databricks, spec-driven

This project uses **spec-driven development (SDD)** for data engineering changes (ETL / ELT, warehouse models,
CDC / SCD pipelines, ingestion, jobs) and for making that data understandable to people and AI: semantic layer
(metric views, keys, comments, Genie Agents) and ontology / knowledge-graph design. It serves data engineers,
analytics engineers, data architects, data modelers, data stewards, tech leads and workspace admins, with advisory
skills alongside, and measures the time it saves against manual estimates (target in `specs/project-profile.md`).
Read this before acting. Package version: `_VERSION` in the installed skills folder.

## Non-negotiable rules

0. **Paths.** The project root is the folder that holds this `AGENTS.md`. Resolve `specs/`, `instructions/`,
   `.internal_*` and `.challenges_*` against it and write with the full workspace path
   (`/Users/<email>/<project>/specs/...` or `/Workspace/.../specs/...`). Never write into the home folder unless it
   is the project root. Read the file back after writing it.
1. **No pipeline, SQL, notebook or bundle code before an approved spec.** Approved means `specs/<track_id>/spec.md`
   has the header line `Status: APPROVED (by <email>, <date>)` **and** a Decision Log row quoting the user's own
   `approved` reply. Until then: questions, drafts, revisions only. Track types `hotfix` and `small` have a shorter
   spec but the same gate. A syntax example shown **in chat only**, labelled as an example and written to no file,
   is not project code and is allowed.
2. **Precedence.** If an official `databricks-*` skill and `de-sdd-spec` both apply and no approved spec exists,
   `de-sdd-spec` governs the process; official skills are welcome for syntax and mechanics. Inside Genie Code skip
   `databricks-core`'s CLI floor check and profile selection; open the product skill's `references/*.md` directly.
3. **One task at a time**, claimed with `(owner: <email>)` in `specs/<track_id>/tasks.md`, dependencies satisfied,
   synced per the project's topology (Git folder Commit & Push, plain-folder re-open, or the Unity Catalog events
   table). Verified before ticked: `in-workspace:` checks you run; `user-run:` checks the user does in the workspace UI
   and pastes.
4. **Ledgers.** Evidence in `.internal_<your-email>/<track_id>/progress.md`; struggles in
   `.challenges_<your-email>/<track_id>.md`, redacted, **in every skill** (spec, implement, review, diagnose). A
   struggle is two failed attempts, any workaround, a file written to the wrong place, or a failed query. Write only
   into your own folders. **Time**: task start / verified / ticked times, and one `.internal_<your-email>/worklog.md`
   row per deliverable outside a track, from `current_timestamp()` folded into a query you already run, never guessed;
   propose a manual estimate the user can correct (`de-sdd-tracking`, "Time and effort").
5. **Never change the spec silently.** Propose the amendment, wait for `approved`; Major amendments get a goldfish
   re-review.
6. **Fresh-eyes review before approval** for full tracks: a **new chat** running
   `@de-goldfish-review specs/<track_id>/spec.md`; Blockers fixed or contested first.
7. **Guardrails** in `instructions/security-guardrails.md` are the single source: dev target only; no destroy, deploy
   or full refresh on non-dev; no DROP / TRUNCATE / GRANT / REVOKE; no secrets or PII in files or chat.
8. **Current names and APIs** (`de-databricks-current`); say when a feature is Preview and prefer GA.

## Current names (always apply)

If a request, existing code or a doc uses the left column, write the right column and say once that you translated
it. Full map and design patterns: `de-databricks-current`.

| Old (in a request, code or docs) | Write instead |
|---|---|
| DLT, Delta Live Tables | Lakeflow Spark Declarative Pipelines (SDP) |
| `import dlt` | `from pyspark import pipelines as dp` |
| `@dlt.table` | `@dp.table` (streaming table) or `@dp.materialized_view` |
| `@dlt.view` | `@dp.temporary_view` |
| `dlt.apply_changes(...)` | `dp.create_auto_cdc_flow(...)` |
| `APPLY CHANGES INTO` | `CREATE FLOW ... AS AUTO CDC INTO` |
| `apply_changes_from_snapshot` | `create_auto_cdc_from_snapshot_flow` |
| `stored_as_scd_type="2"` | `stored_as_scd_type=2` (integer); SQL `STORED AS SCD TYPE 2` |
| `LIVE.` prefix | plain dataset name |
| `CREATE LIVE VIEW` read with `STREAM(...)` | `CREATE TEMPORARY VIEW v AS SELECT ... FROM STREAM(src)`; downstream reads `FROM STREAM(v)` (`databricks-pipelines` temporary-view-sql reference) |
| `partition_cols`, `PARTITIONED BY`, `ZORDER` on new tables | `cluster_by`, `CLUSTER BY AUTO` (liquid clustering) |
| Databricks Asset Bundles (DABs) | Declarative Automation Bundles (file still `databricks.yml`) |
| Workflows | Lakeflow Jobs |
| Vector Search | AI Search |
| Genie Spaces | Genie Agents |
| Lakehouse Monitoring | Data Profiling |
| Mosaic AI Gateway | Unity Gateway |
| Databricks Assistant agent mode | Genie Code |

## Lifecycle (the "manager")

A new project or workspace starts with `de-env-check` (what compute, quota, catalogs and system tables exist).
A broad request ("build a medallion architecture for X") goes through one path: `de-sdd-spec` (discovery,
clarifying questions, spec, goldfish, approval, plan, tasks) then `de-sdd-implement` in **autopilot** (tasks back
to back, self-fix with `de-run-diagnose`, a Validate block per task, tick on the human's `ok`) then
`de-release-gate`. The human answers questions, validates and approves; the agent does the rest.

## Which skill to load

| When the user says... | Load |
|---|---|
| a new requirement, "spec this", "requirement", "greenfield", "brownfield", "new track", "hotfix track" | `de-sdd-spec` |
| "approved", "implement", "next task", "work on T03" | `de-sdd-implement` |
| "goldfish review", "review the spec", "fresh-eyes review" (in a NEW chat) | `de-goldfish-review` |
| "status", "where are we", "what's left", "who did what", "what did we struggle with", "resume", "time report", "productivity report", "how much time did we save" | `de-sdd-tracking` |
| "advise", "advisor mode", "should we use X or Y", "which service", "review this architecture" | `de-advisor` |
| "check the environment", "workspace readiness", "what compute do I have", quota / no compute / privilege errors | `de-env-check` |
| "how much will it cost", "cheapest", "serverless or classic", "cost vs speed", "refresh prices" | `de-cost` |
| "data model", "star schema", "bus matrix", "conformed dimension", "Data Vault", "grain", "ERD", "model review", "metric views", "semantic layer", "Genie on gold" | `de-data-modeling` |
| "ontology", "knowledge graph design", "concepts / properties / relationships in our data", "glossary terms" | `de-ontology-design` |
| "governance audit", "scorecard", "who owns this data", "steward", "PII classification", "tag taxonomy", "unprotected sensitive columns", "ABAC policy", "certify / deprecate", "CDMC" | `de-data-governance` |
| "data contract", "schema change", "what breaks downstream", "impact" | `de-data-contract` |
| "DQ rules", "expectations", "quarantine", "unit tests for the transformation" | `de-quality-testing` |
| "run the pipeline", "it failed", a stack trace, "slow", "wrong numbers", "performance review", "explain this log / Spark UI / query profile / plan" | `de-run-diagnose` |
| "which cluster", "right-size", "cluster too big / idle", "warehouse size", "which runtime / DBR version", "what if we upgrade", "better function on our Spark version", "deprecated?" | `de-spark-runtime` |
| "review this PR", "merge ready", "release checklist", "go / no-go", "deploy to prod" | `de-release-gate` |
| old names (DLT, Asset Bundles, Workflows, Vector Search), SCD / CDC / medallion design, "which official reference" | `de-databricks-current` |
| product syntax: pipelines, jobs, bundles, Zerobus, Lakeflow Connect, grants | official `databricks-pipelines`, `databricks-jobs`, `databricks-dabs`, `databricks-zerobus-ingest`, `databricks-lakeflow-connect`, `databricks-unity-catalog`; `databricks-docs` when none fits |

## Instructions to read before writing code

| Before you... | Read |
|---|---|
| write pipeline, SQL, bundle or job code | `instructions/data-engineering-conventions.md` |
| write or review Python / PySpark | `instructions/python-pyspark-conventions.md` |
| run any command, SQL, or touch grants, secrets, PII | `instructions/security-guardrails.md` |
| deviate from any rule | `instructions/waivers.md`; record the waiver id in the spec's Decision Log |

## Execution environment

Everything happens inside the Databricks workspace; nothing in this method needs a laptop, a local CLI or CI.
- Genie Code does itself (`in-workspace:`): SQL on the attached warehouse, the Python SDK
  (`from databricks.sdk import WorkspaceClient`, workspace auth), the Lakeflow Pipelines Editor (Validate, Run), and
  `pytest.main([...])` in a notebook cell. On serverless the `databricks` CLI is **not** installed; do not plan on it.
- The user does in the workspace UI (`user-run:`): pull, diff and **Commit & Push** in the Git folder dialog; deploy a
  bundle target from the Git folder's **Deployments panel** (Public Preview; only targets in the same workspace, so
  prod is deployed from the prod workspace); admin settings. Say which you are using.
- Read and edit project files with the file tools and do arithmetic in the reply; never run shell or Python cells for
  these (they run on whatever cluster the notebook is attached to).
- Genie Code has **no custom sub-agents, hooks or slash commands**: roles are skills; the goldfish runs in a new chat.
- The official `databricks-*` skills must be installed in the same `.assistant/skills` folder. This repo's
  `install/install_skills` notebook installs both: the `de-*` skills and the vendored official skills in
  `install/official/`.

## Project conventions (the lead fills this in; everything else is in `instructions/`)

- Catalogs: dev `dev_<user>`, staging `<name>`, prod `<name>`. Schemas: `<layer>_<domain>`.
- Pipeline language: SQL | Python (project choice). Compute: serverless. Deployment: bundles with `dev` and `prod` targets (add `staging` if used), deployed from each workspace's Git folder Deployments panel (needs serverless; without it the agent creates **dev** jobs via the Jobs API / SDK, recorded in the spec; non-dev jobs are user-run).
- Topology for shared files: git-folder | plain-folder | org-events (`<catalog>.sdd.task_events`). Email folder style: literal | `_at_`.
- Ledger retention: 12 months. Ledgers are auditable evidence and lesson sources, not performance ratings; anyone may ask the lead to git-ignore their challenges file.
- Commits: `feat(<track_id>): T03 <title>`; `docs(<track_id>): spec approved`.
