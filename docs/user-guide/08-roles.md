# 8. Roles: where to start

Find your role. Each section says, in plain words:

- **You do**: your part of the work,
- **Type first**: a request to copy, using the ShopCo example from [page 3](03-first-task.md),
- **What happens**: the skills that help, in order,
- **You get**: the files it writes,
- **You approve**: the decisions that need your reply.

You never need skill names. Type the request and Genie Code loads the right skill.

## Data engineer

- **You do:** build and run the pipelines, keep them healthy and efficient.
- **Type first:**
  ```
  build the ShopCo sales pipeline: daily orders JSON from /Volumes/dev_shop/raw/orders/ into bronze, silver and gold
  ```
- **What happens:** questions and a spec (`de-sdd-spec`) → a fresh-eyes review in a new chat (`de-goldfish-review`)
  → you reply `approved` → tasks one by one with a check each (`de-sdd-implement`, `de-quality-testing`) → failures
  are explained and fixed (`de-run-diagnose`) → merge and production checks (`de-release-gate`).
- **Also useful:**
  - `explain this stack trace` / `explain this query profile`: plain-language explanation (`de-run-diagnose`).
  - `is the compute for the ShopCo job the right size?`, `which functions in bronze_orders.py should change for our
    runtime?` (`de-spark-runtime`).
- **You get:** `specs/<track_id>/`, code in `src/` and `resources/`, tests in `tests/`, your records.
- **You approve:** the spec, each task's Validate check (`ok`), changes to the spec.

## Analytics engineer / BI developer

- **You do:** make gold data easy to use: metrics, descriptions, dashboards, Genie Agents.
- **Type first:**
  ```
  make gold sales ready for Genie: a revenue metric view, descriptions, keys and a Genie Agent for sales managers
  ```
- **What happens:** `de-data-modeling` asks the business questions first, then proposes metric views (with synonyms
  like "sales" for revenue), table and column descriptions, keys, and a Genie Agent with test questions and their
  expected answers. Then `de-sdd-spec` turns it into a build, and `de-sdd-implement` creates it in dev.
- **Also useful:** `right-size warehouse sales_wh` (`de-spark-runtime`), `explain this query profile`
  (`de-run-diagnose`) for a slow dashboard.
- **You get:** `specs/models/sales/model.md`, then a build track.
- **You approve:** metric definitions, descriptions, the test questions.

## Data architect

- **You do:** choose technologies and patterns, set standards, review designs.
- **Type first:**
  ```
  advise: Lakeflow Connect, Auto Loader or Zerobus for ShopCo's order events at 2,000 per second?
  ```
- **What happens:** `de-advisor` compares options for your real environment (`de-env-check`), with cost and time
  (`de-cost`), and says which features are GA or Preview. For changes to shared tables, `de-data-contract` writes the
  contract and an impact report. For specs written by others, run a fresh-eyes review in a new chat
  (`de-goldfish-review`).
- **Also useful:** `what compute standard should we use for nightly ETL?` (`de-spark-runtime`).
- **You get:** `specs/decisions/ADR-*.md`, `specs/contracts/*.yaml`, `impact_<n>.md`, review files.
- **You approve:** decision records, contract versions, breaking changes.

## Data modeler

- **You do:** design how data is structured and what it means.
- **Type first:**
  ```
  design the model for sales reporting: revenue by day, country and customer segment
  ```
  or, for concepts and links:
  ```
  what concepts and relationships do the ShopCo customer and order tables support?
  ```
- **What happens:** `de-data-modeling` works out the business processes, the grain (what one row means), facts and
  dimensions, history rules (SCD), a diagram and check queries, then a review. `de-ontology-design` proposes concepts
  ("Customer", "Order"), properties and relationships ("Customer places Order"), each with how strong the evidence is.
  Neither skill writes pipeline code; the build goes through `de-sdd-spec`.
- **You get:** `specs/models/<model>/model.md`, `specs/ontology/<domain>/ontology.md`.
- **You approve:** grain, keys, history types, names and definitions (or you name the business owner who does).

## Data steward / governance lead

- **You do:** make sure data has owners, descriptions, correct sensitivity labels and protection, and that trusted data
  is marked as trusted.
- **Type first:**
  ```
  governance audit of dev_shop: owners, descriptions, sensitive data, and which sensitive columns are not protected
  ```
- **What happens:** `de-data-governance` reads only metadata (names, tags, owners, counts; never data rows). It scores
  every table against 22 checks based on the EDM Council's CDMC controls, rates maturity, and lists fixes, most risky
  first: sensitivity tags, masks and access policies, group owners, stewards, certification. You reply `approved`; the
  owner or admin runs `apply_<n>.sql`; then `recheck governance of dev_shop` shows the score move.
- **Also useful:** `propose a tag taxonomy for our catalogs`, `who should own and look after the sales schemas?`,
  `what can we certify in gold?`
- **You get:** `specs/governance/taxonomy.md`, `specs/governance/<scope>/assessment.md`, `apply_<n>.sql`,
  `specs/governance/history.md`.
- **You approve:** the tag list, sensitivity per column, owners and stewards, certification. The agent never applies
  tags, descriptions, permissions or policies itself.
- **Before the first audit:** reading the classification and data quality results needs a grant from the account
  admin. The report lists the exact step.

## Tech lead

- **You do:** plan, unblock, approve releases, and watch quality and productivity.
- **Type first:**
  ```
  status of shop_orders_20261112
  ```
- **What happens:** `de-sdd-tracking` shows what is done, in progress and blocked, who owns what, what the agent
  struggled with, and time taken against manual estimates. `de-release-gate` checks merges and production readiness.
- **Also useful:** `who did what on shop_orders_20261112`, `what did we struggle with this month`,
  `productivity report for the team, last 30 days`, `is shop_orders_20261112 ready for production?`
- **You own:** `specs/project-profile.md` (conventions, shared-file setup, record retention, productivity target),
  handovers, and the production decision after GO.

## Workspace admin

- **You do:** install the kit and give access, compute and settings that only an admin can give.
- **Type first:**
  ```
  check this workspace's readiness for the sales team
  ```
- **What happens:** `de-env-check` lists compute per workload, quota, catalogs and system tables, and writes a
  checklist of what only you can enable. Install or update the kit with `install/install_skills` (scope `workspace`).
- **Also useful:** `which clusters are idle or running jobs on all-purpose compute?` (`de-spark-runtime`).
- **You get:** `specs/env/<env>-<team>.md`.

## Business / product owner

- **You do:** say what is needed, answer questions, and approve.
- **What happens:** the agent asks you up to 5 questions at a time, each with a suggested answer. Reply `defaults` to
  accept them all, or answer by number. Read the spec summary and reply `approved`. For models and metrics you own the
  **meaning**: names, definitions and the business questions the data must answer ("What was revenue by country last
  week?"). Those questions become tests and Genie test questions.

## Roles not covered yet

| Role | What is missing | What to use today |
|---|---|---|
| ML engineer / data scientist | feature tables, training sets and model serving | the official `databricks-*` skills |
| On-call / operations | `de-run-diagnose` handles one failure at a time; there is no runbook or incident-review skill across jobs | `de-run-diagnose` plus the runbook note from the operations task |

Want one of these covered? Tell the kit's maintainers which role, and the first three requests you would type.
