# Runtime versions and the code that fits them

Checked **2026-11-12**. Sources: Databricks Runtime release notes `[RT]` (docs.databricks.com/aws/en/release-notes/runtime/
and the per-version pages), serverless release notes and environment versions `[SL]`, Databricks SQL release notes
`[DBSQL]`, Databricks SQL function pages `[FN]`, Apache Spark release notes `[S-x]` (spark.apache.org/releases/),
the Spark SQL and PySpark migration guides `[SMG]` / `[PMG]`, the Spark SQL function "Since" fields `[SF]` (full list:
`spark-functions-since.md`) and PySpark API pages `[PY]`. Items marked **unverified** were not confirmed on a page.
Recheck when this date is older than 90 days or a runtime is not listed: add nothing from memory.

## 1. Databricks Runtime map `[RT]`

| DBR | LTS | Apache Spark | Python | Scala | JDK | Released | End of support |
|---|---|---|---|---|---|---|---|
| 19 | no | 4.2.0 | 3.12.3 | 2.13.18 | 21 only | 2026-07-23 | set at LTS transition |
| 18 LTS | yes (since 2026-07-23) | 4.1.0 | 3.12.3 | 2.13.16 | 21 | 2026-06-10 | 2029-06-10 |
| 17.3 LTS | yes | 4.0.0 | 3.12.3 | 2.13.16 | 17 | 2025-10-22 | 2028-10-22 |
| 16.4 LTS | yes | 3.5.2 | 3.12.3 | 2.12.15 or 2.13.10 | 17 | 2025-05-09 | 2028-05-09 |
| 15.4 LTS | yes | 3.5.0 | 3.11 | 2.12.15 | 8 | 2024-08-19 | 2027-08-19 |
| 14.3 LTS | yes | 3.5.0 | 3.10.12 | 2.12.15 | 8 | 2024-02-01 | **2027-02-01** |

DBR 17 and later: Scala 2.13 only. Apache Spark 4.3.0 (2026-10-30) is in no DBR yet; DBR 19 already carries a few
4.3 functions (`collect_union`, `variant_strip_nulls`). Production classic compute: latest LTS (18 LTS today); flag
anything within 6 months of end of support (14.3 LTS ends 2027-02-01).

## 2. Serverless and SQL warehouses

| Serverless env | Python | Databricks Connect | Released | End of support |
|---|---|---|---|---|
| 1 | 3.10.12 | 14.3.7 | 2024-03-12 | 2027-03-12 |
| 2 | 3.11.10 | 15.4.5 | 2024-11-21 | 2027-11-21 |
| 3 | 3.12.3 | 16.4.2 | 2025-06-13 | 2028-06-13 |
| 4 | 3.12.3 | 17.3.2 | 2025-08-13 | 2028-08-13 |
| 5 | 3.12.3 | 18 | 2026-02-25 | 2029-02-25 |
| 6 | 3.12.3 | 19 | 2026-09-03 | 2029-09-03 |

- The environment version pins the **client** (Python, packages, Databricks Connect); the serverless engine follows
  current DBR releases `[SL]`. The Spark API level a job can use is bounded by its Databricks Connect version
  (14.3 → 3.5, 17.3 → 4.0, 18 → 4.1, 19 → 4.2: **unverified** mapping). New jobs: the latest environment.
- DataFrame caching on serverless is Public Preview (2026-10-23) and needs environment 5 or later.
- SQL warehouses: channel Current = DBSQL 2026.44, Preview = 2026.45 `[DBSQL]`; the Spark version behind DBSQL is
  **unverified**; treat a Current warehouse as at least the latest GA DBR for function availability, and check the
  function page's "Applies to" line when it matters.
- Photon: always on for serverless, SQL warehouses and serverless pipelines; on by default for classic. Not used for
  UDFs, RDD / Dataset code or stateful streaming; unsupported operators fall back to Spark.

## 3. What each Spark version adds that changes the code you should write

| Spark (DBR) | Use when available | Watch out |
|---|---|---|
| 3.3 (11.3+ / 12.2) | `try_sum`, `try_avg`, `try_element_at`, `try_to_number`, `array_size`, `split_part`, `contains`, `startswith`, `endswith`, `ilike`, `map_contains_key`, `withColumns`, `observe`, `mapInArrow` | |
| 3.4 (13.3 LTS) | lateral column alias, parameterized `spark.sql(q, args=)`, `GROUP BY ALL`, `UNPIVOT`, `OFFSET`, column `DEFAULT`, `TIMESTAMP_NTZ`; `any_value`, `median`, `mode`, `regexp_count` / `_instr` / `_substr`, `to_char`, `try_to_timestamp`, `url_decode`, `mask`, `convert_timezone`; `unpivot` / `melt`, `withColumnsRenamed` | `Trigger.Once` deprecated (use `AvailableNow`); `to_binary` / `unbase64` raise on bad input |
| 3.5 (14.3 LTS, 15.4 LTS, 16.4 LTS) | Arrow-optimized Python UDFs (`useArrow=True`, opt-in), Python UDTFs, `IDENTIFIER`, positional parameters, named arguments, `dropDuplicatesWithinWatermark`, HLL sketches (`hll_sketch_agg` ...), bitmap functions, `to_varchar`; Python wrappers for `count_if`, `percentile`, `try_divide`, `split_part`, `regexp_extract_all` | Python 3.7 removed |
| 4.0 (17.3 LTS) | VARIANT (`parse_json`, `try_parse_json`, `variant_get`), collations (`COLLATE UTF8_LCASE`), pipe syntax `\|>`, session variables, SQL UDFs, Python Data Source API, `transformWithState(InPandas)`, `applyInArrow`, `listagg` / `string_agg`, `percentile_cont` / `_disc`, more `try_*` (`try_url_decode`, `try_parse_url`, `try_mod`, `try_make_timestamp`), `zeroifnull`, `nullifzero` | **ANSI on by default**: casts, division, overflow and bad input now raise; Python 3.8, JDK 8/11, Scala 2.12 removed; deprecated pandas-on-Spark APIs removed; `functions import *` no longer exports `DataFrame` / `Column` / types; `CREATE TABLE` without `USING` follows `spark.sql.sources.default`; pandas 2.0+ and PyArrow 11+ |
| 4.1 (18 LTS) | `arrow_udf` / Arrow UDTF, vectorized `udf` via type hints, SQL scripting on by default, VARIANT shredding, recursive CTE, `TIME` type, sketches `approx_top_k`, `kll_sketch_*`, `theta_*`, real-time streaming mode | Python 3.9 dropped; PyArrow 15+, pandas 2.2+; `BinaryType` maps to `bytes` |
| 4.2 (19) | **Arrow Python UDFs on by default**, `GEOMETRY` / `GEOGRAPHY` with `ST_*`, `QUALIFY`, `CHANGES` clause, metric views, `max_by` / `min_by` with k, `time_bucket`, `vector_*` (cosine similarity, distances), `IGNORE NULLS` on `array_agg` / `collect_list` | PyArrow 18+; on DBR 19: JDK 17 removed, about 90 preinstalled Python packages removed (pin your own), `HAVING` evaluated before window functions with generators |
| 4.3 (no DBR yet) | `JSON_TABLE`, `ASOF JOIN` (off by default), `UNNEST`, `collect_union`, `jaro_winkler_similarity`, `variant_set` / `variant_insert` | Python 3.10 dropped |

## 4. Databricks features with a minimum runtime

| Feature | Minimum | Source |
|---|---|---|
| `_metadata.file_path` / `file_name` | DBR 10.5 | file metadata column page |
| `h3_*` | 11.3 LTS | `[FN]` |
| `MERGE ... WHEN NOT MATCHED BY SOURCE`, `INSERT ... REPLACE WHERE`, deletion vector reads | 12.2 LTS | merge-into, insert-into, deletion vectors pages |
| `INSERT BY NAME`, `read_files`, `IDENTIFIER`, optimized writes on UC | 13.3 LTS | insert-into, `[FN]`, identifier, tune-file-size pages |
| Python UDTF (Public Preview), deletion vector write optimizations | 14.3 LTS | python-udtf, deletion vectors pages |
| `MERGE WITH SCHEMA EVOLUTION` | 15.2 | merge-into page |
| `try_parse_json` 15.3; VARIANT, Python data sources, liquid clustering GA with `CLUSTER BY AUTO`, `ai_query` | 15.4 LTS | variant, datasources, clustering, `[FN]` |
| `OPTIMIZE FULL` 16.0; collations 16.1; `http_request`, pipe syntax, `transformWithState` 16.2; SQL scripting, `INSERT REPLACE USING` 16.3; `listagg` 16.4 | 16.x | respective pages |
| stored procedures 17.0; `st_*`, `INSERT REPLACE ON` 17.1; RocksDB state store with changelog checkpointing by default 17.3 LTS | 17.x | scripting, `[FN]`, `[RT 17.3]` |
| `INSERT ... WITH SCHEMA EVOLUTION` 18.1; UC Python UDTF, `max_by` / `min_by` with limit, `parse_timestamp` | 18 | insert-into, python-udtf, `[RT 18]` |
| Arrow Python UDFs default (roll back: `spark.databricks.execution.pythonUDF.arrow.enabled=false`), `collect_union`, `parse_sql`, `trim_array` | 19 | `[RT 19]` |

`QUALIFY` and `approx_top_k`: listed in the DBR 18 notes and in Apache Spark 4.2, but Databricks SQL may have had them
earlier: check the function or clause page's "Applies to" line before saying a runtime lacks them (**unverified**).

## 5. Breakers: code that stops working or behaves differently

| Code | Breaks on | Do instead |
|---|---|---|
| `input_file_name()` | unsupported on DBR 17.3 LTS and later and on DBSQL (deprecated since 13.3) | `col("_metadata.file_path")` / `_metadata.file_name` |
| implicit casts, `/` by zero, overflow, bad date strings | ANSI default: Spark 4.0 / DBR 17.3+, and serverless | fix the data, or `try_cast`, `try_divide`, `try_to_date` / `try_to_timestamp` where NULL is the wanted result |
| RDD (`.rdd`, `sc.parallelize`, `mapPartitions` on RDD), `sparkContext`, `sqlContext` | serverless and Standard access mode (Python `sc` only from 14.0 on Standard; Scala never) | DataFrame API, `mapInArrow`, `mapInPandas` |
| `.cache()`, `.persist()`, `CACHE TABLE`, `checkpoint()`, global temp views, `${var}` substitution, Hive SerDe | serverless (caching: Public Preview on env 5+) | write an intermediate table or temporary view; parameters |
| `trigger(once=True)`, `processingTime`, continuous triggers | serverless jobs (Once deprecated since 3.4) | `trigger(availableNow=True)`; continuous work in a continuous pipeline or job |
| `spark.conf.set` for executors, memory, shuffle | serverless (most configs rejected) | remove; fix the query or move to classic |
| deprecated pandas-on-Spark APIs (`iteritems`, `append`, `mad`, `Int64Index`, `to_koalas`) | Spark 4.0 / DBR 17.3+ | the pandas 2 equivalents |
| `from pyspark.sql.functions import *` expecting `DataFrame`, `Column`, types | Spark 4.0+ | explicit imports |
| `from pyspark.sql.functions import max, min, sum, round, abs, filter` | any (shadows Python builtins) | `import pyspark.sql.functions as F` |
| `LATERAL VIEW explode(...)` | deprecated since DBR 12.2 | `FROM t, explode(...)` |
| preinstalled packages (plotly, seaborn, openai, psycopg2, pyodbc ...) | DBR 19 | declare and pin them in the environment |
| Python 3.9 code paths, PyArrow under 15 | Spark 4.1 / DBR 18 | Python 3.12 runtime, current PyArrow |
| R, SparkR | SparkR deprecated in Spark 4.0; R not on serverless | Python or SQL; R only on Dedicated classic |

## 6. Replacement table (use, avoid, gain by upgrading)

| If the code does | Use instead | From | Why |
|---|---|---|---|
| a row-at-a-time Python `@udf` | a native function first; else an Arrow UDF (`useArrow=True`, 3.5 / DBR 14.3) or `arrow_udf` (4.1 / DBR 18); default Arrow on DBR 19 | 3.5 | vectorized transfer; native functions also run in Photon |
| `pandas_udf` / `applyInPandas` doing Arrow-friendly work | `arrow_udf`, `applyInArrow` | 4.0 / 4.1 | skips pandas conversion |
| `explode` + `groupBy` to rebuild arrays | `transform`, `filter`, `aggregate`, `exists`, `forall` | 2.4 / 3.0 | no shuffle |
| casts or parsing on dirty data | `try_*` functions | 3.2 to 4.0 | no failures under ANSI, explicit NULLs |
| `from_json` with a hand-kept schema for changing JSON | VARIANT with `parse_json` / `variant_get` | DBR 15.4 / Spark 4.0 | no schema maintenance; shredded storage from 4.1 |
| `collect_list` + `concat_ws` | `listagg` / `string_agg` | DBR 16.4 / 4.0 | one ordered aggregate |
| window `row_number()` then filter in a subquery | `QUALIFY` (see section 4 note) or `max_by` / `min_by` | 3.0 / 4.2 | no extra subquery; single aggregate |
| exact `percentile` / `median` on large data | `percentile_approx`; `kll_sketch_*` | any / 4.1 | bounded memory |
| `distinct().count()` on large data | `approx_count_distinct`; `hll_sketch_agg` for mergeable counts | any / 3.5 | no full shuffle |
| `lower(a) = lower(b)` | `COLLATE UTF8_LCASE` | DBR 16.1 / 4.0 | native case-insensitive comparison |
| chained `withColumn` / `withColumnRenamed` | `withColumns` / `withColumnsRenamed` | 3.3 / 3.4 | smaller plans |
| manual unions to unpivot | `unpivot` / `melt` | 3.4 | native |
| f-string SQL | `spark.sql(q, args=...)`, `IDENTIFIER(:t)` | 3.4 / DBR 13.3 | injection-safe, plan reuse |
| `PARTITIONED BY` / `ZORDER` on new tables | `CLUSTER BY AUTO` | DBR 15.4 LTS | layout managed for you |
| scheduled `OPTIMIZE` / `VACUUM` / `ANALYZE` on UC managed tables | predictive optimization | UC managed | automatic |
| `repartition(n)` / `coalesce(n)` before a Delta write | optimized writes (default on UC) | DBR 13.3 LTS | fewer tiny or giant files |
| `DELETE` then `INSERT` of a slice | `INSERT ... REPLACE WHERE` / `REPLACE USING` / `REPLACE ON` | 12.2 / 16.3 / 17.1 | atomic |
| `MERGE` then a separate delete of rows gone from the source | `WHEN NOT MATCHED BY SOURCE` | 12.2 LTS | one pass |
| `ALTER` to add columns before `MERGE` | `MERGE WITH SCHEMA EVOLUTION` | 15.2 | simpler |
| `flatMapGroupsWithState` / `applyInPandasWithState` | `transformWithState` / `transformWithStateInPandas` | DBR 16.2 / 4.0 | recommended state API, TTL, multiple state variables |
| `dropDuplicates` on a stream | `dropDuplicatesWithinWatermark` | 3.5 | bounded state |
| HDFS-backed state store | RocksDB with changelog checkpointing | default 17.3 LTS | faster checkpoints |
| `collect()` loop issuing a query per row | a set-based join or `MERGE`; SQL scripting for control flow | any / 16.3 | no driver bottleneck |
| `union` of mismatched schemas | `unionByName(allowMissingColumns=True)` | 3.1 (**unverified** version) | correctness |
| deep nested CTEs | pipe syntax `\|>` | DBR 16.2 / 4.0 | readability only, no speed claim |

## 7. Upgrade arguments by step (summary for "what would we gain")

| From | To | Main gains for typical ETL | Main work |
|---|---|---|---|
| 14.3 LTS (Spark 3.5) | 16.4 LTS (3.5) | collations, `listagg`, pipe syntax, `transformWithState`, SQL scripting, `REPLACE USING`, VARIANT and liquid clustering GA (from 15.4) | low: same Spark line; 14.3 support ends 2027-02-01 |
| 16.4 LTS (3.5) | 17.3 LTS (4.0) | `input_file_name` replacement forced, RocksDB default, stored procedures, `st_*` | **ANSI default**, Scala 2.13 only, pandas-on-Spark removals, `input_file_name` gone: test in dev with invariants |
| 17.3 LTS (4.0) | 18 LTS (4.1) | `arrow_udf`, SQL scripting GA, VARIANT shredding, sketches, `max_by` with limit, `INSERT WITH SCHEMA EVOLUTION` | JDK 21, Python 3.10+, PyArrow 15+ |
| 18 LTS (4.1) | 19 (4.2) | Arrow UDFs by default, `QUALIFY`, geospatial types, vector functions | not LTS; JDK 17 removed; about 90 preinstalled packages removed |

Test plan for any step: same input in dev on the target runtime, compare row counts, key uniqueness and column
checksums (`de-quality-testing` invariants) and run time (`de-run-diagnose`) before proposing it for prod.
