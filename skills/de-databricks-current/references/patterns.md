# Data engineering patterns on Databricks (reference)

## Medallion with SDP

| Layer | Object | Rules |
|---|---|---|
| bronze | streaming table | raw columns as-is plus `_ingest_ts`, `_source_file` (`_metadata.file_path`), `_rescued_data`; no business logic; `expect_or_fail` only on key and sequence columns (see "Design conventions") |
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
- Backfill: see "Idempotency and backfills" below. `once` is not a parameter of `create_auto_cdc_from_snapshot_flow`;
  it belongs to `create_auto_cdc_flow` (Python) and to SQL `AUTO CDC ONCE`.

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
- A full refresh rebuilds from scratch; for large histories prefer a one-time backfill flow plus the live flow.
- For materialized views prefer deterministic SQL so incremental refresh applies.
- Backfill options (syntax in official `databricks-pipelines/references/streaming-table-*.md` and `auto-cdc-*.md`):
  - append history into a streaming table: one-time append flow, `@dp.append_flow(..., once=True)` with `spark.read`
    or SQL `CREATE FLOW ... AS INSERT INTO ONCE <target>` (no `STREAM()`), beside the live append flow;
  - initial load of an AUTO CDC target: SQL `AUTO CDC ONCE INTO <target> FROM SNAPSHOT (...)` (DBR 18.3 or later), or
    Python `dp.create_auto_cdc_flow(..., once=True)` over a batch history source; then the live CDC flow into the
    same target (snapshot plus regular AUTO CDC on one target only where that interoperability is enabled);
  - a ONCE flow re-runs on a full refresh, so `pipelines.reset.allowed=false` on targets that must keep history;
  - date-range reprocessing of a job: job parameters for the range, or Lakeflow Jobs backfill runs (optional, if
    available in the workspace).
- **Backfill plan (in the spec or task, approved before running):** owner and reason; date range and tables; write mode
  and why a re-run is safe (`replaceWhere` / MERGE on keys / ONCE flow); whether consumers are paused or read the old
  data meanwhile; rollback (table version before, RESTORE in dev, human-run outside dev); reconciliation thresholds.
  Run one slice first (one day or one partition), check it, then expand slice by slice. Before consumers read the
  result: row counts per slice against the source, no duplicate business keys, KPI totals reconciled against the
  previous values within the threshold, schema matches the contract. A safe re-run does not prove correct totals
  across slices; reconcile anyway.

## Late-arriving data

- Streaming tables and materialized views handle late rows themselves: watermarks bound streaming state, and an MV
  refresh recomputes the affected aggregates. Nothing extra to build.
- MERGE or notebook pipelines whose downstream aggregates are rebuilt per date must recompute only the dates the late
  rows touch:
  1. in the same run, collect the distinct business dates of the newly arrived rows (e.g. `order_date`), not the
     run date;
  2. rebuild each affected date with `replaceWhere` (or `REPLACE USING`) on the downstream table, in one write;
  3. bound how late is accepted (e.g. 30 days) in the spec; rows older than that go to quarantine with a reason, or
     trigger a planned backfill;
  4. test it: a fixture file with an old date arrives after a newer one, and only that date's aggregate changes.
- SCD2 history: order versions by the record's business timestamp, never by arrival time, so a late older change
  slots into history instead of becoming current.

## Orchestration, delivery and serving

- **Branching in a job**: an If/else `condition_task` picks a path from a task value or job parameter (e.g. full
  vs incremental load); `run_if` (`ALL_SUCCESS`, `AT_LEAST_ONE_SUCCESS`, `ALL_DONE`, ...) controls joins of parallel
  branches; `for_each_task` fans out one task per item (e.g. per source table). Syntax: official
  `databricks-jobs/references/task-types.md` and `examples.md`.
- **Signal that data is ready**: downstream jobs start on a table-update trigger on the published table (official
  `databricks-jobs/references/triggers-schedules.md`), or a task in the same job; for consumers outside Databricks
  jobs, write one "load complete" row per run (run id, business date, row counts) to an audit table they read.
  Consumers never poll for files or guess by time.
- **Copies of a table** (another catalog, region or DR): `CREATE OR REPLACE TABLE <copy> DEEP CLONE <source>`
  re-runs incrementally (only changed files); other workspaces or organisations get Delta Sharing instead of a copy.
  Never clone PII into a catalog with weaker access; masked or row-filtered tables cannot be cloned.
- **Deletes from full-snapshot sources**: in SDP use AUTO CDC from snapshot; in MERGE pipelines add
  `WHEN NOT MATCHED BY SOURCE THEN UPDATE SET is_deleted = true, deleted_at = ...` (soft delete, the default) or
  `THEN DELETE` when the spec says hard delete. Only for full snapshots: on incremental files it would mark every
  absent row deleted.
- **Stable interface for consumers**: consumers read the gold table or a view on it, never a staging table. A breaking
  change ships as `<table>_v2` with the view switched after consumers move (`de-data-contract`), and the old version
  is dropped by a human after the agreed window.

## Graph-shaped tables (when a build track needs them)

Concepts and relationships come from `de-ontology-design`; this is how a build track stores them in Delta.

- **Node tables:** one per concept, keyed by the concept's identifier, with properties as columns, `record_source`,
  and SCD2 validity where the concept changes over time.
- **Edge tables:** one per relationship type: `src_id`, `dst_id`, relationship properties, `valid_from` / `valid_to`
  (SCD2 via AUTO CDC when links change over time), `record_source`, `run_id`, and `confidence` for inferred links.
  Cluster by `src_id` (and `dst_id` if traversed both ways).
- **Edge checks:** both endpoints exist in their node tables; no duplicate edges per (src, dst, valid period);
  cardinality as designed; no cycles where the design says hierarchy.
- **Traversal, cheapest first:** SQL joins for one or two hops; recursive CTE (`WITH RECURSIVE`, official
  `databricks-dbsql` reference) for hierarchies and bounded paths; GraphFrames (ML runtime, classic compute: needs
  a waiver from the serverless convention) for graph algorithms; an external graph database (e.g. Neo4j via its Spark
  connector, dedicated access mode) only when consumers need interactive multi-hop queries. Data exported to an
  external graph is a consumer in the contract and is covered by erasure requests.
- **Incremental sync:** enable change data feed on node and edge tables and push only changes to any external graph.

## Entity resolution (one ID per real-world thing)

- Deterministic first: exact match on strong keys (tax id, normalized email hash, external id), recorded in a
  match table (`source`, `source_key`, `entity_id`, `rule`, `matched_at`).
- Probabilistic matching (open-source libraries such as Splink or Zingg, run on classic compute) only for what the
  deterministic rules leave, with a confidence score and a threshold the owner agrees; matches below it go to a
  review queue, not into the graph.
- Never overwrite source keys to merge: keep the mapping table, so a wrong merge can be undone. The `entity_id` is
  stable; re-runs must not renumber it.
- Measure it: share of records matched per source, entities with more than N source records (likely over-merging),
  and a sample reviewed by the owner (counts in ledgers, never row values).

## Personal data erasure (right to erasure requests)

The goal is to remove what identifies a person while keeping the business records (orders, amounts, history,
totals). Some records must be kept by law (invoices, legal hold); the privacy or legal team decides those, not the
pipeline.

- **Design (default for new tables): keep PII apart.** Personal fields (name, email, phone, address, date of birth)
  live in one small PII table keyed by a surrogate id; facts and dimensions carry only that id. An erasure touches
  one row there, and every report still adds up.
- **Existing tables: anonymize in place.** `UPDATE` the PII columns to NULL or a fixed placeholder and replace the
  natural key with an anonymous id where it identifies the person. Keep the row and its measures.
- **Delete rows only** when the row is nothing but personal data (a contact list row) or legal requires it.
- **A hash is not anonymization.** `sha2(email)` can be matched by anyone who has the email, so it is still personal
  data: overwrite hashed identifiers too.
- **Find every copy:** bronze raw tables and landing files, silver, SCD2 history (all versions, not only the
  current one), quarantine tables, gold, exports and dev clones. Use Unity Catalog lineage from the PII columns.
- **Old versions still hold the values** after an UPDATE or DELETE: time travel and the change data feed keep them
  until cleanup. Finish with `REORG TABLE ... APPLY (PURGE)` where deletion vectors are on, then `VACUUM` after the
  retention period agreed with privacy. This removes old file versions, not current business rows.
- **Streams reading an erased table** need `skipChangeCommits` (or a reset) so the update does not break or replay
  them; SDP targets with `pipelines.reset.allowed=false` keep their history through it.
- **Who runs it:** the agent writes the erasure procedure and tests it in dev with synthetic people. In staging or
  prod a human with the right approval runs it, and the request id, tables touched and row counts are recorded.
  Never run erasure from a scheduled pipeline without that approval.

## Design conventions (apply in specs)

- **AI Functions** (`ai_query`, `ai_classify`, ...): never in bronze; sample in dev (`LIMIT` or a sample table) before
  a full run; persist results in a table (streaming table or MV) instead of calling per query; state the token or
  DBU cost in the spec (`de-cost`). Syntax: official `databricks-dbsql/references/ai-functions.md`.
- **Change data feed and row tracking**: enable row tracking (and CDF where a downstream reads changes) on silver and
  gold sources of materialized views so incremental refresh applies; bronze only when a consumer reads its changes.
- **Protect history**: `pipelines.reset.allowed=false` on SCD2 targets and on bronze whose source has short retention,
  so a full refresh cannot wipe history that cannot be re-read.
- **Bronze failures**: `expect_or_fail` in bronze only on key and AUTO CDC sequence columns (Critical in
  `de-quality-testing/references/severity-and-rules.md`); everything else in bronze is `expect` (log only).

## Dimensional modelling (gold)

Moved to the `de-data-modeling` skill (`references/modeling-rules.md`): grain, bus matrix, conformed dimensions,
surrogate keys, unknown row, SCD per attribute, physical design and validation queries.

## Modeling checklist for the spec

1. Grain stated per table and keys unique at that grain.
2. Time zone of every timestamp known; sequence column chosen.
3. Late-arriving and out-of-order events handled by sequencing, not by assumptions.
4. Delete semantics decided (hard delete, soft delete flag, SCD2 close-out).
5. Reference data (SCD1 dimensions) versus event facts (append) distinguished.
6. PII columns listed, hashed or masked by silver, none in gold.
7. Every acceptance criterion is a query with an expected result.
