# Modeling rules (Databricks lakehouse, dimensional gold)

## Layers and entities

| Layer | Holds | Modeling rule |
|---|---|---|
| bronze | raw records as received plus audit columns | no business keys enforced, no business logic |
| silver | one table per business entity at a stated grain | typed, deduplicated, conformed; SCD history lives here (AUTO CDC) |
| gold | facts and dimensions, metric views | star schema; consumption names; KPIs defined once |

## Grain and facts

- State the grain in words: "one row per order line per day". Every column depends on the full grain.
- Prove it: `SELECT count(*) = count(DISTINCT <grain cols>) FROM <table>` must be true.
- Fact types: **transaction** (one row per event), **periodic snapshot** (one row per entity per period, for balances
  and stock), **accumulating snapshot** (one row per process instance with milestone dates).
- Measures: additive (sum over all dimensions), semi-additive (balances: not over time), non-additive (ratios: store
  numerator and denominator, compute the ratio in a metric view).
- No NULL foreign keys: map unknown or late members to the unknown row (`-1`).

## Dimensions

- **Candidates**: every text, code, flag, date and geo field. Under about 10,000 distinct labelled values usually means
  its own dimension; high-cardinality identifiers stay on the fact as degenerate dimensions (order number).
- **Conformed**: one physical table and key shared by every fact that uses it; same attribute names and values.
- **Surrogate keys**: deterministic, for example `xxhash64(natural_key, version_start)`; never
  `monotonically_increasing_id()`. A version that starts and ends at the same instant must be dropped or the key
  repeats.
- **SCD per attribute group**: type 1 (overwrite) for corrections, type 2 (versions) for history that changes facts'
  meaning, type 0 for fixed attributes. SCD2 via AUTO CDC on the silver entity; the gold dimension is a view or MV with
  `valid_from`, `valid_to`, `is_current`.
- **Unknown row**: `sk = -1`, natural key `UNKNOWN`, fixed `valid_from` (for example 1900-01-01), `valid_to` NULL.
- **Role-playing**: one `dim_date`, used as order date, ship date... through views or aliased keys.
- **Junk dimension**: combine low-cardinality flags into one dimension instead of many tiny ones.
- **Point-in-time join** for SCD2: `fact.event_ts >= dim.valid_from AND (fact.event_ts < dim.valid_to OR dim.valid_to IS NULL)`.

## Physical design on Databricks

- Unity Catalog three-part names; catalog from configuration, never hard-coded in code.
- Informational constraints: `PRIMARY KEY` on dimension surrogate keys, `FOREIGN KEY` on facts (add `RELY` only when a
  validation query guarantees it).
- Layout: `CLUSTER BY AUTO` or explicit liquid clustering keys on large facts (common filter and join keys); no
  `PARTITIONED BY` or `ZORDER` on new tables.
- Comments on every table and column; PII columns tagged at bronze, hashed or masked by silver, none in gold.
- Metric views for shared KPIs (official `databricks-metric-views` skill).
- On classic compute materialized views recompute fully on each refresh (no serverless incremental refresh); keep gold
  MVs narrow or move heavy history to streaming tables.

## Validation queries (pass/fail)

| Check | Query shape |
|---|---|
| Grain | `count(*) = count(DISTINCT grain)` |
| Orphans | `SELECT count(*) = 0 FROM fact f LEFT ANTI JOIN dim d ON f.sk = d.sk` |
| Unknown share | `avg(CASE WHEN sk = -1 THEN 1 ELSE 0 END) <= <limit>` |
| One current row | `count(*) = count(DISTINCT natural_key)` where `is_current` |
| Conformance | the same natural key has the same attributes in every fact's view of the dimension |
| Reconciliation | `sum(measure)` in gold equals silver for the same grain and period |
| Fan trap | joining a fact to a one-to-many child does not change `sum(measure)` (compare before and after the join); otherwise aggregate the child first or use a bridge |
| Chasm trap | two facts sharing a dimension are never joined directly; each is aggregated to the shared grain, then combined |
| Mixed grain | no fact holds rows at two grains (e.g. order and order line): `count(DISTINCT grain) = count(*)` per load and one documented grain |
| Bridge weights | for weighted many-to-many bridges, `sum(weight) = 1` per group (tolerance 0.0001) |
| SCD2 overlap and gaps | per natural key, no two versions overlap and `valid_to` of one equals `valid_from` of the next |
| Inferred members | share of facts pointing at placeholder (late-arriving) dimension rows stays under the agreed limit, and placeholders are updated when the real row arrives |

## Review checklist

1. Every fact has a stated, proven grain and a fact type.
2. Every measure is classified by additivity.
3. Bus matrix complete; conformed dimensions shared, not duplicated.
4. Every dimension candidate has an Include Y/N decision from the user.
5. Surrogate keys deterministic; unknown row present; no NULL foreign keys.
6. SCD type chosen per attribute group with a reason.
7. Date dimension present; role-playing handled.
8. Physical names, types, nullability, constraints, clustering, comments, PII tags present.
9. Validation queries exist for every rule above.
10. Compute consequences from the Environment section considered (MV refresh, cluster time).
11. Join traps checked: no fan or chasm trap, no mixed grain, bridges weighted, SCD2 without overlaps or gaps.
12. Semantic hand-off present when people or Genie query the model: metric views with synonyms, keys (RELY only after
    checks), reviewed comments, certification plan, benchmark questions with expected SQL.
