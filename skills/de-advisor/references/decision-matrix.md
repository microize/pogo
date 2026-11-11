# Decision matrix (Databricks, as of Nov 2026; verify maturity before production use)

Scope: choosing **between services**. Choices **inside** a service are already covered by the official skills and are
not repeated here: dataset type (streaming table vs materialized view vs view vs sink) is the decision tree in
`databricks-pipelines/SKILL.md`; serverless STANDARD vs PERFORMANCE_OPTIMIZED vs classic is `databricks-serverless`;
connector choice per source system is `databricks-lakeflow-connect` and `databricks-lakeflow-connect-saas`.

## 1. Ingestion

| Option | Fits when | Trade-offs | Maturity |
|---|---|---|---|
| Lakeflow Connect managed connectors (SaaS, databases) | source is a supported SaaS or OLTP DB, you want managed CDC with minimal code | connector coverage and refresh cadence set by Databricks; cost per connector | GA for major connectors, check per source |
| Auto Loader (`cloudFiles`) into a streaming table | files land in cloud storage or a volume; batch or micro-batch | you own file layout and schema evolution settings | GA |
| Zerobus Ingest (direct write API, gRPC SDKs / REST / OTLP / MQTT / Kafka-compatible) | applications, devices or services push records straight into Unity Catalog tables without a message bus | schema is the contract (no auto-evolution); needs service principal; new pattern for app teams | GA for the core API; maturity differs per interface (official `databricks-zerobus-ingest` marks the Kafka-compatible API and the rescue column Beta); check per interface |
| Kafka / Event Hubs / Kinesis via Structured Streaming or SDP | you already run a message bus; need replay and fan-out | you operate the bus; more moving parts | GA |
| Delta Sharing / UniForm / Iceberg REST | data already lives in another lakehouse | read-only, governance across orgs | GA |

Default: managed connector if it exists; else Auto Loader for files; Zerobus for app-originated events when no bus exists; keep Kafka when it already exists.

## 2. Transformation engine

| Option | Fits when | Trade-offs | Maturity |
|---|---|---|---|
| Lakeflow Spark Declarative Pipelines (SDP, formerly DLT) | medallion ETL, CDC/SCD, streaming tables, expectations, lineage | less control over execution order; some Spark features unavailable | GA |
| Lakeflow Jobs + notebooks / Python wheels | imperative steps, ML, external calls, orchestration of mixed tasks | you write MERGE, checkpoints, retries | GA |
| Structured Streaming (custom) | stateful streaming beyond SDP's model, custom sinks | most code and ops | GA |
| dbt on Databricks SQL | SQL-centric analytics team already on dbt; batch models | no streaming tables / AUTO CDC; separate tool | GA (dbt-sql bundle template) |
| Standalone materialized views / streaming tables in Databricks SQL | a few tables, no pipeline project | limited to SQL, no pipeline-level config | GA (serverless), some Beta features |

Default: SDP for ETL / DWH; Jobs for orchestration around it.

## 3. History / change handling

| Need | Choose | Notes |
|---|---|---|
| current state only | AUTO CDC `stored_as_scd_type=1` | overwrites; no history columns |
| full history of changes | AUTO CDC `stored_as_scd_type=2` (integer) | adds `__START_AT`, `__END_AT`; limit with `track_history_except_column_list` |
| history by business time and system time | bitemporal AUTO CDC (stream CDC only; parameters from the Databricks CDC docs page, not in the official skill yet) | newer (2026); verify GA |
| source gives periodic full snapshots, no CDC | `create_auto_cdc_from_snapshot_flow` / SQL `FROM SNAPSHOT` | SCD1 or SCD2; detects deletes by absence |
| append-only facts / events | streaming table with `@dp.append_flow` | no keys needed |
| custom merge semantics SDP cannot express | `MERGE INTO` in a Job | last resort; own idempotency |

Sequence column must be sortable and non-null; use `struct(ts, id)` for ties.

## 4. Serving

| Consumer | Choose |
|---|---|
| dashboards, BI | gold materialized views; metric views for governed measures; AI/BI dashboards |
| applications needing low-latency reads/writes | Lakebase (Postgres) with synced tables from gold |
| downstream teams / partners | Delta Sharing |
| ML / agents | feature tables, AI Search (formerly Vector Search) for retrieval |

## 5. Compute and mode

| Choice | Default | When to deviate |
|---|---|---|
| Serverless vs classic | serverless | classic only for unsupported libraries, specific instance needs, or existing cost commitments |
| Triggered vs continuous vs real-time | triggered | continuous for minutes latency; real-time mode for sub-second (verify availability) |
| Clustering | `CLUSTER BY AUTO` | explicit `CLUSTER BY` when query patterns are known and stable |

## 6. Deployment and orchestration

- Declarative Automation Bundles (formerly Databricks Asset Bundles) with `dev` / `prod` targets, kept in a Git folder and deployed by a human from the bundle Deployments panel (Public Preview; one workspace per deploy, so prod deploys from the prod workspace's Git folder).
- Lakeflow Jobs for schedules, triggers (file arrival, table update), notifications, retries.
- Pipeline event log (`event_log('<pipeline-id>')`, and the system table `system.lakeflow_pipeline_events_preview.pipeline_events` in Beta) for monitoring and alerts.
