# Model: <model name>

Status: DRAFT | Version: 1 | Owner: <email> | Date: <YYYY-MM-DD>
Catalog: `${catalog}` (dev value <catalog>) | Related track: <track id or none>

## 1. Business processes and questions

| Process | Questions / KPIs | Consumers | Latency |
|---|---|---|---|

## 2. Bus matrix

| Process (fact) | dim_date | dim_<a> | dim_<b> | ... |
|---|---|---|---|---|

## 3. Facts

| Fact | Type | Grain (one row per ...) | Grain proof (query, result) | Measures (additivity) | Foreign keys |
|---|---|---|---|---|---|

## 4. Dimension candidates

| Source field | Cardinality | Proposed dimension / role | Include Y/N (user) |
|---|---|---|---|

## 5. Dimensions

| Dimension | Natural key | Surrogate key | SCD per attribute group | Unknown row | Conformed with |
|---|---|---|---|---|---|

## 6. Physical model

| Table | Layer | Dataset type | Columns (type, null) | Constraints | Clustering | PII |
|---|---|---|---|---|---|---|

## 6b. Semantic hand-off

| Asset (metric view / table) | Measures or columns | Synonyms (max 10 per field) | Comment reviewed | Keys (PK / FK, RELY after checks) | Domain / tags | Certify at release |
|---|---|---|---|---|---|---|

Genie Agent (if a consumer): tables or metric views (about 5 max), join relationships without an FK, example SQL.

| Benchmark question | Expected SQL | Expected result shape |
|---|---|---|

## 7. Diagram

```mermaid
erDiagram
```

## 8. Validation queries (pass/fail)

| Check | Query | Expected |
|---|---|---|

## 9. Review and decision log

| Date | Decision | Why / verbatim reply | By |
|---|---|---|---|
