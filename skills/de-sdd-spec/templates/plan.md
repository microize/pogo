# Plan: <track title>

Track id: `<track_id>` | Spec: `specs/<track_id>/spec.md` v<version> | Status: APPROVED

## Architecture sketch

```
source --> bronze (streaming table) --> silver (streaming table + AUTO CDC) --> gold (MV / metric view)
                                             |
                                             +--> quarantine (expectations)
```

## Components

| Component | Technology | Location in repo | Notes |
|---|---|---|---|
| Bundle | Declarative Automation Bundles | `databricks.yml`, `resources/` | targets dev / prod |
| Pipeline | Lakeflow Spark Declarative Pipelines (Python, `from pyspark import pipelines as dp`) | `src/<pipeline>/` | serverless, triggered |
| Job | Lakeflow Jobs | `resources/<name>_job.yml` | schedule / trigger |
| Tests | pipeline unit tests | `tests/` | |

## Phases

1. **Foundation**: project profile, bundle skeleton, dev catalog, parameters.
2. **Bronze**: ingestion (Auto Loader / Lakeflow Connect / Zerobus / Kafka).
3. **Silver**: cleaning, expectations, AUTO CDC / SCD.
4. **Gold**: materialized views, metric views.
5. **Operate**: job, schedule, alerts (event log), docs.
6. **Verify**: run all acceptance criteria from the spec.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| sequence column has NULLs | AUTO CDC fails | expectation `expect_or_fail` on bronze |

## Rollback

How to undo: in dev, user-run with the user's explicit instruction: remove the dev resources from the bundle Deployments panel, or ask an admin; in prod, pause the job, redeploy the previous tag from the prod workspace's Git folder Deployments panel, keep tables (see `de-release-gate`).
