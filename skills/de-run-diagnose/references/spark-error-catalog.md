# Spark and Databricks error catalog

Trimmed (Nov 2026) to what still applies on Databricks with
serverless and Lakeflow pipelines. Memory, shuffle and executor settings apply to classic compute only;
on serverless, fix the query or data shape instead. Pipeline-specific PIPE patterns live in SKILL.md.

## OOM: out of memory

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| OOM-01 | executor OOM during shuffle | shuffle partition too large | AQE on; repartition on a finer key; classic: raise `shuffle.partitions` |
| OOM-02 | executor OOM during broadcast join | broadcast side too large | drop the hint; classic: lower `autoBroadcastJoinThreshold` |
| OOM-03 | driver OOM on `collect()` / `toPandas()` | too much data to driver | `.limit()`; aggregate in Spark; write to a table |
| OOM-04 | GC overhead limit exceeded | object churn from UDFs or huge plans | native functions; split the plan |
| OOM-05 | OOM during `explode()` | arrays with extreme cardinality | pre-filter; `posexplode` in batches |
| OOM-06 | container killed (exit 137) | memory above container limit (classic) | larger node or `memoryOverhead`; serverless: reduce per-task data |

## SHF: shuffle failures

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| SHF-01 | `FetchFailedException` | executor died mid-shuffle | check skew; classic: more memory |
| SHF-02 | shuffle read timeout | slow I/O or network | retry; reduce shuffle volume (project columns early) |
| SHF-03 | `MetadataFetchFailedException` | driver overloaded by shuffle metadata | fewer partitions; classic: driver memory |
| SHF-04 | repeated retries on one partition | data skew | AQE skew join; salt key |

## SKW: data skew

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| SKW-01 | one task 50x slower than median | hot key in join or groupBy | salt; broadcast small side |
| SKW-02 | spill on specific tasks | skewed partition | AQE skew join; finer key |
| SKW-03 | stragglers in a stage | uneven distribution | repartition on a better key |
| SKW-04 | one executor OOM, rest idle | NULL keys land in one partition | filter or handle NULL keys separately |

Diagnostic:
```python
from pyspark.sql.functions import col, count, lit
df.groupBy("join_key").agg(count(lit(1)).alias("n")).orderBy(col("n").desc()).show(20)
```

## CLU: cluster and infrastructure (classic compute)

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| CLU-01 | `ExecutorLostFailure` (-100) | spot instance reclaimed | on-demand for critical jobs; or serverless |
| CLU-02 | cluster start timeout | cloud quota | different zone; serverless |
| CLU-03 | all executors die at start | init script or image failure | pin versions; check init logs |
| CLU-04 | `Py4JNetworkError` / JVM crash | library conflict | remove conflicting JARs |
| CLU-05 | autoscale not adding workers | max workers or quota | raise limits |

## SCH: schema and data

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| SCH-01 | `cannot resolve column` | upstream rename or drop | check contract and `de-data-contract` impact |
| SCH-02 | `ClassCastException` / `NumberFormatException` | source type changed silently | explicit schema; `_rescued_data` check |
| SCH-03 | `mergeSchema` conflict | same column, different types across files | fix source; cast before merge |
| SCH-04 | `NullPointerException` in transform | unexpected NULL | expectation plus null guards |
| SCH-05 | `CorruptRecordException` | malformed JSON / CSV | Auto Loader `rescuedDataColumn`; quarantine |
| SCH-06 | `ConcurrentAppendException` / `ConcurrentModificationException` | two writers on the same table | single writer per table; job `max_concurrent_runs: 1`; retry with backoff |

## NET: connectivity

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| NET-01 | JDBC timeout | database overloaded or firewall | partitioned reads; Lakeflow Connect instead of JDBC |
| NET-02 | storage 401 / 403 | credential or external location missing | UC external location and storage credential |
| NET-03 | DNS failure | private link misconfigured | network team |
| NET-04 | TLS handshake failure | certificate | update CA store |
| NET-05 | 429 throttling | too many API calls | backoff; lower parallelism |

## CFG: configuration

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| CFG-01 | `ClassNotFoundException` | missing library | declare in bundle / pipeline environment |
| CFG-02 | behaviour changed after runtime upgrade | breaking change | pin runtime; read release notes |
| CFG-03 | slow with no errors | bad partition count (classic) | AQE auto |
| CFG-04 | works in dev, fails in prod | config mismatch | `de-release-gate` prod checks |
| CFG-05 | `IllegalArgumentException` on a config key | typo | verify key |

## LGC: logic and correctness

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| LGC-01 | duplicate rows | non-idempotent append; missing dedup | AUTO CDC by key and sequence; streaming table |
| LGC-02 | missing rows | inner join or over-filter | left join; review filters |
| LGC-03 | row count multiplied | many-to-many join | dedup one side; verify grain |
| LGC-04 | aggregates off | fan-out before aggregation | aggregate first |
| LGC-05 | timestamps shifted | implicit time zone | store UTC; `spark.sql.session.timeZone` |
| LGC-06 | NULL where values expected | key type mismatch | cast keys before join |

## PRM: permissions

| Id | Symptom | Root cause | Fix |
|---|---|---|---|
| PRM-01 | `PERMISSION_DENIED` on Unity Catalog object | missing `USE CATALOG` / `USE SCHEMA` / `SELECT` / `MODIFY` / `CREATE TABLE` | grant to the run-as principal |
| PRM-02 | cannot read external location | no `READ FILES` | grant on external location |
| PRM-03 | secret scope access denied | scope ACL | grant `READ` on scope |

## Universal steps

1. Read the full stack trace bottom-up; the real cause is after the last `Caused by:`.
2. Pipelines: event log first, Spark UI second.
3. `df.explain("formatted")` shows shuffles, broadcasts and skew candidates.
4. Reproduce on a small slice before changing anything.
