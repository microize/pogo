# 6. Cost, environments and teams

## Environments

Most companies have several Databricks workspaces: dev, staging, prod, sometimes one per team or region. They can be
very different. For example, dev may have no serverless compute while prod has it.

- The agent checks **one workspace at a time**: the one you are in. Each check is saved as `specs/env/<env>-<team>.md`.
  *ShopCo:* `specs/env/dev-sales.md`.
- It never assumes prod looks like dev. To check prod, someone with access opens Genie Code **in the prod workspace**
  and runs the readiness check there. Until then, the file marks prod as "not checked".
- Each bundle target (`dev`, `prod`, and `staging` if used) must point at the right workspace. The checks flag a target
  that does not.
- Deploying from the **Deployments** panel needs serverless in that workspace. Without it, the agent creates **dev**
  jobs through the Jobs API with your approval. Jobs in other environments are created by a person. The spec records
  this.

## Teams sharing a workspace

- Use only your team's compute: your SQL warehouse and your cluster policies. Another team's running cluster is not
  free capacity. The agent will never start, stop or attach it.
- Cloud quotas (a limit on machines, for example 10 vCPUs, meaning virtual processor cores, in one region) are shared by everyone in the cloud subscription. If a run is
  "waiting for resources", someone else may be using the quota. Agree on a split with the other team; the environment
  file records it.

## Cost

Ask in plain words: `how much will this cost per month?`, `serverless or classic?`, `which warehouse size?`

How the estimate works (`de-cost`). A **DBU** (Databricks Unit) is how Databricks measures usage for billing:
bigger or longer-running compute uses more DBUs.

| Compute | Cost per run |
|---|---|
| Classic cluster or pipeline | hours x machines x (DBUs per hour x price per DBU + machine price per hour) |
| Serverless SQL warehouse | hours x warehouse DBUs per hour x serverless SQL price |
| Serverless jobs or pipelines | DBUs used x serverless price |

"Hours" includes start-up and idle time. In our test, a classic cluster took about 10 minutes to start for a 1-minute
job, so start-up was most of the cost.

**Example from our test** (Azure East US 2, list prices): the daily pipeline on two mid-size machines (type D4ds_v4)
cost about 0.22 USD per run, about 6.60 USD a month. Keeping the same cluster running all the time would cost about 921 USD a month.

**While you build**, agent turns and SQL warehouse time usually cost more than the pipeline runs. To keep this down:

- set the warehouse auto-stop low (a few minutes),
- ask the agent to combine its checks into fewer queries,
- keep your team's SQL warehouse attached to the notebook or file you chat from (page 2), instead of a big cluster.

Good to know:

- Prices come from a **dated price file** in the kit (`skills/de-cost/references/prices/azure-<region>.json`). The agent
  always tells you the date. These are list prices: no company discounts, no taxes.
- (For maintainers.) To update prices: type `refresh prices` in a chat that has Python compute with internet access. Or a maintainer runs
  `skills/de-cost/scripts/refresh_prices.py --region <region>` from a notebook cell in the kit's Git folder, commits the
  new file, and re-runs `install/install_skills`.
- Real spend is in the `system.billing` tables, if your admin has given you access.

## Choosing compute

There are two kinds of question, and two skills:

| Question | Skill | ShopCo example |
|---|---|---|
| Which **service or approach**? | `de-advisor` | `advise: Auto Loader or Lakeflow Connect for the daily files?` |
| Which **compute and how big**, is it the **right size**, which **runtime version**? | `de-spark-runtime` | `is the compute for the ShopCo job the right size?` |

`de-advisor`:

1. reads your environment file (what you have now),
2. checks which features exist and are GA (fully released) or still Preview,
3. compares options by run time and cost,
4. recommends the best fit today. If an upgrade would help, it says which one, who must do it and what it changes. For
   example: "An account admin enables serverless pipelines: start-up drops from about 10 minutes to under a few
   minutes, for about 0 to 20 USD more a month."

If you accept, it saves the decision in `specs/decisions/` so the next person knows why.

`de-spark-runtime`:

- for **new** work, asks about the workload and recommends compute. Serverless is the default; a classic cluster only
  when something needs it (for example R code);
- for **existing** work, reads real usage from the system tables (how busy the machines were, whether data ran out of
  memory and *spilled* to disk, how long queries *queued* waiting for compute) and says "too big", "not enough memory",
  "idle" and so on, with the numbers. It needs at least 3 normal runs before it proposes a
  change;
- checks the **runtime version**: support end dates, and what an upgrade would bring or break;
- checks your **code against the Spark version** it runs on: what to use now, what to stop using, what a newer version
  would give.

It never resizes, starts or stops compute. Changes become small tasks or a request to the admin.
