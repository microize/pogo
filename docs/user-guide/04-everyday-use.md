# 4. Everyday use: what to type

Before you start: open a notebook inside the project folder (create an empty one called `chat` if there is none),
attach your team's SQL warehouse, then start a **new chat** for each new piece of work. New words are explained on [page 0](00-basics.md). Write in plain
words. If the chat might not know the project, add its path.

## Three sizes of work

The agent picks the size from your words; you can say it yourself ("small change", "hotfix").

| Size | Use it for | What you get | ShopCo example |
|---|---|---|---|
| **full** | new pipelines, new tables, anything with several steps | questions, a spec, a fresh-eyes review, a plan, 8 to 15 tasks | the whole ShopCo sales pipeline |
| **small** | one table or one rule changes | a one-page spec, one build task, one test task, a merge check | "add a region column to silver orders" |
| **hotfix** | a bug in production | a one-paragraph spec with a before / after check, one fix task, a merge check | "fact_orders counts cancelled orders twice" |

All three need your `approved` before any code is written.

## Short replies the agent understands

| You type | Meaning |
|---|---|
| `defaults` | accept every suggested answer in the current round of questions |
| `enough` | stop asking questions and write the spec |
| `approved` | approve the spec or a change to it (only this word counts, not "ok") |
| `goldfish` | ask for a fresh-eyes review before approving |
| `resolve review 1` | go through the findings of review number 1 and propose fixes |
| `ok` | the task's Validate check looks right: tick it and continue |
| `auto` | tick tasks whose checks passed without waiting for me |
| `next` | continue with the next task |
| `check` | the run you told me to wait for should be done now: check it |
| `stop` | pause here |
| `status` | where is this work, who did what, what is left |
| `est 5h` | correct the agent's manual estimate for the work it just logged |

## What to type, by situation (with ShopCo examples)

| Situation | Example |
|---|---|
| Understand a table | `what is in dev_shop.silver_sales.orders and where does it come from?` |
| See where work stands | `status of shop_orders_20261112` |
| New pipeline or table | `build a pipeline that loads the daily ShopCo order JSON from /Volumes/dev_shop/raw/orders/ into bronze, silver and gold` |
| Small change | `add a region column to silver orders from the shipping region field (small change)` |
| Production bug | `hotfix: gold fact_orders counts cancelled orders twice` |
| Continue yesterday's work | `status of shop_orders_20261112`, then `next` |
| Something failed | `the dev pipeline shop_orders failed today: find out why and what to change` |
| Understand an error or log | `explain this stack trace` (paste it) |
| Understand a slow query | `explain this query profile` (paste the JSON from Query History > Download), or `why is stage 12 slow?` (paste the Spark UI stage summary) |
| Data quality | `propose data quality rules and tests for silver orders and customers` |
| Data model | `design the model for sales reporting: revenue by day, country and segment` |
| Metrics and Genie | `set up metric views and a Genie Agent on gold sales, with descriptions and keys` |
| Business concepts | `what concepts and relationships do our customer and order tables support?` |
| Governance | `governance audit of dev_shop: owners, descriptions, sensitive data, unprotected columns` |
| Choose a technology | `advise: Auto Loader or Lakeflow Connect for files that arrive by SFTP?` |
| Choose or size compute | `which compute for a nightly 200 GB join job?`, `is cluster etl-nightly too big?`, `right-size warehouse sales_wh` |
| Runtime and code versions | `we run DBR 15.4: which functions in bronze_orders.py should change, and what would 18 LTS give us?` |
| Cost | `how much does the daily ShopCo pipeline cost, and would serverless be cheaper?` |
| Contract and impact | `write the data contract for gold fact_orders and tell me what breaks if we drop region` |
| Before merging | `review shop_orders_20261112 for merge` |
| Before production | `is shop_orders_20261112 ready for production?` |
| Hand work to a teammate | `hand over T05 to T07 of shop_orders_20261112 to ben@example.com` |
| Workspace problems | `check this workspace's readiness`, or later `recheck` |
| Time saved | `productivity report for me, last 30 days` |
| Old price list | `refresh prices` |

## Working with teammates

- **Each person has their own record folders** (`.internal_<email>/`, `.challenges_<email>/`). Write only in your own.
- **Tasks have owners.** The agent writes your email on a task before it works on it, and skips tasks someone else
  owns.
- **Git folder:** in the folder's Git dialog, click **Pull** before you start and **Commit & Push** after each ticked
  task. The agent suggests the message, for example `feat(shop_orders_20261112): T03 bundle`. Scheduled runs use the
  files in the Git folder, so commit only work whose task is ticked.
- **Plain folder:** the agent re-reads a file just before saving, so it does not overwrite a teammate's change.
- **Going on leave?** Ask for a handover. The agent writes a note with everything the next person needs and moves your
  open tasks to them.

## Time and estimates

The agent records when each task starts and finishes, using the time from Databricks itself (not a guess). This adds
no extra Allow / Skip prompts.

With the task list, it suggests a **manual estimate** per task (how long it would take by hand). Correct any that look
wrong in the same reply. After advice, a model, a diagnosis or other work outside a track, it ends with a line like:
```
Logged: about 3 h by hand (say "est 5h" to correct).
```
Nothing is guessed: a step with no query shows `n/a`. The productivity report compares time taken with the estimates,
and shows rework (fix cycles, changes to the spec) next to the saving. It is for improving the kit, never for rating
people.

## Approvals inside Genie Code

Genie Code asks **Allow / Skip** before it runs anything. Use the one rule on
[page 0, section 7](00-basics.md#7-two-safety-rules). In short: allow reading; allow dev changes inside an approved task;
skip anything not dev, anything that deletes or changes permissions, and anything you are unsure about.

There is an **Auto-approve** switch for one chat. Do not use it until your lead says so, and never where there is
production data.

## Habits that save time

- One chat per track or question. Long chats get slow and lose focus. The files carry the memory.
- Keep your team's SQL warehouse attached in the editor.
- When the agent asks questions, answer all of them in one reply.
- Read the spec summary before `approved`. Changing a spec later is possible, but costs time.
- If a step looks stuck but has already finished (see [Troubleshooting](07-troubleshooting.md)), tell the agent "the
  query finished, continue" instead of starting over.
