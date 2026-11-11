# PySpark anti-pattern catalog (Databricks 2026 edition)

Items marked (updated) changed because of liquid clustering,
AUTO CDC and serverless. Severity uses the package scale: Blocker (was Critical), Major (was High), Minor (was Medium or Low).
Severities here are for performance review. In a PR review, `de-release-gate/references/pr-rule-catalog.md` decides
and may be stricter (for example AP-13 and cross joins are Blockers there, AP-16 is Advisory = Major).

| Id | Anti-pattern | Severity | Fix |
|---|---|---|---|
| AP-01 | `collect()` on a large DataFrame | Blocker | keep work distributed; `.limit()` for inspection; write to a table |
| AP-02 | `toPandas()` on a large DataFrame | Blocker | native aggregation; `pandas_api()` only when needed |
| AP-03 | Python UDF where a native function exists | Major | `F.initcap(F.trim(...))`, built-in SQL functions, `ai_*` functions for text tasks |
| AP-04 | row-by-row iteration (`for row in df.collect()`) | Blocker | vectorized transformations |
| AP-05 | `monotonically_increasing_id()` as a stable key | Major | `xxhash64` of the natural key, or identity columns |
| AP-06 | `df.count() > 0` for emptiness | Major | `df.isEmpty()` |
| AP-07 | same lineage computed repeatedly | Major | materialize as a view or table in the pipeline; `cache()` only in Jobs and `unpersist()` |
| AP-08 | `cache()` without `unpersist()` | Major | scoped caching |
| AP-09 | schema inference on large reads | Minor | explicit schema; Auto Loader schema hints |
| AP-10 | `SELECT *` carried through layers | Minor | project early; `except_column_list` in AUTO CDC |
| AP-11 | string column refs everywhere | Minor | `col("x")` for type safety in complex expressions |
| AP-12 | hard-coded paths, catalogs, magic numbers | Minor (Blocker in PR review) | pipeline configuration, bundle variables |
| AP-13 | `coalesce(1)` on large output | Major | let Delta manage files; liquid clustering |
| AP-14 | `orderBy()` before write | Minor | drop the global sort; clustering handles layout |
| AP-15 | joins on nested struct fields | Minor | flatten first |
| AP-16 (updated) | `partitionBy(date)` and `ZORDER` on new tables | Minor | `CLUSTER BY AUTO` (liquid clustering) |
| AP-17 (updated) | hand-written MERGE for SCD | Major | AUTO CDC flows (`stored_as_scd_type`) |
| AP-18 (updated) | `spark.conf.set` cluster tuning in pipeline code | Minor | not applied on serverless; use pipeline configuration or fix the query |
| AP-19 | stateful stream without watermark | Blocker | `withWatermark` on every aggregation or stream-stream join |
| AP-20 | `spark.sql(f"... {user_input} ...")` | Blocker | parameter markers or DataFrame API |
| AP-21 | cross join (or join with no or always-true condition) without a comment justifying it | Major (Blocker in PR review) | add the join key; if intended, comment why and bound the small side |

## Join checklist
- Broadcast dimensions under about 100 MB; let AQE handle the rest.
- Check grain on both sides before joining; fan-out is the most common wrong-number bug.
- Cast key types to match; NULL keys never match, handle them explicitly.

## Idempotency checklist
- Re-running a pipeline update must not duplicate rows: streaming tables and AUTO CDC are idempotent by design; Jobs need MERGE on the full key or `replaceWhere`.
- Backfills are tasks with a defined window and a verification query.
