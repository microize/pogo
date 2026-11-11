# Spec: <track title>

Status: DRAFT
Type: full
Version: 1
Owner team: <team> (contact: <channel>)
Track id: <shortname>_<YYYYMMDD>
Context: greenfield | brownfield
Owner: <email>
Related tracks: -

Header lines are literal and machine-checked. Status values: DRAFT | IN_REVIEW | APPROVED (by <email>, <YYYY-MM-DD>) |
IN_PROGRESS | BLOCKED | ON_HOLD | COMPLETE | ABANDONED | SUPERSEDED. Type: full | small | hotfix (minimums in tasks.md).

## 1. Goal (2 to 3 sentences)

What business outcome this delivers and for whom.

## 2. Context

- Existing state (brownfield: what exists today, link `specs/project-profile.md`).
- Constraints inherited from the project (naming, catalogs, compute, deployment).

## 2b. Decisions

Decisions file: `specs/<track_id>/decisions.md` (rounds completed: <n>) or "chat interview".

## 3. Sources

| Source | Type | Format / interface | Delivery | Keys | Sequence column | Notes |
|---|---|---|---|---|---|---|
| orders_cdc | CDC feed | Kafka JSON | continuous | order_id | event_ts | deletes as op='D' |

## 4. Targets

| Table (catalog.schema.table) | Layer | Object type | Grain (one row per) | Keys | History | Clustering |
|---|---|---|---|---|---|---|
| `${catalog}.silver_sales.orders` | silver | streaming table + AUTO CDC | order | order_id | SCD2, track all except updated_at | AUTO |

## 4b. Entities and dimension candidates (warehouse tracks)

| Entity | Grain | Keys | Source | Dimension or fact | Kept (Y/N, per decisions) |
|---|---|---|---|---|---|

## 5. Transformation rules

One block per rule, numbered. Edge cases are part of the rule.

```
T-01: normalize order status
  Input:      bronze.orders.status
  Logic:      upper(trim(status)) mapped through ref.order_status_map; unmapped -> 'UNKNOWN'
  Output:     silver.orders.order_status STRING NOT NULL
  Edge cases: NULL -> 'UNKNOWN'; trailing spaces; mixed case
```

## 6. History and change handling

- SCD type per target (1, 2, bitemporal, append-only).
- Delete handling (`apply_as_deletes`), truncate handling, late-arriving data, out-of-order sequence.

## 7. Data quality expectations

| Name | Rule | Action (warn / drop / fail) | Target |
|---|---|---|---|
| valid_order_id | `order_id IS NOT NULL` | fail | silver orders |

## 8. Latency, schedule, mode

- Pipeline mode: triggered \| continuous \| real-time. Schedule / trigger. SLA.

## 9. Non-functional

- Compute: serverless (default) \| classic (why). Expected volume. Cost ceiling. Retention.
- Environments and deployment: bundle targets, run-as identity, who deploys from the Git folder Deployments panel.

## 10. Governance and security

- PII columns and masking / row filters. Grants. Delta Sharing. Audit requirements.

## 11. Consumers

- Who reads the gold objects and how (AI/BI dashboard, metric view, downstream pipeline, app, ML).

## 12. Out of scope

- Explicit list.

## 12b. Known test gaps

| Behaviour | Why the test data cannot show it | Plan (fixture id / accepted risk) |
|---|---|---|

## 13. Assumptions and open questions

- `[ASSUMED]` items the user did not answer, with the default taken.
- Open questions that do not block approval.

## 14. Alternatives considered

- One line each: option, why not chosen (or "ask de-advisor for a full comparison").

## 14b. Requirement traceability

Every KPI, measure or business question from the request maps to a deliverable. An unmapped row is a spec gap.

| # | Business requirement / KPI | Source (quote from request) | Deliverable | Table.column | Status |
|---|---|---|---|---|---|
| R1 | | | gold MV | | mapped / GAP |

## 15. Acceptance criteria (each one runnable)

| # | Check | Command / query | Expected |
|---|---|---|---|
| AC1 | Row count matches source | `SELECT count(*) FROM ... WHERE __END_AT IS NULL` | equals source current count |
| AC2 | One current row per key (SCD2 targets; else one row per key) | `SELECT order_id, count(*) ... WHERE __END_AT IS NULL GROUP BY order_id HAVING count(*) > 1` | 0 rows |
| AC3 | Bundle deploys to dev | user-run: Deployments panel > deploy target `dev` (deploy validates first) | deployment succeeds |
| AC4 | Re-run gives the same result | run twice on the same input; compare `count(*)` and a column checksum per target | identical |
| AC5 | No rows lost (where a quarantine exists) | `count(bronze)` vs `count(silver) + count(quarantine)` for the same load | equal |
## 15b. Unchanged behaviour (hotfix tracks)

What the fix must not change, each with a query run before and after the fix.

| # | Behaviour | Query | Before | After |
|---|---|---|---|---|

## 16. Decision log

| Date | Decision | Why / verbatim | By |
|---|---|---|---|
| <date> | Spec v1 approved | user reply, verbatim: "<paste>" | <email> |
| | Goldfish review 1 resolved / skipped by user | | |
