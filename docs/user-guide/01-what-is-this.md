# 1. What it is and the words we use

## The pieces

| Piece | What it is | Where it lives |
|---|---|---|
| **Genie Code** | The AI assistant in the Databricks workspace (the sparkle icon on the right of the editor). In **agent mode** it can read files, run SQL, call APIs and write files, asking you before each action. | Built into Databricks |
| **Skill** | A folder with a `SKILL.md` file: instructions Genie Code reads when your request matches. Our skills start with `de-`. Databricks also ships official skills that start with `databricks-` (product syntax). | `/Workspace/.assistant/skills` (everyone) or `/Users/<you>/.assistant/skills` (just you) |
| **AGENTS.md** | Project rules Genie Code reads automatically for any file in that folder: no code before approval, dev only, current product names, and so on. | Root of each project folder |
| **Instructions** | Longer rules the skills point to: coding conventions, security guardrails, waivers. | `instructions/` in each project |
| **This repo** | The source of the skills, `AGENTS.md` template, instructions, scripts and docs. Maintainers change it; admins publish it. | Git (`genie-de-skills`) |

## The skills and what each one does

You never have to call them by name. This table only helps you understand what you see in the chat
("Read de-sdd-spec skill" means that skill was loaded).

| Skill | In plain words |
|---|---|
| `de-sdd-spec` | Turns your request into questions, then a spec, then a task list. The entry point for new work. |
| `de-sdd-implement` | Builds the approved tasks one by one, checks each, fixes its own errors, asks you to validate. |
| `de-sdd-tracking` | Keeps the records: who claimed which task, progress, problems met, status, handover. |
| `de-goldfish-review` | A second opinion on a spec, run in a **new** chat so it has no memory of the first one. |
| `de-data-modeling` | Designs or reviews the data model (facts, dimensions, keys, diagram). For modellers. |
| `de-env-check` | Finds out what your workspace can run (compute, quota, permissions) and lists what the admin must fix. |
| `de-cost` | Estimates cost and run time of options from a dated Azure price list. |
| `de-advisor` | Recommends the best option for a need, in your environment, with cost and time. Read-only. |
| `de-data-contract` | Writes a data contract for a table and tells you what breaks if it changes. |
| `de-quality-testing` | Proposes data quality rules and tests. |
| `de-run-diagnose` | Explains why a run failed and proposes a fix. |
| `de-release-gate` | Reviews work before merge (PR gate) and before production (prod gate). |
| `de-databricks-current` | Current Databricks names and patterns (for example DLT is now Lakeflow Spark Declarative Pipelines). |

## Words you will see

| Word | Meaning |
|---|---|
| **Spec** | A short document (`spec.md`) that says what will be built: sources, tables, rules, checks. Status starts as DRAFT and becomes APPROVED when you reply `approved`. |
| **Track** | One piece of work with its own spec and tasks, for example `orders_medallion_20261111`. Types: `full`, `small`, `hotfix`. |
| **Task** | One step of a track (T01, T02...). Marks: `[ ]` to do, `[~]` in progress, `[x]` done, `[!]` blocked. Each has an owner. |
| **Validate block** | What the agent shows after a task: what changed, what you can check, and the expected result. |
| **Amendment** | A change to an approved spec. Minor ones need your `approved`; major ones (keys, grain, history type, schedule, targets) also need a fresh review. |
| **Goldfish review** | The fresh-eyes review done in a new chat. "Elephant" is the chat that wrote the spec and remembers everything; "goldfish" remembers nothing, so it spots gaps. |
| **Ledgers** | Your own record folders: `.internal_<your-email>/` (progress, evidence) and `.challenges_<your-email>/` (where the agent struggled, with lessons). |
| **user-run** | A step you do yourself in the workspace UI because Genie Code cannot: pull, review the diff and **Commit & Push** in the Git folder dialog, deploy a bundle from the **Deployments** panel, or an admin setting. The agent tells you exactly which button and what to paste back. |
| **in-workspace** | A check the agent runs itself inside Databricks: SQL on your warehouse, an API call, the Pipelines Editor, or `pytest` in a notebook cell. |
| **Medallion** | Bronze (raw), silver (cleaned, one table per business entity), gold (facts and dimensions for reporting). |
| **SCD 1 / SCD 2** | Slowly changing dimension. Type 1 keeps the latest value; type 2 keeps every version with start and end dates. |
| **Bundle** | Declarative Automation Bundle: `databricks.yml` plus `resources/` that describe the pipeline and jobs per environment (dev, prod). |
| **Release gate** | The checklist before merge or production. Verdicts: GO, CONDITIONAL_GO, NO_GO. |

## Why work this way

- **Fewer surprises**: you agree what will be built before any code exists.
- **Smaller mistakes**: one task at a time, each checked with real numbers.
- **Shared knowledge**: specs, decisions and lessons are files in the project, so the next person (or the next chat)
  can continue.
- **Safety**: the agent works in dev, and a human makes every production and permission change.
