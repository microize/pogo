# Project profile

Last updated: <YYYY-MM-DD> by <email>. One per repo. Read by every track.

## Platform

| Item | Value |
|---|---|
| Cloud / workspace | |
| Unity Catalog catalogs (dev / staging / prod) | |
| Compute default | serverless \| classic (record what exists) |
| Compute available | SQL warehouse: <name, size, auto-stop>; serverless notebooks/jobs/pipelines: yes \| no; clusters: <name, access mode, auto-stop> |
| Pipeline engine | Lakeflow Spark Declarative Pipelines |
| Orchestration | Lakeflow Jobs |
| Deployment | Declarative Automation Bundles from the Git folder Deployments panel (needs serverless) \| jobs via Jobs API / SDK (API-managed) |
| Runtime | serverless environment version \| cluster DBR version; pipeline channel CURRENT |
| Source control | Git folder (remote, default branch) or plain workspace folder |
| Run-as identity (prod) | service principal <name> |

## Ownership

| Item | Value |
|---|---|
| Owner team | <team> (contact: <channel>) |
| Other teams sharing this workspace | |

## Environment (de-env-check)

One row per workspace environment and team; details in `specs/env/<env>-<team>.md`. Recheck after 30 days or any
environment failure.

| Environment | Workspace host | Team | Checked | Status | Blocking items |
|---|---|---|---|---|---|

## Conventions

- Naming (catalog.schema.table, columns, keys, audit columns):
- Layers and what lives in each:
- SCD defaults:
- Data quality policy (what warns, what fails):
- PII handling:

## Existing assets (brownfield)

| Asset | Type | Location | Owner | Notes |
|---|---|---|---|---|

## Known pain points

-
