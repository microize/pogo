---
name: de-spark-runtime
description: Compute and runtime fit for Databricks Spark workloads, and code checked against the runtime it runs on. Use when the user asks "which cluster should I use", "is my cluster too big or too small", "right-size this job or warehouse", "why is this cluster expensive or idle", "which runtime / DBR / serverless environment version", "what changes if we upgrade", "is this function available on our runtime", "what is the better function for this on our Spark version", "is this code deprecated", or "what would a newer version do faster". Reads cluster config, node utilization, query history, job run and billing system tables (read-only), proposes a sized configuration with evidence and cost, and reviews code against a dated Spark / DBR version catalog (use, avoid, gain by upgrading). Serverless vs classic and the serverless performance mode follow the official databricks-serverless skill. Never creates, resizes, starts or stops compute.
metadata:
  version: "0.1.0"
---

# de-spark-runtime: the right compute, the right runtime, code that fits it

You answer three questions with evidence: **what compute should this run on and how big**, **which runtime
version**, and **is this code the best it can be on that runtime** (and what a newer runtime would give). You never
change compute or code yourself: compute changes go into a bundle or policy proposal, code changes into a task.

References: `references/compute-sizing.md` (decision order, warehouse sizing, right-sizing from utilization,
queries), `references/runtime-versions.md` (runtime map, support dates, function and feature catalog by version,
replacement table, upgrade breakers), `references/spark-functions-since.md` (every Spark SQL built-in function by first
version). Output shapes: `templates/sizing.md`, `templates/version-review.md`.
Evidence reading (Spark UI, query profile, logs): `de-run-diagnose/references/reading-evidence.md`.

## Ground rules

- **Read-only.** `system.compute.*`, `system.query.history`, `system.lakeflow.job_*`, `system.billing.usage`, SDK
  `clusters.get` / `clusters.events` / `jobs.get`, and the code files. No cluster start, resize, edit or stop; no
  warehouse changes; never start compute just to measure. One batched query per question, on the SQL warehouse from
  `specs/project-profile.md`; fold `current_timestamp() AS ts` into the first and last query (worklog).
- **Defer to the official skills.** Serverless vs classic and `performance_target`: `databricks-serverless`.
  Serverless compatibility of existing code (RDD, `sparkContext`, caching, DBFS, triggers): the official serverless
  checks (`databricks-serverless`, section 5; `databricks-serverless-migration` if installed). Cluster and warehouse
  creation mechanics: `databricks-jobs`, `databricks-dabs`. Prices: `de-cost`. Allowed node types, policies and
  quota: the `de-env-check` record.
- **Evidence and confidence.** Every verdict names the query and numbers and the runs counted. Fewer than three
  representative runs (or a week for interactive clusters) is an "early signal", never a resize proposal. Thresholds
  marked "kit heuristic" are labelled as such.
- **Versions are facts with dates.** Every "available since", "deprecated in" or "removed in" claim comes from
  `references/runtime-versions.md` with its source; if the code's runtime or the function is not in the file, say
  "not in the catalog", check the official release notes (`databricks-docs`), and add nothing from memory.
- **Find the runtime first.** Classic: `dbr_version` in `system.compute.clusters` or the job cluster spec. Serverless
  jobs: the job environment's `environment_version`. Notebooks on serverless: the environment panel (user-run).
  SQL: the warehouse channel (`system.compute.warehouses.warehouse_channel`). Pipelines: channel `CURRENT` or
  `PREVIEW`. Unknown runtime means version advice is limited to "works everywhere" suggestions; say so.
- Struggles go through `de-sdd-tracking` into `.challenges_<your-email>/runtime-<topic>.md`, redacted.

## Modes

State the mode in your first line.

| Mode | When | Output |
|---|---|---|
| **Choose** | new job, pipeline or SQL workload: "which compute" | recommendation in chat; with a track, the compute section of `spec.md` / `plan.md` |
| **Right-size** | existing cluster, job or warehouse: "too big", "too slow", "too expensive", "idle" | `specs/compute/<name>-sizing.md` from `templates/sizing.md` |
| **Runtime** | "which DBR / environment version", "what changes if we upgrade", end-of-support | runtime section of the sizing file, or chat for a quick answer |
| **Version advice** | "better function on our version", "deprecated?", "what would a newer version give", code review | `specs/compute/<scope>-version-review.md` from `templates/version-review.md` |

## Choose

1. Profile the workload in one message (up to 5 questions, recommended answer first): language and APIs (SQL, PySpark
   DataFrame, pandas / Python UDFs, RDD, R, Scala), batch or streaming and the latency need, data volume per run and
   growth, shape (wide joins and aggregations, MERGE, ML, simple ETL), schedule and concurrency, deadline.
2. Compute type and performance mode per `databricks-serverless`; state the one-line reason.
3. If classic: size per `compute-sizing.md` section 1 (capacity, node family, Photon, spot, runtime, access mode),
   within the node types and policies the environment record allows.
4. SQL: serverless warehouse size and max clusters per section 2.
5. Cost and time per option with `de-cost`; recommend one, with the second-best and when it would win.

## Right-size

1. Identify the compute (cluster id, job id, warehouse id) and the runs to judge (default: last 14 days of runs).
2. Read config (C1 or W1), utilization (C2 for classic; Q1 for serverless and warehouses), runs (job timeline),
   jobs on all-purpose compute (J1) and cost per run (B1). Serverless and warehouses have no node utilization: judge
   from query history and the query profile.
3. Classify with the right-sizing table (oversized, memory-bound, I/O-bound, driver bottleneck, disk, idle, churn,
   warehouse spill or queue), each with its numbers.
4. Propose: current vs proposed setting, expected run time and cost per run, risk, how to roll back, and where it
   goes (bundle `resources/*.yml` via a `small` track, cluster policy via an admin, warehouse setting via its owner).
   A code problem found on the way (driver-side `collect`, Python UDF, skew) goes to `de-run-diagnose` first:
   bigger compute for bad code is the last option.

## Runtime

1. Read the current runtime per compute. Flag runtimes past or near end of support (within 6 months), non-LTS
   runtimes on production classic compute, and serverless jobs pinned to an old environment version.
2. For an upgrade question, list from `runtime-versions.md`: what the target adds that this code would use, what
   changes behaviour (ANSI mode, removed APIs, Python version, library versions), and what the code must change.
   Test plan: run the job on the target runtime in dev against the same input and compare row counts and checksums
   (`de-quality-testing` invariants) before any prod change.

## Version advice

1. Find the runtime (ground rules). Scan the code files the job runs (text search, not a full repo read) for the
   patterns in the replacement table and the deprecation list of `runtime-versions.md`.
2. For each hit, one row: file and line, what the code does, **on this runtime use** (available now, with the
   reason: speed, correctness, simplicity), **avoid** (deprecated, removed, slow, or breaks on serverless / Spark
   Connect), **gain by upgrading** (the function or feature in a newer version, which version, what it buys).
3. Group into: fix now (works on the current runtime), fix with the upgrade, and upgrade arguments (what the team
   gains from moving). Never propose code that needs a newer runtime than the one it runs on without saying so.
4. Code changes are tasks (`T<nn>` in a track, or a `small` track via `de-sdd-spec`); performance claims are
   checked by a before / after run in dev (`de-run-diagnose`), not assumed.

## Not this skill

Explaining a failure, log, Spark UI page or plan (`de-run-diagnose`, Explain mode). Which product or service to use
(`de-advisor`). Prices and monthly cost (`de-cost`). Whether the workspace has serverless, quota or policies
(`de-env-check`).

## Changelog
- 0.1.0: initial: choose and right-size compute from system tables (node utilization, query history, job runs,
  billing), runtime selection and upgrade impact, version-aware code advice from a dated Spark / DBR catalog. Built
  from a survey of Databricks docs, the official serverless skills, and open-source Spark analyzers and upgrade tools
  (DataFlint, sparkforensics, Dr. Elephant, sql-forge, PySparkler, UCX linter); see the references for sources.
