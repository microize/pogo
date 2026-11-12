# 1. What it is and the words we use

New to Databricks? Read [page 0: Basics](00-basics.md) first. It explains dev and prod, catalogs, volumes,
compute, pipelines, jobs, Git folders and where to click.

## The pieces

| Piece | What it is | Where it lives |
|---|---|---|
| **Genie Code** | The AI assistant in the Databricks workspace (the sparkle icon on the right of the editor). It can read files, run SQL and write files for you (the panel says "Run multi-step data and AI tasks"). It asks you before each action. | Built into Databricks |
| **Skill** | A folder with a `SKILL.md` file. It holds instructions that Genie Code reads when your request matches. Our skills start with `de-`. Databricks also ships official skills that start with `databricks-`; they hold product syntax. | `/Workspace/.assistant/skills` (everyone) or `/Users/<you>/.assistant/skills` (just you) |
| **AGENTS.md** | The project's rules. Genie Code reads it for any file in that folder: no code before approval, dev only, current product names, and so on. | Root of each project folder |
| **Instructions** | Longer rules the skills point to: coding conventions, security rules, approved exceptions. | `instructions/` in each project |
| **This kit** | The source of the skills, the `AGENTS.md` template, the instructions and these docs. Maintainers change it; admins install it. | Git repository `genie-de-skills` |

## Words you will see

| Word | Meaning |
|---|---|
| **Spec** | A short document (`spec.md`) that says what will be built: sources, tables, rules, checks. It starts as DRAFT and becomes APPROVED when you reply `approved`. |
| **Track** | One piece of work with its own spec and tasks. Example: `shop_orders_20261112`. Types: `full` (bigger work), `small` (one table or rule), `hotfix` (a production bug). |
| **Task** | One step of a track (T01, T02, ...). Marks: `[ ]` to do, `[~]` in progress, `[x]` done, `[!]` blocked. Each task has an owner. |
| **Validate block** | The short note after each task: what changed, how you can check it, and the result to expect. |
| **Amendment** | A change to an approved spec. It needs your `approved` too. Big changes (keys, grain, history type, schedule, targets) also need a fresh review. |
| **Goldfish review** | A fresh-eyes review in a new chat. The chat that wrote the spec remembers everything (the "elephant"); a new chat remembers nothing (the "goldfish"), so it spots gaps. |
| **Ledgers** | Your own record folders: `.internal_<your-email>/` (progress, evidence, time) and `.challenges_<your-email>/` (where the agent struggled, and the lesson). The agent writes them; you only read them. |
| **Manual estimate** | How long an experienced engineer would need **without** the agent for the same result. The agent suggests it; you correct it. It is used only to measure time saved. |
| **Work log** | `worklog.md` in your `.internal_<your-email>/` folder: one line per piece of work outside a track (advice, a model, a diagnosis) with start, finish and manual estimate. |
| **user-run** | A step only you can do in the workspace, because Genie Code cannot press those buttons: pull, review and **Commit & Push** in the Git folder dialog, deploy from the **Deployments** panel, admin settings. The agent tells you which button to press and what to paste back. Where the buttons are: [page 0, section 6](00-basics.md#6-where-to-click). |
| **in-workspace** | A check the agent runs itself: SQL on your warehouse, an API call, the Pipelines Editor, or tests in a notebook cell. |
| **Medallion** | Three layers of tables. **Bronze**: raw data as it arrived. **Silver**: cleaned, one table per business thing (orders, customers). **Gold**: ready for reports, usually *fact* tables (events with numbers, like orders) and *dimension* tables (descriptions, like customer or date). |
| **SCD 1 / SCD 2** | How a table keeps changes. Type 1 keeps only the latest value. Type 2 keeps every version, with start and end dates. Example: a customer moves country; SCD 2 keeps both countries with dates. |
| **Metric view** | A saved definition of business numbers (for example revenue = sum of order amount), so dashboards and Genie use the same formula. |
| **Genie Agent** | A Databricks chat assistant for business users that answers questions on chosen tables (formerly "Genie space"). |
| **Grain** | What one row of a table means. Example: "one row per order line". Getting the grain right prevents double counting. |
| **Unity Catalog** | Where Databricks keeps tables, their owners, descriptions, tags and permissions. Names have three parts: `catalog.schema.table`, for example `dev_shop.gold_sales.fact_orders`. |
| **Lineage** | Which tables feed which other tables. Databricks records it, so the agent can tell what breaks if a table changes. |
| **Runtime (DBR)** | The Databricks Runtime version a classic cluster (machines you choose yourself) runs, for example 15.4 LTS. Each runtime carries one Spark version. LTS means long-term support (three years). Serverless picks the runtime for you. |
| **Bundle** | A few settings files (`databricks.yml` and the `resources/` folder) that tell Databricks what to create, such as the pipeline and its daily job, in dev and in prod. Full name: Declarative Automation Bundle. |
| **Release gate** | The checklist before merge or production. Answers: GO, CONDITIONAL_GO (go, once named conditions are met), NO_GO. |
| **Serverless** | Compute that Databricks starts and sizes for you. You do not choose machines. Most new work runs here. |
| **Classic cluster** | Compute you choose and size yourself (machine type, number of machines). Needed only in special cases. |

## The skills in plain words

You never have to call a skill by name. When you see "Read de-sdd-spec skill" in the chat, that skill was loaded.
The last column shows what each skill would do for ShopCo.

| Skill | What it does | ShopCo example |
|---|---|---|
| `de-env-check` | Finds out what this workspace can run (compute, quota, permissions) and lists what the admin must fix. | "Serverless is on; the system tables for usage are not granted yet." |
| `de-advisor` | Recommends the best option for a need, for your environment, with cost and time. Changes nothing. | "Use Auto Loader for the daily files, not a custom script." |
| `de-cost` | Estimates cost and run time from a dated price list, or reads real spend. | "About 0.20 USD per daily run." |
| `de-data-modeling` | Designs or reviews the data model, the metrics and the Genie Agent setup. | "One fact table for orders, dimensions for customer and date, one metric view for revenue." |
| `de-ontology-design` | Proposes the business concepts and links your data can support, with evidence. Builds nothing. | "Customer places Order; Order contains Product." |
| `de-data-governance` | Checks ownership, descriptions, sensitive data, protection and certification, scores them, and proposes fixes that a person applies. | "Email and phone are not masked: fix first." |
| `de-data-contract` | Writes a contract for a table and says what breaks if it changes. | "Dropping `country` breaks the revenue dashboard." |
| `de-sdd-spec` | Turns your request into questions, then a spec, then a task list. The starting point for new work. | writes `specs/shop_orders_20261112/spec.md` |
| `de-goldfish-review` | A second opinion on a spec, in a **new** chat, so it has no memory of how the spec was written. | "The spec does not say what happens to late orders." |
| `de-sdd-implement` | Builds the approved tasks one by one, checks each, fixes its own errors, and asks you to validate. | builds bronze, silver and gold tables |
| `de-quality-testing` | Proposes data quality rules and tests. | "Order id must be unique; amount must not be negative." |
| `de-run-diagnose` | Runs and checks pipelines, explains failures, logs and slow queries in plain words, and fixes them. | "The silver step failed because a normal view was read as a stream." |
| `de-spark-runtime` | Says which compute and how big, which runtime version, and which code to change for your Spark version. | "Your cluster is idle 88% of the time, and one function in your code stops working on newer Databricks versions." |
| `de-release-gate` | Checks work before merge and before production. Answers GO, CONDITIONAL_GO or NO_GO. | "GO, if the masking policy is in place first." |
| `de-sdd-tracking` | Keeps the records: who did which task, progress, problems, status, handover, time saved. | "9 of 12 tasks done; 6 h 40 min with the agent vs a 32 h manual estimate." |
| `de-databricks-current` | Knows the current Databricks names and patterns. | "DLT is now called Lakeflow Spark Declarative Pipelines." |

## Why work this way

- **Fewer surprises.** You agree on what will be built before any code exists.
- **Smaller mistakes.** One task at a time, each checked with real numbers.
- **Shared knowledge.** Specs, decisions and lessons are files in the project. The next person, or the next chat, can
  continue.
- **Safety.** The agent works in dev. A person makes every production and permission change.
- **Measured benefit.** Every task records how long it took next to a manual estimate, so the team can see the time
  saved instead of guessing.
