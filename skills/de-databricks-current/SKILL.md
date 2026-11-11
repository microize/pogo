---
name: de-databricks-current
description: Cross-service name map and data engineering design patterns for Databricks (2026), plus routing to the official databricks-* skills for syntax. Use when a conversation uses an old service name (DLT, Asset Bundles, Workflows, Vector Search, Genie Spaces, AI Gateway) or an old pipeline API (import dlt, @dlt.table, @dlt.view, dlt.apply_changes, apply_changes_from_snapshot, LIVE. prefix), when choosing medallion layout, SCD type or CDC source handling, or when unsure which official skill reference holds the API. Does not hold product syntax; the official databricks-pipelines, databricks-dabs, databricks-jobs skills do.
metadata:
  version: "0.7.0"
---

# de-databricks-current: right name, right pattern, right reference

Product syntax lives in the official skills (https://github.com/databricks/databricks-agent-skills).
This skill keeps the two things they do not: the **cross-service name map** and the **design patterns**
a spec needs before any syntax is written.

## Name map (old to current, across services)

| You may remember | Current name | Where the syntax lives |
|---|---|---|
| Delta Live Tables (DLT) | **Lakeflow Spark Declarative Pipelines** (SDP, "Lakeflow pipelines") | `databricks-pipelines` (its SKILL.md has the full legacy-to-modern table: `import dlt` to `from pyspark import pipelines as dp`, `apply_changes` to `create_auto_cdc_flow`, `@dlt.view` to `@dp.temporary_view`, `LIVE.` dropped, `partition_cols` to `cluster_by`) |
| `APPLY CHANGES INTO` | **AUTO CDC** | `databricks-pipelines/references/auto-cdc-python.md`, `auto-cdc-sql.md` |
| Databricks Asset Bundles (DABs) | **Declarative Automation Bundles** (file still `databricks.yml`; in the workspace, deployed from the Git folder's Deployments panel) | `databricks-dabs` |
| Workflows | **Lakeflow Jobs** | `databricks-jobs` |
| Ingestion connectors | **Lakeflow Connect** (databases, SaaS, Kafka) | `databricks-lakeflow-connect`, `databricks-lakeflow-connect-saas` |
| Zerobus | **Zerobus Ingest** (direct write API, under Lakeflow Connect) | `databricks-zerobus-ingest` |
| Vector Search | **AI Search** | `databricks-vector-search` (if installed; not vendored by this kit), else `databricks-docs` |
| Genie Spaces | **Genie Agents** | `databricks-genie-agents` (if installed; not vendored), else `databricks-docs` |
| Mosaic AI Gateway / Unity AI Gateway | **Unity Gateway** | `databricks-unity-gateway` (if installed; not vendored), else `databricks-docs` |
| Lakehouse Monitoring | **Data Profiling** | `databricks-unity-catalog/references/7-data-profiling.md` |
| tag policies | **governed tags** (Unity Catalog; GA) | `databricks-unity-catalog` for tag DDL; `de-data-governance` for taxonomy, coverage and ABAC policies; `de-ontology-design` for vocabularies |
| PII scanning, sensitive data discovery | **Data Classification** (GA; auto-tagging Public Preview) and **ABAC** row filter / column mask policies on governed tags (GA) | `de-data-governance` (status table: `references/uc-governance-features.md`) |
| business glossary (in Databricks) | **Pages** (Unity Catalog business semantics; GA per the Nov 2026 release notes; UC wikis Beta) | `databricks-docs` |
| metric views (Unity Catalog business semantics) | **metric views**: GA on AWS per Databricks; some Azure / GCP pages still say Public Preview; check your cloud's release notes. Materialization: Preview | `databricks-metric-views` |
| Domains, Genie Ontology | **Discover page and domains** (GA, Oct 2026) and **Genie Ontology** (GA, Nov 2026), per the Databricks release notes; optional, not the default path | `databricks-docs` |
| Databricks Assistant agent mode | **Genie Code** | runs these skills inside the workspace; no CLI on serverless (see AGENTS.md) |
| Partitioning plus ZORDER | **Liquid clustering** (`CLUSTER BY AUTO`) | `databricks-pipelines/references/performance.md` |
| Classic clusters by default | **Serverless** by default | `databricks-serverless` (`databricks-serverless-migration` if installed; not vendored) |

Say the current name; give the old one once in parentheses if the user used it.

## Code-level map (master copy; AGENTS.md carries this exact subset)

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
| `CREATE LIVE VIEW` read with `STREAM(...)` | `CREATE TEMPORARY VIEW v AS SELECT ... FROM STREAM(src)`; downstream reads `FROM STREAM(v)` (`databricks-pipelines/references/temporary-view-sql.md`; legacy `CREATE STREAMING LIVE VIEW` only in old code) |
| `partition_cols`, `PARTITIONED BY`, `ZORDER` on new tables | `cluster_by`, `CLUSTER BY AUTO` (liquid clustering) |
| Databricks Asset Bundles (DABs) | Declarative Automation Bundles (file still `databricks.yml`) |
| Workflows | Lakeflow Jobs |
| Vector Search | AI Search |
| Genie Spaces | Genie Agents |
| Lakehouse Monitoring | Data Profiling |
| tag policies | governed tags |
| Mosaic AI Gateway | Unity Gateway |
| Databricks Assistant agent mode | Genie Code |

Keep this table and the `## Current names (always apply)` table in AGENTS.md identical in the left column.


## Which official reference to open (so you do not guess an API)

| Need | Open |
|---|---|
| dataset type choice (streaming table vs materialized view vs view vs sink) | `databricks-pipelines/SKILL.md` decision tree |
| SCD1 / SCD2 / bitemporal / snapshot flows, parameters | `databricks-pipelines/references/auto-cdc-python.md` or `-sql.md` |
| expectations syntax (warn / drop / fail, grouped) | `databricks-pipelines/references/expectations-python.md` or `-sql.md` |
| Auto Loader options per format | `databricks-pipelines/references/auto-loader-*.md`, `options-*.md` |
| querying SCD2 (`__START_AT`, `__END_AT`) | `databricks-pipelines/references/scd-2-querying.md` |
| dedup, windows, late data, rescued-data quarantine, lag monitoring | `databricks-pipelines/references/streaming-patterns.md` |
| late-arriving rows in MERGE or notebook pipelines; job branching, "data ready" signals, table copies, deletes from full snapshots, stable consumer interface; backfill plans; graph-shaped tables; entity resolution; personal data erasure requests (keep business rows) | `references/patterns.md` ("Idempotency and backfills", "Late-arriving data", "Orchestration, delivery and serving", "Graph-shaped tables", "Entity resolution", "Personal data erasure") |
| liquid clustering keys, streaming state, joins | `databricks-pipelines/references/performance.md` |
| bundle project layout, targets | `databricks-pipelines/references/1-project-initialization-with-dab.md`, `databricks-dabs` (read for `databricks.yml` structure; deploy from the Deployments panel, not the CLI commands shown there) |
| jobs, tasks, triggers, notifications | `databricks-jobs` |
| grants, lineage system tables | `databricks-unity-catalog` (`references/1-access-control.md`, `references/5-system-tables.md`) |
| row filters, column masks, ABAC | `databricks-unity-catalog/references/4-fine-grained-access.md` |
| sinks (Kafka, Event Hubs, external Delta) and `foreachBatch` from a pipeline | `databricks-pipelines/references/sink-python.md`; `foreach-batch-sink-python.md` (Public Preview, optional) |
| materialized views in a pipeline, incremental refresh eligibility | `databricks-pipelines/references/materialized-view-sql.md` or `-python.md` |
| migrating `import dlt` code | `databricks-pipelines/references/dlt-migration.md` |
| materialized views in Databricks SQL (outside a pipeline: schedule, refresh), temporary tables, pipe syntax | `databricks-dbsql/references/materialized-views-pipes.md` |
| AI Functions (`ai_query`, `ai_classify`, `ai_extract`, ...) in SQL | `databricks-dbsql/references/ai-functions.md` (design rules in `references/patterns.md`) |
| Structured Streaming outside pipelines (checkpoints, triggers, stateful ops, joins, MERGE in `foreachBatch`) | `databricks-spark-structured-streaming` |
| Python SDK calls (`WorkspaceClient`: jobs, pipelines, clusters, warehouses) | `databricks-python-sdk` |
| serverless vs classic, STANDARD vs PERFORMANCE_OPTIMIZED | `databricks-serverless` |
| synthetic or test data | `databricks-synthetic-data-gen` (Spark + Faker script). Drop its `DatabricksSession.builder.serverless()` line and use the notebook's `spark` |
| anything else | `databricks-docs` (llms.txt lookup) |

If the official skills are not installed in this workspace, say so and ask the admin to run the kit's
`install/install_skills` notebook with `include_official` = `yes` (README, "Official skills") before writing
pipeline code. Skip `databricks-core`'s CLI floor check and profile selection (there is no
CLI in Genie Code); open the product skill's `references/*.md` directly, and use the SDK or UI equivalent of any CLI
command it shows.

Official skills pinned for this package: `databricks/databricks-agent-skills` commit `1e883ceb1835` (release 0.2.45, 2026-11-10).
## Design patterns (what a spec decides before syntax)

- **Medallion**: bronze streaming tables (raw plus `_ingest_ts`, `_metadata.file_path`, `_rescued_data`), silver streaming tables with expectations and AUTO CDC for entity history, gold materialized views and metric views. Separate ingestion pipelines from transformation pipelines.
- **History**: SCD1 for current state, SCD2 for history, snapshot flows when the source has no CDC, append-only for
  events. Bitemporal AUTO CDC (business time plus system time) is documented on the Databricks CDC page
  (docs.databricks.com/aws/en/ldp/cdc, stream CDC only; snapshot CDC does not support it) but is not yet in the official
  skill: take parameter names from that page, not from memory. Decide per table in the spec.
- **CDC source shapes**: Debezium-style events, Lakeflow Connect CDC tables, Delta change data feed, nightly full extracts, append-only logs. Each maps to a different flow type; see `references/patterns.md`.
- **Dimensional modeling for gold** (grain, bus matrix, conformed dimensions, surrogate keys, unknown row): load `de-data-modeling`.
- **Quality tiers**: warn / drop / fail mapped to severity; quarantine flow for dropped rows. Rule design in `de-quality-testing`.
- **Operations**: triggered mode by default, serverless, liquid clustering, event log for monitoring, bundles with `dev` and `prod` targets.

## Freshness protocol

Status changes monthly (real-time mode, bitemporal AUTO CDC, Rewind, pipeline unit tests, event-log system table,
catalog commits). Before a spec relies on one: check the Lakeflow pipelines release notes
(`docs.databricks.com/aws/en/release-notes/dlt/<year>`) or the `databricks-docs` skill, and write the status and
date into the spec's Alternatives or Decision Log.

## Changelog
- 0.7.0: governance rows: Data Classification and ABAC routed to de-data-governance; Pages, Discover domains and Genie Ontology statuses updated from the Sep to Nov 2026 release notes.
- 0.6.0: patterns reference adds late-arriving data (recompute affected dates), orchestration/delivery/serving (If/else and for-each tasks, ready signals, DEEP CLONE copies, snapshot delete propagation, stable consumer interface), backfill plan with slice-first reconciliation, graph-shaped tables, entity resolution, status lines for metric views / Domains / Genie Ontology, and personal data erasure (separate PII, anonymize in place, purge old versions, human-run outside dev).
- 0.5.0: QA and gap-analysis fixes: streaming view is `CREATE TEMPORARY VIEW ... FROM STREAM(src)`, non-vendored
  official skills marked "if installed", Data Profiling row, unverified Knowledge Assistant row removed, unrouted
  vendored references routed, snapshot `once` fix and backfill options, AI Functions / CDF / reset / bronze-fail rules.
- 0.4.1: official skills are installed by the kit's install notebook (vendored in install/official).
- 0.4.0: workspace-only: Pipelines Editor, SDK, Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.3.0: code-level map as master copy of the AGENTS.md "Current names (always apply)" table (last synced 2026-11-11); streaming-view lesson.
- 0.2.2: dimensional modeling rules moved to de-data-modeling.
- 0.2.1: old pipeline API names (dlt.view, apply_changes, LIVE.) added as triggers after a live Genie Code test answered from docs search instead of this skill.
- 0.2.0: slimmed to name map, routing and patterns; official pin; Genie Code routing rule; bitemporal caveat.
- 0.1.0: initial.
