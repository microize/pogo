---
name: de-quality-testing
description: Data quality rules and tests for Databricks pipelines. Use when the user asks for DQ rules, expectations, validation, duplicate or freshness checks, schema drift detection, quarantine, Data Profiling (formerly Lakehouse Monitoring), or unit tests for pipeline / PySpark / SQL transformation code. Produces a severity-classified rule table (as Lakeflow pipeline expectations plus post-load SQL checks) and runnable tests under tests/. Tests data properties and code logic; does not design tables or run pipelines.
metadata:
  version: "0.4.0"
---

# de-quality-testing: rules for the data, tests for the code

**Precondition**: an approved spec and an open task in `tasks.md` (or a `hotfix` / `small` track). Standalone use
produces a proposal in chat and the rule table for the spec, not files under `tests/`.

Two deliverables, kept apart:
- **Part A, data properties**: completeness, uniqueness, validity, referential integrity, freshness, schema, volume. Implemented as pipeline expectations and SQL checks.
- **Part B, code logic**: unit tests for transformation functions and pipeline flows. Implemented as pipeline unit tests or pytest.

## Part A: data quality rules

### 1. Profile first
Read the spec (targets, grain, keys, section 7) and the contract if one exists. For brownfield, sample the live table (`DESCRIBE`, `SELECT ... LIMIT 100`, null and distinct counts). Decide the layer: bronze loose, silver strict, gold business-critical (`references/severity-and-rules.md`).

### 2. Write the rule table (goes into spec section 7)

| Rule id | Table.column | Dimension | Rule | Severity | Enforcement |
|---|---|---|---|---|---|
| CMP-01 | silver.orders.order_id | completeness | `order_id IS NOT NULL` | Critical | `expect_or_fail` |
| UNQ-01 | silver.orders | uniqueness | one current row per order_id | Critical | aggregate expectation (private incremental MV + `expect_or_fail`), post-load SQL when it must gate downstream |
| RNG-01 | silver.orders.amount | validity | `amount > 0 AND amount < 1e6` | Warning | `expect_or_drop` to quarantine |
| REF-01 | gold.fact_orders.customer_sk | referential | exists in dim_customer | Critical | aggregate expectation on an orphan-count MV, post-load SQL when it must gate |
| FRS-01 | silver.orders | freshness | `max(event_ts) > now() - INTERVAL 2 HOURS` | Critical | SQL alert |
| SCH-01 | bronze.orders | schema | no `_rescued_data` rows above 0.1 percent | Warning | `expect` |
| THR-01 | silver.orders | volume | daily rows within 30-day band | Warning | Data Profiling (formerly Lakehouse Monitoring) or SQL alert |

Id prefixes: CMP, UNQ, RNG, REF, FRS, SCH, THR. Severity maps to action: Critical = fail the update or page; Warning = drop or quarantine and notify; Low = log.

### 3. Enforce on Databricks (write as tasks)

- **Row-level, in the pipeline** (Lakeflow Spark Declarative Pipelines): expectations with warn / drop / fail actions,
  single or grouped. Syntax and placement rules: official `databricks-pipelines/references/expectations-python.md` or
  `expectations-sql.md` (read before writing one). Quarantine of dropped or rescued rows: `databricks-pipelines/references/streaming-patterns.md`.
  Metrics land in the event log: `SELECT * FROM event_log('<pipeline-id>') WHERE event_type = 'flow_progress'` (`details:flow_progress.data_quality.expectations`).
- **Dataset-level, in the pipeline**: uniqueness at grain, orphan foreign keys, row counts over a window, freshness and ratio
  thresholds go into a **private incremental materialized view with `expect_or_fail`** (official pattern:
  `databricks-pipelines/references/expectations-python.md`, "Aggregate Expectations"). Caveat from that file: a failed
  check does not gate other flows in the same pipeline; when the check must block downstream work, put it in a separate
  pipeline chained by a job task, or use the post-load SQL below.
- **Table-level**: `NOT NULL` and `CHECK` constraints for invariants; UC PK / FK for documentation and optimizer hints only.
- **Post-load SQL** for uniqueness at grain, referential integrity, reconciliation against source counts. Put the queries in `tests/dq/<table>.sql` and run them as a job task after the pipeline, failing the task on violations.
- **Trend and drift**: Data Profiling (formerly Lakehouse Monitoring; official `databricks-unity-catalog/references/7-data-profiling.md`) or SQL alerts on saved queries; thresholds start at 2 sigma over a 30-day baseline, tighter for gold.

Write post-load checks from `templates/dq-checks.sql` (one pass/fail row per rule, catalog as a variable, no row
values) and fixture tests for SQL pipelines with `references/sql-fixture-pattern.md` (synthetic files in a separate
test volume, a dev bundle target writing to separate schemas, expected results per case).

### 4. Hand back
Rule table into the spec; enforcement tasks into `tasks.md` (one task per layer); acceptance criteria that re-run the Critical rules.

## Part B: unit tests for code logic

Project layout for tests follows the official `databricks-pipelines/references/1-project-initialization-with-dab.md`
and `databricks-jobs` (pyproject, `tests/`); in Genie Code tests run in a notebook cell or a job task, not with
`uv run pytest` in a shell. This skill adds what those do not say: which tests
to write, where Spark tests must run, and the Databricks-safe session rules.

### Where tests run
- **Pipeline unit tests** (Lakeflow Pipelines Editor, Python, Beta): mock source data, assert flow outputs. Use when the project is an SDP pipeline. Verify availability first; it is Beta.
- **pytest in a notebook cell** for transformation functions factored out of flows and for pure-Python helpers: run
  `pytest.main(["-q", "--assert=plain", "-p", "no:cacheprovider", "/Workspace/.../tests/unit"])` in a notebook cell on
  serverless (or the team's cluster), from the project's Git folder.
- **Scheduled or pre-release runs**: the same `pytest.main` call as a notebook or Python-script task in a Lakeflow
  Job defined in the bundle, so the suite also runs after each dev deploy from the Deployments panel.
  Mark Spark tests with `@pytest.mark.spark` so a fast pure-Python pass can run with `-m "not spark"`.

### Databricks-safe test rules (non-negotiable for Spark tests)
- `SparkSession.builder.getOrCreate()` only; never `.master("local[*]")`, never `spark.stop()`.
- Guard Spark tests with `pytest.importorskip("pyspark")` or `@pytest.mark.skipif(spark is None, ...)`.
- No real I/O: mock cloud reads, JDBC, HTTP, env vars; build inputs with `spark.createDataFrame`.
- Pytest flags when running from a workspace path: `--assert=plain -p no:cacheprovider --cache-dir=/tmp/pytest_cache` (workspace paths can be read-only for `__pycache__`); write reports to `/tmp`.

### Test layout
```
tests/
  conftest.py                 # spark fixture via getOrCreate
  unit/test_<module>.py       # TestXxxHappyPaths, TestXxxSchema, TestXxxEdgeCases, TestXxxErrorHandling
  pipeline/test_<flow>.py     # pipeline unit tests with mocked sources (if using SDP tests)
  dq/<table>.sql              # post-load checks (Part A)
```
Minimum per public function: one happy path, one schema assertion (columns and types), one edge case (empty input, nulls, duplicates), one error case. Add resiliency and performance tests only when the user asks for "advanced".

### Execution is part of the task
Tests are not done until they ran. Paste the pass / fail summary into `progress.md`. A failing test with no fix is a challenge entry, not a skipped step.

## Changelog
- 0.4.0: workspace-only: Pipelines Editor, SDK, Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.3.0: dq-checks.sql template and SQL pipeline fixture pattern.
- 0.2.0: precondition; aggregate expectations via private MV per official pattern; Data Profiling name; in-workspace pytest.
- 0.1.0: initial.

## Not this skill
Table design (`de-sdd-spec`, `de-databricks-current`), running pipelines and diagnosing failures (`de-run-diagnose`), synthetic test data (official `databricks-synthetic-data-gen`).
