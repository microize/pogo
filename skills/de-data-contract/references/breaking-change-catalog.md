# Breaking change catalog (Databricks / Delta, 2026)

Shared by `de-data-contract` (both modes) and `de-release-gate`.

## Classification

| Change | Breaking? | Migration | Risk | Databricks note |
|---|---|---|---|---|
| Add nullable column | No | None | Low | consumers using `SELECT *` into fixed schemas may still break; flag them |
| Add non-nullable column | **Yes** | Backfill then `SET NOT NULL` | High | `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL` fails if NULLs exist |
| Remove column | **Yes** | Consumer code update | High | needs column mapping (`delta.columnMapping.mode = name`); data stays until VACUUM |
| Rename column | **Yes** | Alias view or consumer update | High | column mapping required; lineage shows old name in history |
| Widen type (INT to BIGINT, DECIMAL scale up) | No | Validate downstream casts | Medium | Delta type widening supported; enable `delta.enableTypeWidening` |
| Narrow type | **Yes** | Rewrite | Critical | data loss risk |
| Change key columns | **Yes** | Re-key and reprocess; AUTO CDC target needs full refresh | Critical | |
| Change sequence column of AUTO CDC | **Yes** | Full refresh of target | Critical | history order changes |
| Change SCD type (1 to 2 or back) | **Yes** | New target table, backfill | Critical | `__START_AT` / `__END_AT` appear or disappear |
| Add enum value | No | Validate consumer handling | Low | |
| Remove enum value | **Yes** | Consumer fallback | High | |
| Change clustering columns | No | `OPTIMIZE` rewrites lazily | Low | liquid clustering replaces partition changes; `ALTER TABLE ... CLUSTER BY` |
| Change partition columns (legacy tables) | **Yes** | Full rewrite | Critical | prefer migrating to liquid clustering |
| Add CHECK constraint | **Yes** if existing rows violate | Clean data first | High | enforced on write |
| Remove constraint | No | None | Low | |
| Change grain of a gold table | **Yes** | New table, deprecate old | Critical | every consumer aggregation changes |
| Change time zone semantics of a timestamp | **Yes** | Backfill | High | document in contract |
| Change refresh schedule / SLA | Depends | Notify consumers | Medium | freshness contract clause |

## Versioning

- **Major**: any breaking change above.
- **Minor**: additive changes (nullable column, enum value, new table).
- **Patch**: descriptions, comments, tags, owner changes.

## Compatibility modes

| Mode | Rule | Use when |
|---|---|---|
| Backward | new schema reads old data | default; consumers upgrade at their pace |
| Forward | old schema reads new data | producers may roll back |
| Full | both | regulated domains |
| None | no guarantee | internal staging only |

## Decision tree

```
Removed, renamed, narrowed, re-keyed, re-sequenced, grain changed?
  yes -> BREAKING (major)
  no  -> non-nullable column added, or constraint added over dirty data?
           yes -> BREAKING (major, backfill first)
           no  -> additive? -> minor. docs only? -> patch.
```
