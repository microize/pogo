# Decisions: <track_id>

How this works: the agent writes questions here with a proposed default; you edit the **Answer** column
(or leave the default), add notes, then tell the agent `done`. The agent appends later rounds below.
Never overwrite earlier rounds. Maximum 5 rounds; unanswered items become `[ASSUMED]` in the spec.

## Round 1 (broad)

| # | Question | Options (recommended first) | Answer | Notes |
|---|---|---|---|---|
| 1.1 | Sources and delivery | CDC feed \| snapshots \| append-only files \| Lakeflow Connect connector \| Zerobus | | |
| 1.2 | Target catalog and schemas | `<catalog>.<layer>_<domain>` | | |
| 1.3 | History requirement | SCD2 \| SCD1 \| bitemporal \| append-only | | |
| 1.4 | Latency | triggered daily \| hourly \| continuous \| real-time | | |
| 1.5 | Environments and deployment | bundles with dev / prod, run-as service principal | | |

## Round 2 (tables, grain, dimensions)

Dimension candidates: every text, code, flag, date and geo field from the sources. Mark Include N to drop.

| Field | Source | Distinct values (approx) | Proposed as | Include (Y/N) | Notes |
|---|---|---|---|---|---|

| # | Question | Options | Answer | Notes |
|---|---|---|---|---|
| 2.1 | Fact tables and grain | | | |
| 2.2 | Keys per table | | | |
| 2.3 | Table names per layer | | | |

## Round 3 (quality, change handling, operations)

| # | Question | Options | Answer | Notes |
|---|---|---|---|---|
| 3.1 | Critical DQ rules (fail the update) | | | |
| 3.2 | Delete and late-arrival handling | | | |
| 3.3 | Alerting channel and SLA | | | |
| 3.4 | PII columns and masking | | | |
