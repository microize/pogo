# 5. Files and folders in a project

The agent writes these files. You rarely edit them by hand; you read and review them. `.yml` / `.yaml` files are
settings files; `.md` files are plain text documents. Here is the ShopCo project after
the work on [page 3](03-first-task.md):

```
shopco-orders/
  AGENTS.md                         project rules; Genie Code reads them automatically
  instructions/                     coding conventions, security rules, approved exceptions (from the kit)
  databricks.yml                    bundle: targets dev and prod, variables such as the catalog name
  resources/shop_orders.yml         pipeline and job definitions
  src/shop_orders/                  pipeline code, one table per file
    bronze_orders.sql
    silver_orders.sql
    gold_fact_orders.sql
  tests/                            acceptance checks, data quality checks, small test data
  specs/
    project-profile.md              platform, owner team, environments, conventions, productivity target
    env/dev-sales.md                what dev allows, plus the admin checklist          (de-env-check)
    decisions/ADR-001-auto-loader.md   an accepted recommendation (ADR = architecture decision record)  (de-advisor)
    models/sales/model.md           data model, metrics, Genie Agent setup, diagram      (de-data-modeling)
    ontology/sales/ontology.md      business concepts and links (if asked)              (de-ontology-design)
    contracts/fact_orders.yaml      data contract: what the table promises its users     (de-data-contract)
    governance/
      taxonomy.md                   which tags exist and who owns what                   (de-data-governance)
      history.md                    governance score over time
      dev_shop/assessment.md        the audit: scores, findings, proposals
      dev_shop/apply_1.sql          fixes for a person to run (the agent never runs it)
    compute/
      shopco-daily-sizing.md        right-size proposal                                  (de-spark-runtime)
      shopco-version-review.md      code to change for this runtime, and upgrade gains
    shop_orders_20261112/           one folder per track                                 (de-sdd-spec)
      spec.md                       what will be built (DRAFT, APPROVED, COMPLETE)
      decisions.md                  every round of questions and your answers
      review_1_<email>.md           fresh-eyes review findings                           (de-goldfish-review)
      amendment_1.md                a change to the approved spec
      plan.md                       how it will be built, risks
      tasks.md                      T01..T12 with owner, dependencies, checks, manual estimate
      impact_1.md                   what breaks if a table changes                       (de-data-contract)
      pr_review_1.md                merge review                                         (de-release-gate)
      release_1.md                  production check: GO / CONDITIONAL_GO / NO_GO
  .internal_asha@example.com/        Asha's own records (one folder per person)          (de-sdd-tracking)
    index.md                        Asha's tracks and their status
    worklog.md                      time for work outside a track (advice, models, audits)
    shop_orders_20261112/progress.md   evidence, timeline and time per task
  .challenges_asha@example.com/      where the agent struggled, with the lesson
    shop_orders_20261112.md
```

## The files worth reading

| File | Read it when |
|---|---|
| `spec.md` summary | before you reply `approved` |
| `tasks.md` | to see what is done, in progress or blocked, and who owns what |
| `specs/env/<env>-<team>.md` | before choosing compute, and when something is "not allowed" |
| `progress.md` | to see the proof for a task (queries and numbers) and how long it took |
| `.challenges_*` | after a hard day: lessons worth adding to `instructions/` |
| `assessment.md` (governance) | to see which data is unowned, undescribed or unprotected |
| `*-sizing.md`, `*-version-review.md` | before changing compute or upgrading the runtime |

## Status words

| Where | Values |
|---|---|
| spec header | the ones you will see most: **DRAFT** (being written), **APPROVED** (you said `approved`), **COMPLETE** (done). Others: IN_REVIEW, IN_PROGRESS, BLOCKED, ON_HOLD, ABANDONED, SUPERSEDED |
| task line | `[ ]` to do, `[~]` in progress, `[x]` done, `[!]` blocked |
| release check | GO, CONDITIONAL_GO, NO_GO |
| review findings | Blocker (must fix), Major (should fix), Minor (nice to fix) |
| governance score band | Strong (90+), Good (75+), Weak (50+), Ungoverned (below 50); not the same as the bronze / silver / gold table layers |

## Privacy of the record folders

The record folders exist to make the agent's work checkable and to collect lessons, not to rate people. Errors are
written with secrets and personal data removed. Anyone can ask the lead to keep their challenges file out of the
repository. How long records are kept is in `specs/project-profile.md` (default 12 months).
