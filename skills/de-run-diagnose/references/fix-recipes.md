# Fix recipes

Short, copyable fixes. Prefer the declarative fix (pipeline or table setting) over a Spark config.

## Duplicates or non-idempotent writes
Replace append plus manual dedup with a streaming table and AUTO CDC keyed by business key and sequence
(see `de-databricks-current`). If a Job must write with MERGE, make the match condition the full key and
run with `max_concurrent_runs: 1`.

## Skew: salt the hot key (classic or serverless)
```python
from pyspark.sql.functions import col, lit, concat, floor, rand, explode, array
B = 10
big = big.withColumn("sk", concat(col("k"), lit("_"), floor(rand() * B).cast("int")))
small = small.withColumn("sk", explode(array([concat(col("k"), lit(f"_{i}")) for i in range(B)])))
out = big.join(small, "sk").drop("sk")
```
AQE skew handling is on by default on Databricks; salting is for the cases it misses.

## Small dimension joins
```python
from pyspark.sql.functions import broadcast
fact.join(broadcast(dim), "dim_id")
```

## Schema drift on ingestion
```python
spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
  .option("cloudFiles.rescuedDataColumn", "_rescued_data")
  .load(path)
```
Add `expect("no_rescue", "_rescued_data IS NULL")` on bronze to watch it.

## Concurrent write conflict (Jobs with MERGE)
```python
from tenacity import retry, stop_after_attempt, wait_exponential
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=30))
def safe_merge(): ...
```
Better: one writer per table; split targets.

## Slow JDBC source
Parallel read with `column`, `lowerBound`, `upperBound`, `numPartitions`, `fetchsize`; or move the source to a Lakeflow Connect managed connector.

## External API calls from a pipeline
Backoff with `tenacity` on `ConnectionError` / `TimeoutError`; cap parallelism; cache responses in a bronze table rather than calling per row.

## Small files
Liquid clustering (`CLUSTER BY AUTO`) plus predictive optimization on managed tables; for Jobs, `optimizeWrite` and `autoCompact` table properties. Avoid `coalesce(1)`.

## Full refresh needed (dev)
Pipelines Editor **Full refresh** in dev, or `WorkspaceClient().pipelines.start_update(pipeline_id=..., full_refresh=True)`, with the user's agreement. In prod, plan it as a task with a backfill window and the user's approval.

## Repair a failed job run (re-run only the failed tasks)
Check idempotency first: every task the repair re-runs must be safe to run twice (MERGE on the full key, AUTO CDC,
`INSERT OVERWRITE` of a bounded partition or date range; not a plain append). If a task appends, fix that before
repairing, or delete the partial output in dev first. Then, in a Python cell (dev only):
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
run = w.jobs.get_run(run_id)
failed = [t.task_key for t in run.tasks if t.state and t.state.result_state
          and t.state.result_state.value not in ("SUCCESS", "EXCLUDED")]
w.jobs.repair_run(run_id=run_id, rerun_tasks=failed).result()   # or rerun_all_failed_tasks=True
```
Verify the output after the repair (SKILL.md step 3): row counts must match a single clean run, not double it.

## Permission denied
Write the statements for a human to run (GRANT is forbidden to the agent by `instructions/security-guardrails.md`;
never executed by the agent):
```sql
GRANT USE CATALOG ON CATALOG c TO `<principal>`;
GRANT USE SCHEMA, CREATE TABLE, MODIFY, SELECT ON SCHEMA c.s TO `<principal>`;
```
Grant to the pipeline's run-as principal, not to the developer.
