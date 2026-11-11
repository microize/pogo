---
name: de-run-diagnose
description: Run, monitor, verify and debug Databricks pipelines and jobs in a bounded loop. Use when the user asks to run a pipeline or job and confirm it worked, or says "did my pipeline fail", "my job failed", "why did the run fail", "why is it slow", "the numbers look wrong", "repair the run", or a run failed, a Spark error or stack trace is pasted, a pipeline is slow or hanging, output tables look wrong, or PySpark code needs a performance review. Classifies the failure, applies a fix, re-runs at most three times, then escalates, and logs every struggle to .challenges_<email>/. Dev target only unless told otherwise.
metadata:
  version: "0.5.0"
---

# de-run-diagnose: run, verify, fix, re-run, escalate

```
RUN -> MONITOR -> VERIFY OUTPUT -> done
          |            |
        FAIL        WRONG DATA
          v            v
       DIAGNOSE (classify) -> FIX -> re-run   (max 3 cycles, then escalate)
```

Every cycle after the first is a challenge entry (`de-sdd-tracking`). Never report success without the verification numbers.

## 1. Run

| What | How |
|---|---|
| Pipeline deployed from a bundle | user deploys the dev target from the Git folder's bundle **Deployments panel** first; then run it like any pipeline (rows below) |
| Pipeline | Lakeflow Pipelines Editor **Run** (or **Validate** as a dry run), or SDK `WorkspaceClient().pipelines.start_update(pipeline_id=..., full_refresh=False)`; `full_refresh=True` only in dev and only when the user agrees |
| Job | Jobs UI **Run now**, or SDK `WorkspaceClient().jobs.run_now(job_id=...)`, then `jobs.get_run(run_id)` |
| Small first | first run with a `test_mode` or `limit_rows` parameter **you added to the pipeline configuration** (not a platform feature), or against a sample source, then full |

Run mechanics (deploy before run, poll the update id not the pipeline state, serverless cold start can sit in
INITIALIZING for minutes, dry run with the editor's Validate or `start_update(validate_only=True)`, selective refresh,
full refresh as a last resort) follow the official `databricks-pipelines/SKILL.md` "Running a Pipeline" section; read
it before the first run. There is no `databricks` CLI in Genie Code on serverless: use the editor, the Jobs UI, the SDK
from a Python cell, and `event_log()` SQL. Where the official skill shows a CLI command, use its SDK or UI equivalent.

Never run against `prod` from this skill. If the user names prod, hand to `de-release-gate` first.

## 2. Monitor

- Pipelines: `SELECT timestamp, level, event_type, message FROM event_log('<pipeline-id>') WHERE level IN ('ERROR','WARN') ORDER BY timestamp DESC`. Flow progress: `event_type = 'flow_progress'`. System table (Beta): `system.lakeflow_pipeline_events_preview.pipeline_events`.
- Jobs (Python SDK, `w = WorkspaceClient()`): `w.jobs.get_run(run_id)` for state and task states (each task's
  `run_id` is the task run id), `w.jobs.get_run_output(task_run_id)` for the error, trace and notebook output. To
  re-run only failed tasks, `w.jobs.repair_run(...)` after the idempotency check in `references/fix-recipes.md`
  ("Repair a failed job run"). SDK mechanics: official `databricks-python-sdk/SKILL.md`.
- Long runs (over 30 minutes or 2x the usual): check whether tasks progress (event log timestamps, Spark UI stages). Stalled with no progress means a diagnose step, not more waiting.

## 3. Verify output (always, even on SUCCESS)

```sql
SELECT count(*) FROM <table>;                                  -- > 0 and near expectation
SELECT max(<ts>) FROM <table>;                                  -- within SLA
SELECT <key>, count(*) FROM <table> WHERE __END_AT IS NULL GROUP BY <key> HAVING count(*) > 1;  -- 0 rows
-- expectations: see de-quality-testing references for the event_log query
```
Silent failures to catch: success with 0 rows written, expectation drop rate jumped, `_rescued_data` populated, full refresh happened unintentionally, table updated but downstream MV not refreshed.

## 4. Diagnose

Classify into one category, then match a pattern in `references/spark-error-catalog.md`. Categories:
OOM, SHF shuffle, SKW skew, CLU cluster, SCH schema or data, NET connectivity, CFG configuration,
LGC logic or correctness, PRM permission, and **PIPE** (declarative pipeline specific):

| PIPE id | Symptom | Cause | Fix |
|---|---|---|---|
| PIPE-01 | AUTO CDC fails on null or unsortable sequence | sequence column NULL or wrong type | `expect_or_fail` on bronze; cast; `struct(ts, seq)` |
| PIPE-02 | "requires full refresh" after code change | changed stateful logic, schema, keys, or SCD type | full refresh in dev; plan prod backfill |
| PIPE-03 | streaming source is not append-only | upstream table had updates or deletes | read with `skipChangeCommits` only if acceptable, else make upstream a streaming table or use AUTO CDC |
| PIPE-04 | expectation `FAIL UPDATE` halted the update | Critical DQ rule violated | fix data or rule; check quarantine |
| PIPE-05 | `PERMISSION_DENIED` on catalog or schema | run-as identity lacks `USE` / `CREATE` / `MODIFY` | grant to the pipeline's run-as principal |
| PIPE-06 | library import fails on serverless | library not declared | declare in pipeline `environment` / bundle `libraries` |
| PIPE-07 | materialized view does full recompute | non-deterministic or unsupported SQL for incremental refresh | simplify; serverless required for incremental |
| PIPE-08 | two updates conflict | concurrent runs of the same pipeline | one trigger; `max_concurrent_runs: 1` on the job |
| PIPE-09 | works on classic, fails on serverless (or reverse) | compute-specific config or `spark.conf` not allowed | remove cluster-only configs; use pipeline configuration |
| PIPE-10 | Preview feature error | feature Beta or needs `PREVIEW` channel | confirm maturity; use GA path for prod |
| PIPE-11 | "<view> was read as a stream ... but is not a streaming table" | a batch view with expectations is read with `STREAM()` or by AUTO CDC | make it a streaming view (AGENTS.md "Current names"); dry-run before the real update |
| PIPE-12 | update stays `WAITING_FOR_RESOURCES` for many minutes | cluster cannot get nodes | read cluster events; `AZURE_QUOTA_EXCEEDED_EXCEPTION` means quota (ENV-01) |
| ENV-01 | `AZURE_QUOTA_EXCEEDED_EXCEPTION` / `QuotaExceeded` | regional vCPU quota shared across teams | stop only your own idle clusters, or ask the platform team; never stop another team's cluster; `de-env-check` |
| ENV-02 | `INSUFFICIENT_PERMISSIONS ... USE SCHEMA on Schema system.access` | system schema not enabled or granted | admin item; impact analysis falls back to lineage API and code reading |
| ENV-03 | `INVALID_ENVIRONMENT` / "No compute is available" | no compute attached or none exists | attach the team's warehouse or ask for compute; `de-env-check` |
| ENV-04 | "Metastore storage root URL does not exist" on `CREATE CATALOG` | no default storage | a human creates the catalog in Catalog Explorer with a location |
| ENV-05 | 401 Unauthorized / expired token on a Git folder pull, push or bundle deploy | Git credential or token expired | user updates the Git credential (Settings > Linked accounts) or re-opens the session; do not retry the deploy first |
| ENV-06 | Genie Code step shows running long after the query finished | display hang | check query history; tell the agent it finished (not a cancel) |

Lakeflow Connect connector failures (gateway, ingestion pipeline, snapshot vs CDC modes) have their own guide:
official `databricks-lakeflow-connect/references/troubleshooting.md`; use it before the generic catalog.

Wrong data with no error is **LGC**: duplicates (join fan-out, non-idempotent append), missing rows (inner join, over-filter), time zone shifts, type mismatch on keys. Check grain before touching code.

Environment errors (ENV-xx) are not code bugs: update the environment record through `de-env-check` and do not
add a `T<nn>-fix` code change for them.

## 5. Fix and re-run

- A fix is work: add `T<nn>-fix` under the current task in `tasks.md` (files, verification), claim it, then edit.
  Smallest change that addresses the matched cause; show the diff. Prefer `references/fix-recipes.md`.
- Re-run the same way as step 1. Three failed cycles, or any fix that would change the spec (keys, grain, SCD type, schedule), means stop and escalate.

## 6. Escalate

Write the report in chat and append it to the challenges file:
error summary, verbatim stack trace (fenced), category and pattern id, what was tried per cycle, affected tables,
recommended human action (grant, quota, decision), and the spec section it touches.

## Performance review mode

When asked to review PySpark or pipeline performance rather than a failure: scan with
`references/anti-pattern-catalog.md`, then check the Databricks-specific list: serverless used, liquid clustering (`CLUSTER BY AUTO`) instead of partitions and Z-ORDER, AQE on (default), broadcast hints for small dimensions, watermarks on stateful streams, no `collect()` / `toPandas()` on large frames, no Python UDF where a native function exists, incremental MV eligibility. Output a prioritized table: finding, impact, fix, effort.

## Changelog
- 0.5.0: QA and gap-analysis fixes: job monitoring through the Python SDK (no CLI), repair_run recipe with
  idempotency check, plain-language triggers, "Tier 1" reworded in fix recipes, anti-pattern catalog defers to the
  PR rule catalog for PR severity and gains AP-21 (cross join).
- 0.4.0: workspace-only: Pipelines Editor, SDK, Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.3.0: PIPE-11/12 and ENV-01..06 from live tests (streaming view, quota, system.access, no compute, metastore root, expired token, display hang).
- 0.2.0: fixes become task lines; parameters wording; official run mechanics and connector troubleshooting pointers.
- 0.1.0: initial.

## Not this skill
Prod deployment or go / no-go (`de-release-gate`), designing DQ rules (`de-quality-testing`), product syntax (official `databricks-pipelines`, `databricks-jobs`).
