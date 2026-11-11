# Compute sizing: <name>

Status: DRAFT | ACCEPTED (by <email>, <YYYY-MM-DD>) | By: <email> | Date: <YYYY-MM-DD HH:MM> (from `current_timestamp()`)
Compute: <cluster id / job id / warehouse id / pipeline id> | Type: serverless | job cluster | all-purpose | SQL warehouse | pipeline
Runs judged: <n> runs, <from> to <to> | Environment record: `specs/env/<env>-<team>.md` | Prices: `de-cost` file <date>

## 1. Workload

| Item | Value |
|---|---|
| Language and APIs | |
| Batch / streaming, latency need | |
| Data per run, growth | |
| Shape (wide joins, aggregations, MERGE, UDFs, ML) | |
| Schedule, concurrency, deadline | |

## 2. Current configuration and runtime

| Setting | Value | Note (end of support, LTS, policy) |
|---|---|---|

## 3. Evidence

| Signal | Value | Query / source | Verdict |
|---|---|---|---|
| avg / p95 worker CPU | | C2 | |
| max memory, swap | | C2 | |
| CPU wait | | C2 | |
| driver load | | C2 | |
| spill, queue, start-up, pruning | | Q1 | |
| jobs on all-purpose compute | | J1 | |
| cost per run (DBUs, USD list) | | B1, `de-cost` | |

Confidence: high (3+ representative runs) | early signal (fewer). Thresholds marked kit heuristic: <list>.

## 4. Recommendation

| Setting | Now | Proposed | Why (evidence) | Expected effect (time, cost per run) |
|---|---|---|---|---|

Second-best option and when it would win: <one line>. Code issues to fix first (`de-run-diagnose`): <list or none>.

## 5. How it is applied (never by the agent)

Where: bundle `resources/<file>.yml` via a `small` track | cluster policy (admin) | warehouse setting (owner).
Rollback: <previous values>. Verify after: same queries on the next <n> runs.
