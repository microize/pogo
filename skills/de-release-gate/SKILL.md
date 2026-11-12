---
name: de-release-gate
description: Two gates for Databricks data engineering changes. PR gate: review a diff for anti-patterns, breaking schema changes, missing tests and DQ checks, hard-coded values, secrets, and docs, and give a merge disposition (APPROVE / REQUEST_CHANGES / BLOCK). Prod gate: pre-production readiness scorecard (bundle targets, run-as identity, compute, secrets, grants, DQ gates, SLA, rollback, operations) with a GO / CONDITIONAL_GO / NO_GO verdict. Use before merging or before deploying to prod. Read-only; never deploys.
metadata:
  version: "0.6.2"
---

# de-release-gate: merge gate and prod gate

State the mode in your first line: **PR gate** or **Prod gate**. Both are read-only: you inspect, you do not fix or deploy.
Output files: `specs/<track_id>/pr_review_<n>.md` or `specs/<track_id>/release_<n>.md` (template `templates/readiness-scorecard.md`).

## PR gate

1. **Collect the diff**: the Git folder dialog's diff view (user-run: the user opens it and pastes or names the changed files), or the files the user names. Categorize files: schema / DDL, pipeline code, bundle config, tests, docs, contracts.
2. **Scan with the rule sets** in `references/pr-rule-catalog.md`: anti-patterns, schema-breaking changes (use `de-data-contract` catalog), tests present, DQ rules present, hard-coded values, secrets and security, logic (idempotency, time zones, bronze has no business logic), docs and contract updated.
3. **Spec conformance** (this is a spec-driven project): every changed table is in the approved spec's Targets; the task id in the commit message exists in `tasks.md`; acceptance criteria touched by the change still have a verification. Deviations are Blockers unless the Decision Log records an approved amendment.
4. **Disposition**:
   - APPROVE: no Blockers, at most 3 advisories.
   - REQUEST_CHANGES: no Blockers, more than 3 advisories.
   - BLOCK: any Blocker.
   - BLOCK and rotate: any secret in the diff (token, password, connection string), even if removed in a later commit.
5. Report: findings table (id, rule, file:line, severity, fix), disposition, and what the author must do.

## Prod gate

Run before the prod deploy. Checks are PASS / WARN / FAIL. Any FAIL is NO_GO.
Mechanics come from the official skills: bundle targets and `run_as` (`databricks-dabs`), compute choice
(`databricks-serverless`), grants and masks (`databricks-unity-catalog`), job settings (`databricks-jobs`).
This gate only checks that they were applied, by reading `databricks.yml` and `resources/` in the Git folder and by
SQL and SDK reads. Genie Code has no CLI: a bundle is validated when a human deploys it from the bundle **Deployments
panel** (rocket icon on `databricks.yml` in a Git folder; Public Preview), and the panel deploys only to targets in the
workspace it runs in, so the prod deploy happens from a Git folder in the **prod** workspace.
When a workspace has no serverless (no Deployments panel), never name the `databricks` CLI, a laptop or CI as the
fix: the routes are an admin enabling serverless in that workspace, or jobs created with the Python SDK / Jobs API by
a person in that workspace and recorded as API-managed.

| Area | Checks |
|---|---|
| Bundle and environments | the dev target deployed from the Deployments panel without errors (proves the bundle validates); `prod` target has `mode: production`, `run_as` a service principal, explicit `workspace.host` and `root_path`; no `dev_` catalogs or personal paths in prod config; catalog and schema come from variables, not literals; the diff of `databricks.yml` and `resources/` against the previous release branch (Git folder dialog) shows only expected changes; if a job runs from a Git folder, uncommitted code there is a finding; jobs created via the Jobs API / SDK are not bundle-managed: the spec records them as API-managed (a user with a CLI host or the serverless Deployments panel may bind them to the bundle later), else WARN |
| Identity and grants | run-as principal has `USE CATALOG`, `USE SCHEMA`, `CREATE TABLE`, `MODIFY`, `SELECT` where needed and nothing more; no personal access tokens; grants scripted, not clicked |
| Compute | serverless, or a pinned runtime; pipeline channel `CURRENT` not `PREVIEW`; no Beta features on the prod path unless the Decision Log accepts the risk; continuous pipelines have a maintenance window |
| Secrets | zero plaintext secrets in repo and bundle (grep for `dapi`, `password`, `jdbc:`, `secret`); secret scopes are environment specific; secrets referenced as `{{secrets/scope/key}}` or `dbutils.secrets.get` |
| Data quality gate | all Critical rules are `expect_or_fail` or a failing job task; post-load SQL checks exist for uniqueness at grain and referential integrity; last dev run shows expectation pass rates in the event log |
| SLA and schedule | job schedule or trigger matches the spec; expected runtime leaves at least 20 percent headroom; `max_concurrent_runs: 1`; timeouts and retries set |
| Observability | job failure notifications to a team channel (not a person); the run-health baseline from `de-quality-testing` in place: "no new data" alert, volume band on bronze and gold, job `RUN_DURATION_SECONDS` health rule with a duration-warning notification (streaming: backlog rule); event log query saved |
| Semantic and Genie readiness | when people or Genie query the output: metric views and gold tables have comments and synonyms; PK / FK present (RELY only where checks pass); gold and metric views certified, retired assets deprecated; dev and experimental assets not readable by broad groups (Genie learns from what they can see); benchmark questions return the expected results |
| Full-refresh protection | `pipelines.reset.allowed=false` set on SCD2 targets and on bronze tables whose source keeps data only briefly, so a full refresh cannot wipe history that cannot be reloaded |
| Rollback | previous release on its own branch (`release/<track_id>-<n>`); rollback is "switch the prod Git folder to branch X and deploy"; `delta.deletedFileRetentionDuration` at least 7 days on targets so time travel works; backfill plan if an AUTO CDC target needs a full refresh |
| Tests | unit tests (notebook-cell pytest) and pipeline tests (Pipelines Editor) passed in the workspace, with the summary in `progress.md`; acceptance criteria from spec section 15 all recorded |
| Operations | runbook (where to look, how to re-run, who owns); on-call aware; post-release validation query ready |
| Governance | the latest `de-data-governance` assessment (or a recheck limited to the new tables) shows no Blocker for the tables in this release: group owner, comments, `sensitivity` / `personal_data` on columns, sensitive columns protected; PII columns tagged and masked per contract; contract version bumped if schema changed; impact report done for breaking changes; tables holding personal data have a tested erasure procedure (anonymize, keep business rows; see `de-databricks-current/references/patterns.md`) that a human runs outside dev |

Target layout (`mode: production`, `root_path`, `run_as`): official `databricks-dabs/references/bundle-structure.md`
and `databricks-pipelines/references/pipeline-configuration.md` ("run_as"). Before every prod deploy the user creates
a release branch `release/<track_id>-<n>` in the Git folder dialog. Rollback is "redeploy the previous release"
(user-run in the prod workspace: switch the Git folder to the previous release branch, then deploy the `prod` target
from the Deployments panel). Data rollback uses Delta time travel (`RESTORE TABLE t TO VERSION AS OF n`)
within the retention window, run by a human; AUTO CDC targets need a backfill plan instead.

Verdict:
- GO: no FAIL, at most 3 WARN.
- CONDITIONAL_GO: no FAIL, more than 3 WARN, each with an owner and a date.
- NO_GO: any FAIL.

Report: scorecard, blockers with owners, conditions, and the exact deploy steps the user will do themselves (prod workspace, Git folder, release branch, Deployments panel, `prod` target). Deployment to prod is never done by an agent in this method.

**From NO_GO to a plan.** On NO_GO or CONDITIONAL_GO, offer: "Create a prod-readiness track?" On yes, hand
`templates/prod-readiness-tasks.md` to `de-sdd-spec` as a `small` track (or an amendment of the current one) with
one task per FAIL and WARN, each with owner, the human step if any (service principal, grants, prod catalog), and a
verification. Then re-run the prod gate when the track is done.

Severity scale: findings are Blocker / Major / Minor; checks are PASS / WARN / FAIL (WARN counts as Major).

## Changelog
- 0.6.2: live test fix: a NO_GO blocker suggested "the CLI" as a deploy route; now names only workspace routes (serverless, or SDK / Jobs API jobs recorded as API-managed).
- 0.6.1: prod gate Governance row reads the de-data-governance assessment for the released tables.
- 0.6.0: PR rules for re-run behaviour and row-multiplying joins; run-health baseline in the Observability row; tested personal data erasure procedure in the Governance row; semantic and Genie readiness row.
- 0.5.0: QA and gap-analysis fixes: full-refresh protection row (`pipelines.reset.allowed=false`), uncommitted Git folder code is a finding, API-created jobs recorded as API-managed.
- 0.4.0: workspace-only: Pipelines Editor, SDK, Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.3.0: NO_GO / CONDITIONAL_GO converts into a prod-readiness track from a template.
- 0.2.0: user-run diff and git steps; dabs snippet replaced by official references; unified severity.
- 0.1.0: initial.
