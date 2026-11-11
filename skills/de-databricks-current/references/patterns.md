# Data engineering patterns on Databricks (reference)

## Medallion with SDP

| Layer | Object | Rules |
|---|---|---|
| bronze | streaming table | raw columns as-is plus `_ingest_ts`, `_source_file` (`_metadata.file_path`), `_rescued_data`; no business logic; `expect_or_fail` only for keys the pipeline cannot live without |
| silver | streaming table (+ AUTO CDC) or materialized view | typed, deduplicated, conformed; expectations; SCD applied here; one table per business entity at a stated grain |
| gold | materialized view / metric view | aggregates, joins for consumption; incremental refresh needs serverless and deterministic logic |

Keep ingestion and transformation in separate pipelines so a bad transform does not block landing data.

## SCD cheat sheet

| Type | What it keeps | AUTO CDC setting | Output columns |
|---|---|---|---|
| 1 | latest row per key | `stored_as_scd_type=1` (integer; see official `auto-cdc-python.md`) | business columns only |
| 2 | every version per key | `stored_as_scd_type=2` (integer, never the string `"2"`) | plus `__START_AT`, `__END_AT` (NULL on current row) |
| 2 subset | versions only when tracked columns change | add `track_history_column_list` or `track_history_except_column_list` | same as 2 |
| bitemporal | business validity and system recording time | stream CDC only; parameters from docs.databricks.com/aws/en/ldp/cdc (not in the official skill yet; snapshot CDC unsupported) | per docs |
| snapshot-based 1 / 2 | derived from periodic full extracts | `create_auto_cdc_from_snapshot_flow(...)` | as above; deletes inferred when a key disappears |

Rules of thumb:
- `sequence_by` must be sortable and non-null. Use `struct(ts, seq)` for ties. Put an `expect_or_fail` on it in bronze.
- Deletes: `apply_as_deletes=expr("op = 'D'")`. Truncates: `apply_as_truncates` (SCD1 only).
- Exclude operational columns with `except_column_list` so they do not create spurious history.
- Querying current rows from SCD2: `WHERE __END_AT IS NULL`.
- Backfill: `create_auto_cdc_from_snapshot_flow(..., once=True)` then the live CDC flow into the same target.

## CDC source shapes

| Source delivers | Treat as |
|---|---|
| Debezium-style events (op, before, after, ts, lsn) | CDC feed; `sequence_by=struct(ts, lsn)`; map `op` to delete predicate |
| Lakeflow Connect CDC tables (`_change_type`, `_commit_version`) | CDC feed; sequence by `_commit_version` (verify column names per connector) |
| Delta change data feed (`table_changes`) | CDC feed with `_change_type` in (`insert`, `update_postimage`, `delete`); drop `update_preimage` |
| nightly full extracts | snapshot flow |
| append-only logs | no CDC; streaming table plus optional dedup window |

## Data quality tiers

| Action | Use for | Effect |
|---|---|---|
| `expect` (warn) | metrics you watch | row kept, counted in event log |
| `expect_or_drop` | rows that must not reach silver | row dropped, counted |
| `expect_or_fail` | invariants whose violation means the feed is broken | update fails |

Quarantine pattern: flow A `expect_or_drop(rule)` into `silver_x`; flow B with `NOT (rule)` into `silver_x_quarantine`.

## Idempotency and backfills

- Streaming tables and AUTO CDC are idempotent per source offset; re-running an update does not duplicate rows.
- A full refresh rebuilds from scratch; for large histories prefer a one-time snapshot flow plus live CDC.
- For materialized views prefer deterministic SQL so incremental refresh applies.

## Dimensional modelling (gold)

Moved to the `de-data-modeling` skill (`references/modeling-rules.md`): grain, bus matrix, conformed dimensions,
surrogate keys, unknown row, SCD per attribute, physical design and validation queries.

## Modeling checklist for the spec

1. Grain stated per table and keys unique at that grain.
2. Time zone of every timestamp known; sequence column chosen.
3. Late-arriving and out-of-order events handled by sequencing, not by assumptions.
4. Delete semantics decided (hard delete, soft delete flag, SCD2 close-out).
5. Reference data (SCD1 dimensions) versus event facts (append) distinguished.
6. PII columns listed and masked or filtered at silver or gold.
7. Every acceptance criterion is a query with an expected result.
