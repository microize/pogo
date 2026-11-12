# Data engineering conventions (Databricks, 2026)

Read before writing pipeline, SQL, bundle or job code. Routed from `AGENTS.md`; the method skills assume these.

## Layers

- **Bronze**: raw, schema-on-read via Auto Loader, add `_ingest_ts`, `_metadata.file_path` as `_source_file`, keep `_rescued_data`. No business logic.
- **Silver**: typed, deduplicated, conformed; expectations enforced; AUTO CDC for entity history; rejected rows to `<table>_quarantine`.
- **Gold**: materialized views and metric views; star schema or wide table per the spec; grain stated.
- Layer transitions are documented in the data contract (`specs/contracts/`).
- Bronze `expect_or_fail` only on key and sequence columns; other bronze expectations log only.
- PII: tagged at bronze, hashed or masked by silver, none in gold. New tables keep personal fields in a separate PII table keyed by a surrogate id, so erasure requests anonymize one row and business records stay.
- AI Functions (`ai_query`, `ai_classify`, ...): not in bronze; sample in dev first; persist results in a table, never recompute per read; estimate the cost in the spec.

## Delta tables

- Delta everywhere; no CSV or JSON as a serving format.
- Liquid clustering (`CLUSTER BY AUTO`) on new tables; no `PARTITIONED BY`, no `ZORDER`.
- Managed tables in Unity Catalog with predictive optimization; do not hand-schedule `OPTIMIZE` unless the spec says so.
- `delta.deletedFileRetentionDuration` at least 7 days on prod targets so time travel can roll back.
- Column mapping mode `name` only when a rename or drop is approved in an impact report.
- Type widening on; prefer widening to re-creating a column.
- `COMMENT` on every table (and key columns); never set `owner` in code or bundles.
- `pipelines.reset.allowed = false` on SCD2 targets and on bronze tables whose source has short retention.

## Writes

- Pipelines: streaming tables and AUTO CDC are idempotent by design; do not add manual dedup on top unless the source itself duplicates.
- Jobs that must write with Spark: `MERGE` on the full key, or `replaceWhere` for partition-level overwrite; never plain `INSERT INTO` or `append` without a key.
- Never `DROP`, `TRUNCATE` or mass `DELETE` in code that can run against prod. Deprecate with a `_deprecated` suffix instead.
- Full refresh of a streaming table or AUTO CDC target is a user decision and a tracked task, never a reflex.

## SQL grain and aggregation integrity

- Every fact query states its grain in a comment: `-- Grain: one row per <entity> per <time>`.
- `GROUP BY` columns equal the stated grain exactly; non-grain attributes use `first()`, `max()` or `any_value()`.
- Dimensions are populated from every source that contributes values, with a catch-all row (`sk = -1`, `UNKNOWN`).
- After build: a left anti join from fact to each dimension returns 0 rows.

## Transformation ordering (silver)

- Cast before filter when the filter uses the cast type (cast `event_date` to DATE before `event_date <> DATE '1900-01-01'`).
- A derived column that references another derived column goes in a second step (`withColumn` after `withColumn`, or a second view), not the same `selectExpr`.
- Document ordering decisions in the spec's transformation rules (`T-xx` blocks).

## Configuration

- Catalog, schema, paths, thresholds come from pipeline configuration or bundle variables (`${var.catalog}`), never literals.
- Global defaults and per-source overrides must not contradict; the override wins and the global is removed or aligned.
- Validate config at load: key presence and value type (positive integers, `https://` endpoints, allowed enums). Fail loudly.
- Pin dependencies to exact versions in `pyproject.toml` or the pipeline `environment`.

## Jobs

- Every job: `max_concurrent_runs: 1`, a `timeout_seconds`, failure notification to a team channel, tags `team`, `environment`, `pipeline`, `cost_center`.
- Task failure policy: critical data and DQ tasks halt the job; notification and cleanup tasks may `continue`.
- Retries with backoff for transient errors; no retry on schema, data-corruption or permission errors.
- Dependency checks before transformation tasks: source exists, is fresh, matches the contract.
- Alert routing: Critical to on-call plus channel; Warning to channel; success to a status channel or nothing.

## Naming

- Tables: `<catalog>.<layer>_<domain>.<entity>` (for example `prod.silver_sales.orders`), or `<layer>_<domain>_<entity>` when one schema per domain is the project convention. Pick one in `specs/project-profile.md`.
- Columns `snake_case`; keys end in `_id`; surrogate keys end in `_sk`; audit columns start with `_`.
- Pipelines `<domain>_<purpose>` (for example `sales_orders_cdc`); jobs `<frequency>_<domain>_<action>` (for example `daily_sales_ingest`).
- Tracks and specs: `<shortname>_<YYYYMMDD>`.

## Deliverables per track

- `databricks.yml` with `dev` and `prod` targets (add `staging` if used); `resources/*.yml`; `src/` one dataset per file.
- Tests under `tests/` and run on Databricks before a task is ticked.
- Spec, plan, tasks, decisions, contracts and gate reports under `specs/`.
- Entry points for `spark_python_task` wheels include an `if __name__ == "__main__":` block that parses arguments and exits with a code.

## Learned in live tests (2026-11-11)

- A view with expectations that a later step reads with `STREAM(...)` or AUTO CDC must be a streaming view; a batch
  pre-check on a SQL warehouse does not test streaming behaviour.
- Validate before you spend: run a dry run (validate-only update) whenever a dataset is added or its type changes; in
  dev the cluster stays up for the shutdown delay, so the real update right after reuses it.
- Development-mode bundles prefix schema names they create; create shared dev schemas once with
  `CREATE SCHEMA IF NOT EXISTS` instead of bundle schema resources.

## Learned in live tests (2026-11-12)

- Read before you query: the first query on a table not yet described in this chat reads its columns
  (`information_schema.columns` or `DESCRIBE`) in the same batch; do not guess column names (a guessed `run_ts` failed).
- Files in a volume: `dbutils.fs.ls('/Volumes/...')` or the `LIST '/Volumes/...'` statement; `FROM LIST(...)` is not a
  table function and fails on classic clusters.
- Integer checksums over many rows overflow under ANSI mode (`sum(xxhash64(...))`); compare `count(*)` plus a
  `sha2(concat_ws(...))` per row aggregated with `collect_list`/`sort_array`, or cast to `DECIMAL(38,0)` before `sum`.
- An absence claim ("no column X", "no source for Y") needs `DESCRIBE` of the candidate tables in every layer
  (bronze, silver, gold); `information_schema` can be incomplete. A live test said "no region field exists anywhere"
  while `DESCRIBE silver.orders` showed it.
