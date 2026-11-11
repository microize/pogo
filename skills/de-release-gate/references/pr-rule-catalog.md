# PR rule catalog (data engineering on Databricks)

Severity: Blocker (BLOCK), Major (counts toward REQUEST_CHANGES), Minor (comment only). "Advisory" below means Major, "Note" means Minor.

## 1. Anti-patterns (see de-run-diagnose/references/anti-pattern-catalog.md)

| Id | Trigger | Severity |
|---|---|---|
| AP-01 / AP-02 | `collect()` / `toPandas()` without a size guard | Blocker |
| AP-04 | row-by-row iteration | Blocker |
| AP-03 | Python UDF where a native function exists | Advisory |
| AP-13 | `coalesce(1)` on large output | Blocker |
| AP-16 | new table with `partitionBy` or ZORDER instead of liquid clustering | Advisory |
| AP-17 | hand-written MERGE for SCD where AUTO CDC fits | Advisory |
| AP-19 | stateful stream without watermark | Blocker |
| AP-20 | SQL built with f-strings from input | Blocker |
| AP-99 | `DROP TABLE` / `DROP SCHEMA` / `bundle destroy` in prod-path code | Blocker |
| cross join | without an explicit comment justifying it | Blocker |
| bare `except:` | swallows errors | Advisory |

## 2. Schema-breaking changes (de-data-contract/references/breaking-change-catalog.md)

| Trigger | Severity |
|---|---|
| column removed, renamed, type narrowed, key or sequence changed, SCD type changed, grain changed | Blocker |
| NOT NULL added without backfill | Blocker |
| nullable column added | Note |
| any breaking change without an impact report and contract bump | Blocker |

## 3. Tests

| Trigger | Severity |
|---|---|
| new or changed transformation without a unit or pipeline test | Blocker |
| new DQ rule without a test or expectation metric check | Blocker |
| bug fix without a regression test | Advisory |
| Spark tests not run on Databricks compute (notebook cell or job task) | Advisory |

## 4. Data quality

| Trigger | Severity |
|---|---|
| new silver or gold table without completeness and uniqueness rules | Blocker |
| ingestion without explicit schema or rescued data column | Advisory |
| Critical rule implemented as `expect` (warn) only | Blocker |

## 5. Hard-coded values

| Trigger | Severity |
|---|---|
| literal catalog or schema (`prod.`, `dev_x.`) in pipeline code | Blocker |
| absolute paths, personal workspace paths | Blocker |
| dates and thresholds inline | Advisory |
| magic repartition numbers | Advisory |

## 6. Logic

| Trigger | Severity |
|---|---|
| non-idempotent write (append without key or dedup) | Blocker |
| implicit time zone handling | Advisory |
| business logic in bronze | Advisory |
| `replaceWhere` missing on partition overwrite in Jobs | Blocker |

## 7. Security

| Trigger | Severity |
|---|---|
| credential, token (`dapi...`), connection string in code or config | Blocker and rotate |
| PII printed or logged | Blocker |
| `.env` or `databrickscfg` committed | Blocker and rotate |
| grants to `account users` or `ALL PRIVILEGES` in scripts | Advisory |

## 8. Docs and method

| Trigger | Severity |
|---|---|
| schema change without contract changelog | Blocker |
| commit not tied to a task id in `tasks.md` | Advisory |
| table not in the approved spec | Blocker |
| new public function without docstring | Note |

## Disposition

| Blockers | Advisories | Verdict |
|---|---|---|
| 0 | 0 to 3 | APPROVE |
| 0 | 4 or more | REQUEST_CHANGES |
| 1 or more | any | BLOCK |
| any secret | any | BLOCK and rotate |
