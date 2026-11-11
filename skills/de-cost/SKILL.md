---
name: de-cost
description: Cost and run-time estimates for Databricks on Azure. Use when the user asks "how much will this cost", "cheapest option", "serverless or classic", "which warehouse size", "cost vs speed", "monthly cost of this pipeline or job", "refresh prices", "update the price file", or when de-advisor or de-sdd-spec needs a cost comparison. Computes from a static, dated price file (references/prices/azure-<region>.json: DBU rates per workload, DBUs and VM price per node type, SQL warehouse sizes) that refresh_prices.py rebuilds from the Azure Retail Prices API and the Azure calculator feed on demand. List prices only; actual spend comes from system.billing when available.
metadata:
  version: "0.2.0"
---

# de-cost: price the options before choosing one

## Inputs

- **Price file**: `references/prices/azure-<region>.json` (and the readable `.md` beside it). Use the workspace's
  region from the environment record (`specs/env/<env>-<team>.md`) or ask. Always print the file's `generated_at`
  and say "list price, pay-as-you-go". If the file is older than 90 days, say so and offer a refresh.
- **Workload shape**: runs per month, data volume, expected run minutes, latency need. Take run minutes from real
  runs when they exist (pipeline update durations, job run durations, `system.billing.usage` if granted); otherwise
  state the assumption.
- **What the environment allows** (`de-env-check` record): serverless or classic, node types allowed by policy, quota.
  Price unavailable options too, marked "needs enablement", so the user sees what an upgrade would buy.

## Formulas (from the price file)

| Option | Cost per run |
|---|---|
| Classic job / pipeline / all-purpose | billed hours x nodes x (DBU per hour x Photon multiplier if Photon x USD per DBU for the workload + VM USD per hour) |
| SQL warehouse (serverless) | billed hours x size DBU per hour x serverless SQL rate (infrastructure included) |
| SQL warehouse (pro / classic) | billed hours x size DBU per hour x pro or classic SQL rate, plus Azure VM cost billed separately |
| Serverless jobs, notebooks, pipelines | DBUs consumed x serverless rate (infrastructure included); DBUs from billing actuals, or estimated from a comparable classic run and stated as an estimate |

Billed hours = start-up + run + idle shutdown delay. Classic start-up on this kind of workspace is 4 to 10 minutes
(measure it from cluster events); serverless start-up is seconds. Workload keys: `jobs`, `jobs_photon`,
`all_purpose`, `pipeline_core|pro|advanced` (Lakeflow pipeline editions; meters still say "Delta Live Tables"),
`sql_serverless`, `sql_pro`, `serverless_jobs`, `serverless_pipelines`, `serverless_notebooks`.

## Procedure

1. Read the price file and the environment record. Name the region, tier and file date.
2. List 2 to 4 options that meet the requirement (from `de-advisor` or the spec), including at least one option the
   environment does not have yet when it would change the answer (for example serverless when only classic exists).
3. For each option compute **wall time per run**, **cost per run** and **cost per month**, showing the arithmetic once
   per option. With Python compute available you may run `scripts/estimate.py` with a scenario file; otherwise
   compute by hand from the formulas. Never invent a rate that is not in the file.
4. **Balance cost and time**: the latency or SLA requirement is a hard filter; among the options that pass, prefer the
   lowest monthly cost unless a slower option risks the SLA window (less than 20 percent headroom). Say which option
   is cheapest, which is fastest, and which is the best fit, with one sentence why.
5. When actuals exist (`system.billing.usage` joined to list prices), compare estimate and actual and say which to trust.

Output table: option, available now or needs enablement, wall time per run, DBU per run, USD per run, USD per
month, fits SLA (yes / no), notes.

## Refresh the price file (user-triggered)

Prices change. When the user says "refresh prices" (or the file is stale):
- Run it from a notebook cell in the **skills repo's Git folder** (the compute needs outbound internet), so the new
  file can be committed: `%sh python skills/de-cost/scripts/refresh_prices.py --region <region> --out
  skills/de-cost/references/prices` (or the same call through `subprocess` in a Python cell), and show the summary
  line. Add `--tier standard` for Standard workspaces and `--nodes d32dsv5,...` for more node types.
- Then the user commits the new files (Git folder dialog, Commit & Push) and republishes the skills with the
  `install/install_skills` notebook, so every Genie Code session reads the new prices.
- No outbound internet from any compute in this workspace: an admin runs the same notebook cell in a workspace that
  has egress, or the estimate stays on the dated file and says how old it is.
- After a refresh, report which rates changed against the previous file.

Sources: Azure Retail Prices API (official) for DBU rates and VM prices; the Azure pricing calculator feed (the data
behind the public calculator page, not an official API) for DBUs per node type, Photon multipliers, SQL warehouse
sizes and the serverless pipeline rate. If the feed changes shape, the script reports what it could not read.

## Rules

- Estimates, not invoices: list price in USD, no commit discounts, reservations or taxes. Say so in every table.
- Read-only: no compute is started to measure cost; use existing run history.
- Cost never overrides guardrails or the spec's SLA.

## Changelog
- 0.2.0: workspace-only: Pipelines Editor, SDK, Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.1.0: initial: static Azure price file with refresh script, estimate formulas and calculator, cost-time balance.
