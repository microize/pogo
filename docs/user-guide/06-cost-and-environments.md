# 6. Cost, environments and teams

## Environments

Most organizations have several Databricks workspaces: dev, staging, prod, sometimes one per team or region. They can
differ a lot: dev may have no serverless compute while prod has it, or the other way round.

- The agent checks one workspace at a time (the one you are in). Each check is saved as `specs/env/<env>-<team>.md`.
- It never assumes prod looks like dev. To check another workspace, someone with access opens Genie Code **in that
  workspace** and runs the readiness check there; until then the file marks it as not checked.
- Each bundle target (`dev`, `prod`) must point at the right workspace host. The checks flag a target that does not.

## Teams sharing a workspace

- Use only your team's compute (your SQL warehouse, your cluster policies). Another team's running cluster is not free
  capacity, and the agent will never start, stop or attach it.
- Cloud quotas (for example 10 vCPU in a region) are shared by everyone in the subscription. If a run waits "for
  resources", someone else may be using the quota. Agree the split with the other team; the environment file records it.

## Cost

Ask in plain words: `how much will this cost per month`, `serverless or classic`, `which warehouse size`.

How the estimate works (`de-cost`):

| Option | Cost per run |
|---|---|
| Classic cluster or pipeline | hours x nodes x (DBUs per hour x price per DBU + VM price per hour) |
| SQL warehouse (serverless) | hours x warehouse DBUs per hour x serverless SQL price |
| Serverless jobs or pipelines | DBUs used x serverless price |

"Hours" includes start-up and idle time. A classic cluster in our test took about 10 minutes to start for a 1 minute
job, so start-up was most of the cost.

Example from our test (East US 2, list price): the daily medallion pipeline on 2 D4ds_v4 nodes costs about 0.22 USD per
run, about 6.60 USD a month; keeping it running all the time would cost about 921 USD a month.

Things to know:

- Prices come from a **dated price file** in the skill (`skills/de-cost/references/prices/azure-<region>.json`). The
  agent always tells you the date. They are list prices: no company discounts, no taxes.
- To update prices: type `refresh prices` in a chat that has Python compute with internet access, or a maintainer runs
  `skills/de-cost/scripts/refresh_prices.py --region <region>` from a notebook cell in the kit's Git folder (needs
  internet egress), commits the new price file, and re-runs `install/install_skills`.
- Actual spend is in the `system.billing` tables, if your admin has granted access.

## Choosing compute: the agent's advice

Ask `advise: ...`. The advisor:

1. reads your environment file (what you have now),
2. checks which features exist and are GA,
3. compares options with run time and cost,
4. recommends the best fit for today and, if an upgrade would help, says which one, who must do it and what it
   changes (for example "an account admin enables serverless pipelines: start-up from about 10 minutes to under a
   few, about 0 to 20 USD more a month").

If you accept, it saves the decision in `specs/decisions/` so the next person knows why.
