# Reading the evidence: logs, Spark UI, query profile, plans

Used by **Explain mode**: turn what the user pastes or what you can query into plain words. Checked against
docs.databricks.com (AWS) and spark.apache.org on 2026-11-12. Items marked **unverified** come from community or KB
posts; say so when you rely on them.

## 1. Where each piece of evidence lives, and who can get it

| Evidence | Compute | How you get it | Notes |
|---|---|---|---|
| Error and stack trace of a job task | any | in-workspace: SDK `w.jobs.get_run_output(task_run_id)` | first place to look |
| Pipeline event log | pipelines | in-workspace: `SELECT ... FROM event_log('<pipeline_id>')`; cross-pipeline `system.lakeflow.pipeline_events` (Beta) | by default only the run-as user can read it |
| Query history (duration split, spill, pruning, cache, shuffle) | warehouses, serverless notebooks and jobs, pipelines | in-workspace: `system.query.history` | no Photon share here |
| Query profile (operator DAG, top operators, Photon %, performance insights) | warehouses, serverless, pipelines | user-run: Query History > the query > **Download JSON** (or Share URL), paste the JSON or the insights | owner or CAN MONITOR on the warehouse; no profile for result-cache hits |
| Cluster event log | classic | in-workspace: SDK `w.clusters.events(cluster_id, start_time=..., end_time=...)` | kept 60 days |
| Node CPU / memory / swap / disk per minute | classic | in-workspace: `system.compute.node_timeline` | not for serverless or warehouses; nodes alive under about 10 minutes may be missing |
| Driver logs (stdout, stderr, log4j) | classic | user-run: Compute > the cluster > **Driver logs**, paste the relevant lines; or read delivered logs from a UC volume (`/Volumes/<c>/<s>/<v>/<cluster_id>/...`) if log delivery was set before the run | worker logs are not available in Standard access mode |
| Spark UI (jobs, stages, tasks, SQL, executors) | classic | user-run: Compute > the cluster > **Spark UI**, paste the stage summary table or a screenshot | **not available on serverless**: use the query profile. After termination a history view exists for a while (unverified: about 30 days) |
| Compute metrics UI | classic | user-run: Compute > **Metrics** (1-minute, 30 days, CSV export) | swap only in `node_timeline` |
| `EXPLAIN` | any SQL | in-workspace: `EXPLAIN FORMATTED <query>` | shows the **initial** plan only (see section 5) |

Ask for the smallest paste that answers the question: the error class and the first `Caused by`, the stage summary
table, or the profile JSON. Never ask for data rows, and redact hostnames, tokens and row values before quoting.

## 2. How to explain (answer shape)

Every explanation, whatever the evidence, uses this order and plain words:

1. **What happened**, in one or two sentences a new engineer understands ("Spark ran out of memory on one worker
   while joining orders to customers, because a handful of customer ids carry most of the rows").
2. **The line or number that shows it**, quoted, with what it means.
3. **Why**: the cause, labelled `measured` (from metrics or the error), `likely` (pattern match) or `guess` (needs
   one more piece of evidence, and which).
4. **What to do**: the smallest fix first, with its id from `spark-error-catalog.md` or `fix-recipes.md`; when the
   fix is compute (size, node family, serverless), hand to `de-spark-runtime`; when it is code that a newer runtime
   would do better, `de-spark-runtime` "version advice".
5. **What to check next** if the cause is not `measured`.

Glossary on first use: executor, driver, stage, task, shuffle, spill, skew, partition, broadcast, Photon, AQE.

## 3. Logs and stack traces

- Read **bottom-up for the cause, top-down for the place**: the last `Caused by:` names the root error; the first
  frame in user code (notebook cell, your module) names where it surfaced. Ignore JVM frames in between.
- A Python error inside a Spark task shows as `PythonException` wrapping the Python traceback: the Python part is
  the real error.
- Error classes (`[UNRESOLVED_COLUMN.WITH_SUGGESTION]`, `[DIVIDE_BY_ZERO]`, `[CAST_INVALID_INPUT]`) map directly to
  causes; under ANSI mode (default from Spark 4.0 / recent runtimes) many former NULL results become errors: suggest
  the `try_*` function only when NULL is really the wanted result.
- Repeated `WARN` lines (`TaskSetManager: Lost task`, `BlockManager`, `Executor heartbeat timed out`) matter only
  next to a failure; one-off warnings are noise: say so instead of explaining each.

### Cluster event types and termination codes (classic)

| Seen | Plain meaning | Next |
|---|---|---|
| `DRIVER_NOT_RESPONDING`, `DRIVER_UNAVAILABLE`, termination `DRIVER_OUT_OF_MEMORY` / `DRIVER_UNRESPONSIVE` | the driver (the coordinator) is overloaded: `collect()`, `toPandas()`, huge plans, Python on the driver | OOM-03; driver-side code |
| `NODES_LOST`, `DECOMMISSION_STARTED`, termination `SPOT_INSTANCE_TERMINATION` | the cloud took workers back (spot) | CLU-01 |
| `AUTOSCALING_FAILED`, `AUTOSCALING_BACKOFF`, `ADD_NODES_FAILED`, `CLOUD_PROVIDER_LAUNCH_FAILURE` | could not get machines: quota, stock-out, policy | ENV-01, `de-env-check` |
| `FAILED_TO_EXPAND_DISK`, `DID_NOT_EXPAND_DISK` | local disk full (shuffle or spill) | bigger disk or less shuffle |
| `INIT_SCRIPTS_*`, termination `INIT_SCRIPT_FAILURE` | a startup script failed | CLU-03 |
| `SPARK_EXCEPTION`, `METASTORE_DOWN`, `DBFS_DOWN` | platform-side component failed | retry once; if repeated, admin |
| termination `INACTIVITY` | auto-stop after idle time: normal | none |

## 4. Spark UI (classic) and query profile (serverless, warehouses)

Databricks' guide "Diagnose cost and performance issues using the Spark UI" (/optimizations/spark-ui-guide/) runs in
this order; stop at the first match.

1. **Jobs timeline**: failed jobs or removed executors: section 3. **Gaps of a minute or more** between jobs: the
   driver is busy (Python on the driver, `collect`, file listing) or nothing is running. **Many tiny jobs** of a few
   seconds: loops or per-row actions, overhead dominates. Otherwise open the longest job, then its longest stage.
2. **Spill** (top of the stage page): data did not fit in memory and went to disk. `Spill (memory)` and `Spill
   (disk)` are the same data in two forms: never add them. Fixes: `spark.sql.shuffle.partitions=auto` (classic),
   fewer columns or rows earlier, more memory per node before more nodes.
3. **Skew**: in the stage's summary metrics, the **max** task duration is at least 50% above the **75th
   percentile**: a few tasks do most of the work. Check whether AQE handled it (section 5), else SKW-01..04.
4. **I/O bound?** Largest of input, output or shuffle bytes, divided by total worker cores, divided by stage seconds:
   about **3 MB/s per core** means the stage is limited by reading or writing. Input: better filters and layout
   (liquid clustering), Photon, disk cache. Output: fewer rewrites, deletion vectors. Shuffle: auto partitions.
5. **Slow with little I/O** (SQL tab, node times are summed task time): scans or writes of tens of thousands of files
   or files under 8 MB (small files: OPTIMIZE, predictive optimization); a Python UDF node (native function); a
   cartesian or nested-loop join (missing join key, range join); an **exploding join** (rows out much greater than
   rows in); a one-task stage (no parallelism: repartition or fix a global sort / window without partition).
6. **Task metrics glossary**: GC time high relative to duration = memory pressure; scheduler delay = waiting for a
   free core; task deserialization = large closures or broadcasts; getting result time = big results to the driver;
   shuffle fetch wait = network or a slow executor.

**Query profile equivalents**: read the **performance insights** first (codes such as `EXPLODING_JOIN`,
`DATA_SKEW`, `DATA_FILE_SIZE`, `DATA_SPILL`, `EXCESSIVE_QUEUE_TIME`, `COVERAGE_PHOTON`, `FLOW_FULL_RECOMPUTE`);
then **top operators** (where time went); rows in vs out on joins; **% pruned** on scans (low = layout or filter
mismatch); bytes spilled (warehouse too small); Photon % (low = UDF or unsupported operator); queue time large
(`waiting_at_capacity_duration_ms`): more clusters, not a bigger size; compilation time large: metadata or too many
files.

**From `system.query.history` without a paste**: `spilled_local_bytes > 0` = spill; `pruned_files / (pruned_files +
read_files)` low = poor pruning; `read_io_cache_percent` low on repeated reads = cache not helping;
`waiting_for_compute_duration_ms` = start-up; `waiting_at_capacity_duration_ms` = queue; `total_task_duration_ms /
execution_duration_ms` far below the cores available = poor parallelism or skew.

### Thresholds (defaults; say which one fired)

Adapted from open-source analyzers (Apache-2.0 / MIT): DataFlint, sparkforensics, Dr. Elephant, Microsoft Fabric
Spark skills. They are starting points, not Databricks guidance. "Suppress" says where AQE or serverless makes the
rule moot.

| Signal | Warn | High | Suppress |
|---|---|---|---|
| task skew: max / median task time (at least 20 tasks) | 3x (and max over 5 s) | 10x | AQE already split it (`isSkew=true`) |
| GC time / executor run time | 10% | 20% | serverless (not visible) |
| spill | any task over 1 GiB, or total over 20% of input | over 5 GiB | - |
| largest partition | over 1 GiB | over 5 GiB | - |
| tiny tasks | over 5,000 tasks with median under 500 ms | - | - |
| small files read or written | over 100 files averaging under 3 MB (8 MB on Delta) | tens of thousands | predictive optimization on |
| broadcast too big | over 1 GiB broadcast | - | - |
| should have broadcast | small side under 10 MiB in a sort-merge join | - | AQE converted it |
| exploding join | rows out over 2x the larger input | over 10x | intended many-to-many (say so) |
| unpruned scan | over 1 GiB read with no filter on the clustering / partition columns | over 80% of files read despite filters | - |
| Python UDF | over 64 MiB sent to Python in a stage of 30 s or more | - | - |
| task failures | over 5% of tasks | over 20% | spot loss explained by events |
| regression | run time over 2x the median of the last 5 successful runs (`system.lakeflow.job_run_timeline`): check data volume first, then code or config changes | - | - |

## 5. Plans (`EXPLAIN`, `df.explain()`)

- `EXPLAIN` does not run the query, so with AQE it shows `AdaptiveSparkPlan isFinalPlan=false`: the plan before
  runtime changes. The final plan is in the Spark UI SQL tab, the query profile, or `df.explain()` after an action.
- Read the physical plan **bottom-up**: scans (check `PushedFilters`, `PartitionFilters`, number of files), then
  exchanges (`Exchange hashpartitioning` = shuffle), then joins (`BroadcastHashJoin` cheap for a small side,
  `SortMergeJoin` for two large sides, `BroadcastNestedLoopJoin` / `CartesianProduct` = missing or non-equi join key),
  then aggregates (`HashAggregate` partial and final around a shuffle).
- AQE at work: a join that changed to broadcast, `AQEShuffleRead` with coalesced partitions, `isSkew=true` on a
  sort-merge join, an empty relation replaced by `LocalTableScan`. AQE splits a skewed partition only when it is
  above **both** 5x the median and 256 MB, and never for broadcast or full outer joins.
- `EXPLAIN COST` shows statistics only when they exist; missing statistics are a finding (`ANALYZE TABLE` or
  predictive optimization).
- Photon: Photon operators are named `Photon...` in plans; a non-Photon operator in the middle of a Photon plan names
  the feature that stopped it.

## 6. Pipeline event log metrics

`flow_progress` details: `metrics.num_output_rows`, `backlog_bytes` / `backlog_files` / `backlog_records` /
`backlog_seconds` (growing backlog = the pipeline falls behind), `executor_time_ms`. Classic only:
`cluster_resources.avg_task_slot_utilization` (low = oversized), `avg_num_queued_tasks` (high = undersized),
`optimal_num_executors`. `planning_information` explains why a materialized view was fully recomputed.
`update_progress` time in `WAITING_FOR_RESOURCES` = compute start or quota (PIPE-12). Read JSON fields with
`details:flow_progress.metrics.backlog_bytes`.
