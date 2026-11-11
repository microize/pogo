# 3. The ShopCo example, start to finish

This page follows one common piece of work from the first question to production. Each step shows **what you type**,
**what the agent does**, and **what you get**. Use the same steps for your own work.

**The need.** ShopCo, a small online shop, receives files every day:

- order files (JSON) in `/Volumes/dev_shop/raw/orders/`,
- a customer file (CSV) in `/Volumes/dev_shop/raw/customers/`, with names, email addresses and phone numbers.

The sales managers want a daily revenue dashboard and a Genie Agent that answers questions like "What was revenue by
country last week?". Customer emails and phone numbers must stay protected.

**The people.** A data engineer builds it. An analytics engineer sets up the metrics and the Genie Agent. A data
steward looks after the sensitive data. The tech lead approves the release. The sales manager (business owner)
answers questions and approves the plan. In a small team, one person can wear several of these hats.

Steps 4 to 8 are shortened from a real test run. The outputs in the other steps are illustrations of what the
skills produce; your numbers will differ.

---

## Step 0. Check what the workspace allows (once per project)

**Type** (any role, usually the lead):
```
check this workspace's readiness for data engineering
```
**The agent** looks at compute, quota, catalogs and system tables. It changes nothing.

**You get** `specs/env/dev-sales.md`, for example:
```
Serverless jobs and pipelines: yes.  SQL warehouse: sales_wh (2X-Small, auto-stop 10 min).
System tables: system.access granted; system.billing NOT granted  -> admin checklist item 1.
```

## Step 1. Ask for advice (optional)

**Type:**
```
advise: what is the best way to load new daily JSON files from a volume?
```
**The agent** compares options for your environment, with cost and time, and says what is GA or still Preview.

**You get** a recommendation: "Auto Loader inside a Lakeflow pipeline on serverless. It picks up only new files,
handles schema changes, and costs about 0.20 USD per daily run." If you accept, it saves a decision record in
`specs/decisions/`.

## Step 2. Design the model and the metrics (analytics engineer)

**Type:**
```
design the model for sales reporting: revenue, orders and average order value by day, country and customer segment.
Genie should answer questions for sales managers.
```
**The agent** asks the business questions first (up to 5, each with a suggested answer). Then it proposes:

- `fact_orders`, one row per order line (the *grain*),
- `dim_customer` (keeps history of country changes, SCD 2), `dim_date`,
- a metric view `sales_metrics` with `revenue`, `order_count` and `avg_order_value`, plus synonyms such as
  "sales" for revenue,
- a Genie Agent "Sales questions" on the metric view, with 5 test questions and their expected answers.

**You get** `specs/models/sales/model.md` with a diagram and checks. Reply `approved` to accept it.

## Step 3. Check governance of the sensitive data (data steward)

**Type:**
```
governance audit of dev_shop: owners, descriptions, sensitive data, and which sensitive columns are not protected
```
**The agent** reads only metadata (names, tags, owners, counts; never the data rows). It scores each table and lists
the most important fixes first:
```
F1 Blocker  silver_sales.customers.email  detected as email address, no mask or policy.
F2 Major    3 tables owned by a person, not a group.
Proposal: tag email and phone  sensitivity=restricted, personal_data=direct;
          add a column-mask policy for everyone except the group sales_pii_readers.
```
**You get** `specs/governance/dev_shop/assessment.md` and `apply_1.sql`. The agent does **not** run it. After your
`approved`, the table owner runs the tag statements and the admin runs the policy.

## Step 4. Ask for the pipeline and answer the questions (data engineer)

Open any file in the project (this is how Genie Code finds `AGENTS.md`), start a **new chat** and **type:**
```
build the ShopCo sales pipeline: daily orders JSON from /Volumes/dev_shop/raw/orders/ and customers CSV from
/Volumes/dev_shop/raw/customers/, into bronze, silver and gold, using the approved model specs/models/sales/model.md.
Project folder: /Users/asha@shopco.com/shopco-orders
```
**The agent** loads `de-sdd-spec`. It looks at the files first. Example: it notices that amounts are stored as text,
times carry time-zone offsets, and two rows are broken. Then it asks:
```
1. Customer history in silver?        a. SCD Type 2 (recommended)  b. SCD Type 1
2. Broken rows?                       a. keep them aside in a quarantine table (recommended)  b. drop them
3. Schedule?                          a. daily at 06:00 UTC (recommended)  b. every hour
4. Time zone for reporting dates?     a. UTC (recommended)  b. shop local time
5. Email and phone in gold?           a. leave them out of gold (recommended)  b. keep them, masked
```
**You type:** `defaults` (accept all suggestions), or answer by number: `1a, 2a, 3a, 4b Europe/Berlin, 5a`.
Add anything else it should know. Type `enough` when you want the draft.

## Step 5. Read the spec, get a fresh-eyes review, approve (business owner and engineer)

**The agent** writes `specs/shop_orders_20261112/spec.md` and shows a summary: tables, rules, checks with the numbers
to expect, and what it could not test.

For a bigger piece of work like this one, get a second opinion first. Open a **new chat** and type:
```
@de-goldfish-review specs/shop_orders_20261112/spec.md
```
The review might say: "Blocker: the spec does not say what happens to orders that arrive a day late." Go back to the
first chat and type `resolve review 1`. The agent proposes a fix for each finding.

When the summary looks right, reply:
```
approved
```
Only this word counts. "ok" or "looks fine" makes the agent ask again. This is on purpose.

## Step 6. Let it build, and validate each task

**The agent** writes `plan.md` and `tasks.md` (T01 to T12, each with an estimate of how long it would take by hand).
Correct any estimate that looks wrong. Then it works through the tasks without you typing `next`. After each task:
```
T04 done (verified): bronze_sales.orders has 8 rows from 2 files; 0 rows in _rescued_data.
Validate: SELECT count(*) FROM dev_shop.bronze_sales.orders     Expected: 8
Reply ok to tick and continue, fix <what> to change it, auto, or stop.
```
- `ok`: you agree. It ticks the task and moves on.
- `fix ...`: say what is wrong, in plain words.
- `auto`: from now on, it ticks tasks whose checks passed without waiting (you still see each Validate note).
- `stop`: pause. Come back later with `status of shop_orders_20261112`, then `next`.

## Step 7. Press the buttons only you can press

1. **Deploy to dev.** Open `databricks.yml` in the project Git folder, click the **Deployments** icon (the rocket),
   choose the `dev` target, click **Deploy**. Paste the result (success or the error text) into the chat.
2. **Commit and push.** Open the Git dialog, look at the changes, use the message the agent suggests (for example
   `feat(shop_orders_20261112): T03 bundle`), and click **Commit & Push**.

The agent groups these, so you stop only once or twice. On a classic cluster a pipeline run can take about 10 minutes
to start; the agent says `say check in about 10 minutes`. Come back and type `check`.

## Step 8. When something fails, it explains and fixes

You do nothing at first. In a real run the silver step failed:
```
orders_valid was read as a stream ... but is not a streaming table
```
**The agent** explains it in plain words: "The silver step reads `orders_valid` as a stream (only new rows), but
`orders_valid` was defined as a normal view (all rows every time). The two do not fit." It fixes both files, logs the
problem in your challenges file, runs again, and the checks pass. After 3 failed attempts on the same problem it stops
and asks you.

You can also ask it to explain anything yourself:
```
explain this query profile        (paste the JSON from Query History > Download)
why is stage 12 so slow?          (paste the stage summary from the Spark UI)
```

## Step 9. Tune compute and code (data engineer)

After a week of daily runs, **type:**
```
is the compute for the ShopCo job the right size? and is our code right for our runtime?
```
**The agent** reads usage from the system tables and the code files:
```
Right-size: worker CPU average 12%, memory 30% over 7 runs -> oversized. Proposal: serverless (STANDARD mode),
            about 40% lower cost per run.
Version:    the job runs DBR 15.4 LTS (Spark 3.5).
            input_file_name() in bronze_orders.py: use _metadata.file_path now (works on 15.4; required from 17.3).
            Upgrade to 18 LTS later: Arrow Python UDFs, SQL scripting; test ANSI mode first.
```
**You get** `specs/compute/shopco-daily-sizing.md` and a version review. Changes become small tasks. The agent never
resizes compute itself.

## Step 10. Release to production (tech lead)

When all tasks are done, the agent runs every acceptance check and asks for your final `ok`. Then **type:**
```
is shop_orders_20261112 ready for production?
```
**You get** `release_1.md` with GO, CONDITIONAL_GO or NO_GO. Example: "CONDITIONAL_GO: the masking policy from
`apply_1.sql` must be applied in prod first." After GO, a **person** deploys from the **Deployments** panel of the
project's Git folder in the **prod** workspace. The agent never deploys to production.

## Step 11. Run it day to day (everyone)

| You type | You get |
|---|---|
| `status of shop_orders_20261112` | done, in progress, blocked, who owns what |
| `hand over T10 to T12 to ben@shopco.com` | a handover note and new owners on those tasks |
| `recheck governance of dev_shop` | the new score next to the old one |
| `we want to drop the region column: what breaks?` | an impact report from lineage (`de-data-contract`) |
| `productivity report for shop_orders_20261112` | for example: "6 h 40 min with the agent vs a 32 h manual estimate; 2 fix cycles; 1 amendment" |

## What you have at the end

- Tables in dev (and later prod) with the expected numbers. The agent showed them; you can query them yourself.
- `specs/shop_orders_20261112/`: spec, plan, tasks (all `[x]` with owners), review and release files.
- `specs/models/sales/model.md`, `specs/governance/dev_shop/assessment.md`, `specs/compute/...`.
- `.internal_<you>/`: progress, evidence and time for each task. `.challenges_<you>/`: what went wrong and the lesson.
