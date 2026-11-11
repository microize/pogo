# DQ severity and rule reference

## Severity

| Severity | Meaning | Pipeline action | Alert |
|---|---|---|---|
| Critical | data corrupt or unusable; key violation; schema break | `expect_or_fail` / fail the job task | on-call |
| Warning | degraded but usable | `expect_or_drop` to quarantine, or keep and count | team channel |
| Low | cosmetic | `expect` (count only) | daily digest |

## Field type to severity

| Field type | Completeness | Uniqueness | Validity |
|---|---|---|---|
| Primary / natural key | Critical, 100 percent | Critical at grain | Critical format |
| Foreign key | Critical, 100 percent (or mapped to the Unknown row) | n/a | Critical: exists in parent |
| Business required | Warning, at least 95 percent | context | Warning |
| Optional | Low | n/a | Low if present |
| Sequence column for AUTO CDC | Critical NOT NULL, sortable | n/a | Critical |

## Layer to strictness

| Layer | Completeness | Uniqueness | Schema | Freshness |
|---|---|---|---|---|
| bronze | log only; count `_rescued_data` | log duplicates | warn on drift, keep `_rescued_data` | relaxed |
| silver | enforce keys; drop or quarantine bad rows | dedup required; AUTO CDC handles by key and sequence | enforced | enforce SLA |
| gold | 100 percent on keys and measures | strict at grain | strict | strict SLA |

## Rule families and how to express them on Databricks

| Family | Prefix | Expectation form | Post-load SQL form |
|---|---|---|---|
| Completeness | CMP | `expect_or_fail("cmp_01", "order_id IS NOT NULL")` | `SELECT count(*) FROM t WHERE order_id IS NULL` = 0 |
| Uniqueness | UNQ | private incremental MV counting duplicates per key plus `expect_or_fail("no_dups", "dup_count = 0")` (official aggregate-expectation pattern) | `SELECT k, count(*) FROM t WHERE __END_AT IS NULL GROUP BY k HAVING count(*) > 1` = 0 rows |
| Validity (range, format, enum) | RNG | `expect_or_drop("rng_01", "amount BETWEEN 0 AND 1e6")`, `status IN (...)`, `email RLIKE '...'` | same predicate as a count |
| Referential | REF | private MV with the orphan count plus `expect_or_fail`; row-level `expect("ref_01", "customer_id IS NOT NULL")` | `LEFT ANTI JOIN` orphan count = 0 (or mapped to Unknown row) |
| Freshness | FRS | private MV with `max(event_ts)` plus `expect_or_fail` (does not gate other flows) | `SELECT max(event_ts) FROM t` within SLA; SQL alert |
| Schema | SCH | `expect("sch_01", "_rescued_data IS NULL")` | compare `information_schema.columns` with the contract |
| Volume / anomaly | THR | private MV with a windowed count plus `expect_or_fail` | Data Profiling (formerly Lakehouse Monitoring) or SQL alert against a 30-day band |
| Consistency | CON | `expect("con_01", "ship_date >= order_date")` | cross-table reconciliation query |

## Threshold guidance

- Start at 2 sigma over a 30-day rolling baseline; gold 1 sigma; bronze 3 sigma or log only.
- Row-count anomaly: flag a drop over 20 percent or a spike over 50 percent day over day.
- Null-rate anomaly: flag an increase over 5 percentage points.

## Reading expectation metrics from the event log

```sql
SELECT timestamp,
       details:flow_progress.data_quality.expectations AS expectations
FROM event_log('<pipeline-id>')
WHERE event_type = 'flow_progress'
  AND details:flow_progress.data_quality IS NOT NULL
ORDER BY timestamp DESC LIMIT 50;
```
