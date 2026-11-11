# Compute sizing: choose, size, right-size

Checked against docs.databricks.com (AWS) on 2026-11-12. **Serverless vs classic and the serverless performance mode
are decided by the official `databricks-serverless` skill**; this file covers what it does not: sizing classic
compute when classic is required, SQL warehouse sizing, right-sizing from measured use, and housekeeping. Numeric
utilization thresholds marked **(kit heuristic)** are this kit's proposals: Databricks publishes none. Say so when you
use them.

## 1. Decision order

1. **Compute type**: follow `databricks-serverless` (serverless by default; classic only for R, Scala notebook cells,
   custom images, OS packages, custom data source JARs, a stated runtime or instance need, or no serverless in the
   workspace). SQL: a serverless SQL warehouse; Pro when custom networking or no serverless; Classic warehouses are
   entry level only. Pipelines: serverless (enhanced autoscaling and vertical autoscaling are built in).
2. **Never run scheduled jobs on all-purpose compute**: job compute costs significantly less (Databricks cost
   optimization best practices). Detect it with query J1 (section 4).
3. **Streaming on classic**: job compute; **autoscaling off** for Structured Streaming (production streaming page);
   elastic streaming belongs in a pipeline with enhanced autoscaling. On serverless jobs only `availableNow`
   triggers; continuous work goes to a continuous pipeline or a continuous job.
4. **Classic size by capacity, not node count**: total cores (parallelism), total memory (spill), local disk
   (shuffle, cache). Two 16-core / 128 GB workers equal eight 4-core / 32 GB ones in capacity; fewer, larger workers
   shuffle less over the network.
   | Workload | Start with |
   |---|---|
   | dev / test | single node or 2 to 4 small workers |
   | simple ETL (no wide joins or aggregations) | smaller, lower-memory nodes, autoscale |
   | complex ETL (wide joins, aggregations, MERGE) | fewer, larger, memory-optimized workers (Databricks: "medium, 8 to 16 workers, memory-optimized, autoscaling" as a starting point); on spill or OOM add memory per node before adding workers |
   | analysis, ad hoc, ML exploration | fewer, larger, storage-optimized nodes (disk cache); single node to start ML |
   | streaming, table maintenance (OPTIMIZE, VACUUM) | compute-optimized |
   | GPU | only when the libraries use the GPU |
5. **Photon** (GA, default on recent runtimes): helps long scans, joins, aggregations, MERGE, wide tables, Delta
   writes, stateless streaming. No help for queries under about 2 seconds, Python UDFs, RDD / Dataset code, or
   stateful streaming. It has its own DBU rate: compare **cost per run** with `de-cost`, not only speed.
6. **Spot**: driver and first worker on-demand; spot workers only for latency-tolerant work; flexible node types on
   (admin setting) so a stock-out falls back to an equivalent type.
7. **Runtime**: latest **LTS** for production classic compute (see `runtime-versions.md`); serverless runs the
   environment version set on the job, latest unless a dependency pins it.
8. **Access mode**: Standard (formerly shared) by default; Dedicated (formerly single user, can be a group) for R, ML
   runtime, GPU or APIs Standard does not support. Worker logs are not visible in Standard mode.
9. **Housekeeping**: auto-termination on every interactive cluster (policy example: 60 minutes); cluster policies
   cap workers, node types and require tags; tag compute and pools; pools with min idle 0, spot for workers,
   on-demand for the driver.

## 2. SQL warehouse sizing

| Signal | Meaning | Change |
|---|---|---|
| bytes spilled (`spilled_local_bytes` > 0, `DATA_SPILL` insight) | queries do not fit in memory | one size larger |
| queue time (`waiting_at_capacity_duration_ms`, `EXCESSIVE_QUEUE_TIME`, peak queued > 0 in monitoring) | too many concurrent queries | raise **max clusters**, not the size |
| long periods at 2 or more clusters (`warehouse_events` `SCALED_UP`) | sustained concurrency | check max clusters and size together |
| start-up time (`waiting_for_compute_duration_ms`) | cold starts | serverless, or a longer auto-stop on Pro |
| no queries in 30 days | unused | propose deletion to the owner |

**Sustained pressure, not one bad query** (adapted from the community DBSQL advisor sql-forge, Apache-2.0): over 7
days, call pressure sustained when spill of 1 GiB or more, queue of 10 minutes or more, or cold start of 5 minutes or
more happens on at least 3 days. Queue wait over 50% of execution time is a scaling problem (more clusters or
serverless). Wide transformations under pressure: scale **up** (size); narrow ones with high concurrency: scale
**out** (clusters). Propose downsizing only when spill stays under 0.1 GiB and queue under 1 minute all week.
Confidence is high with 5 of 7 days and at least 100 queries; otherwise "early signal".

Sizes run 2X-Small (1 worker) to 5X-Large (Public Preview). Serverless: start larger and size down. Pro and Classic:
about one cluster per 10 concurrent queries.

## 3. Right-sizing from measured use (classic)

`system.compute.node_timeline` has one row per node per minute (`cpu_user_percent`, `cpu_system_percent`,
`cpu_wait_percent`, `mem_used_percent`, `mem_swap_percent`, `disk_free_bytes_per_mount_point`, `driver`). It does not
cover serverless or warehouses: use `system.query.history`, the query profile and billing there.

| Pattern (over representative runs) | Verdict | Proposal |
|---|---|---|
| workers: average CPU (user + system) under 25% and p95 under 50%, memory under 50% (kit heuristic) | oversized | fewer or smaller workers, or serverless |
| `mem_swap_percent` > 0 sustained, memory over 90%, or spill in query history | memory-bound | more memory per node (memory-optimized) before more workers |
| `cpu_wait_percent` high (kit heuristic: over 20%) and the 3 MB/s-per-core rule holds | I/O-bound | storage-optimized or disk cache, better layout and pruning |
| driver row busy (CPU over 80% or memory over 90%) while workers idle | driver bottleneck | fix driver-side code first (`collect`, Python loops); then a larger driver |
| `disk_free` low, `FAILED_TO_EXPAND_DISK` events | shuffle or spill fills local disk | larger local disk or less shuffle |
| all-purpose cluster with long near-zero CPU periods, auto-termination 0 or over 120 minutes | idle spend | auto-termination 30 to 60 minutes, policy |
| idle core share over 50% across runs (DataFlint) or core utilization under 30% (sparkforensics) | oversized | as the first row |
| peak memory over 95% / under 70% of the node (DataFlint) | under / over provisioned memory | +20% memory / smaller memory family |
| autoscaling removes executors within 2 minutes of adding them on 30% or more of executors | autoscaling churn | narrower min / max range, or fixed size for steady loads |
| pipeline `cluster_resources.avg_task_slot_utilization` low / `avg_num_queued_tasks` high | over / under provisioned pipeline | lower / raise `max_workers` (classic pipelines) |

A verdict needs at least three representative runs or a week of an interactive cluster; with fewer, say "early
signal". Never recommend a change from a single run.

## 4. Queries (read-only, counts and metadata)

**C1 current cluster config** (`system.compute.clusters` keeps one row per change; take the latest)
```sql
SELECT c.cluster_id, c.cluster_name, c.cluster_source, c.dbr_version, c.data_security_mode,
       c.driver_node_type, c.worker_node_type, c.worker_count, c.min_autoscale_workers, c.max_autoscale_workers,
       c.auto_termination_minutes, w.core_count AS worker_cores, w.memory_mb AS worker_memory_mb,
       current_timestamp() AS ts
FROM system.compute.clusters c
LEFT JOIN system.compute.node_types w ON w.node_type = c.worker_node_type
WHERE c.cluster_id IN (<ids>) AND c.delete_time IS NULL
QUALIFY row_number() OVER (PARTITION BY c.workspace_id, c.cluster_id ORDER BY c.change_time DESC) = 1;
```

**C2 utilization per cluster and role, last 14 days**
```sql
SELECT cluster_id, driver,
       round(avg(cpu_user_percent + cpu_system_percent), 1)                         AS avg_cpu,
       round(percentile(cpu_user_percent + cpu_system_percent, 0.95), 1)            AS p95_cpu,
       round(avg(cpu_wait_percent), 1)                                              AS avg_cpu_wait,
       round(avg(mem_used_percent), 1)                                              AS avg_mem,
       round(max(mem_used_percent), 1)                                              AS max_mem,
       round(max(mem_swap_percent), 1)                                              AS max_swap,
       count(DISTINCT instance_id)                                                  AS nodes_seen,
       count(*)                                                                     AS node_minutes
FROM system.compute.node_timeline
WHERE cluster_id IN (<ids>) AND start_time >= current_timestamp() - INTERVAL 14 DAYS
GROUP BY ALL;
```

**J1 jobs running on all-purpose compute, last 30 days**
```sql
WITH clusters AS (
  SELECT cluster_id, cluster_name, cluster_source FROM system.compute.clusters
  QUALIFY row_number() OVER (PARTITION BY workspace_id, cluster_id ORDER BY change_time DESC) = 1)
SELECT t.job_id, c.cluster_id, c.cluster_name, count(DISTINCT t.job_run_id) AS runs
FROM system.lakeflow.job_task_run_timeline t
LATERAL VIEW explode(t.compute_ids) AS cid
JOIN clusters c ON c.cluster_id = cid
WHERE t.period_start_time >= current_timestamp() - INTERVAL 30 DAYS AND c.cluster_source IN ('UI', 'API')
GROUP BY ALL;
```

**Q1 query-level signals (serverless, warehouses, pipelines)**
```sql
SELECT compute.type AS compute_type, compute.warehouse_id,
       count(*) AS queries,
       round(percentile(total_duration_ms, 0.95) / 1000, 1)                AS p95_s,
       count_if(spilled_local_bytes > 0)                                  AS queries_spilling,
       round(avg(waiting_at_capacity_duration_ms) / 1000, 1)              AS avg_queue_s,
       round(avg(waiting_for_compute_duration_ms) / 1000, 1)              AS avg_startup_s,
       round(sum(pruned_files) / nullif(sum(pruned_files) + sum(read_files), 0), 2) AS prune_ratio,
       round(avg(read_io_cache_percent), 0)                               AS avg_cache_pct
FROM system.query.history
WHERE start_time >= current_timestamp() - INTERVAL 14 DAYS AND <filter: warehouse_id, query_source.job_info.job_id, ...>
GROUP BY ALL;
```
`query_source` field names are nested; run `DESCRIBE TABLE system.query.history` once and adapt the filter.

**B1 cost per run and Photon share** (with `de-cost` for list prices)
```sql
SELECT usage_metadata.job_id, usage_metadata.job_run_id, billing_origin_product,
       product_features.is_serverless, product_features.is_photon, product_features.performance_target,
       sum(usage_quantity) AS dbus
FROM system.billing.usage
WHERE usage_date >= current_date() - 30 AND usage_metadata.job_id IN (<ids>)
GROUP BY ALL;
```

**W1 warehouses: config and scale events**: `system.compute.warehouses` (latest row per `warehouse_id`) and
`system.compute.warehouse_events` (`event_type`, `cluster_count`, `event_time`) for the last 30 days.

## 5. Recommendation shape

For every proposal: current setting, proposed setting, evidence (query, numbers, runs counted), expected effect on
run time and cost per run (`de-cost`), risk, and where the change goes: a bundle `resources/*.yml` change through a
`small` track (`de-sdd-spec`), a cluster policy (admin), or a warehouse setting (owner). This skill never edits,
resizes, starts or stops compute.
