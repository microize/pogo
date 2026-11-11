# 5. Files and folders in a project

A project after a few tracks looks like this. You rarely edit these by hand; the agent writes them and you review them.

```
my-project/
  AGENTS.md                      project rules, read by Genie Code automatically
  instructions/                  conventions, security guardrails, waivers (from this repo)
  databricks.yml                 bundle: targets dev / prod, variables
  resources/*.yml                pipeline and job definitions
  src/<pipeline>/*.sql|*.py      pipeline code, one dataset per file
  tests/                         acceptance checks, data quality checks, fixtures
  specs/
    project-profile.md           platform, owner team, environment index, conventions
    env/<env>-<team>.md          what this environment allows + admin checklist (de-env-check)
    models/<model>/model.md      data model, bus matrix, diagram (de-data-modeling)
    decisions/ADR-001-*.md       accepted recommendations (de-advisor)
    contracts/<table>.yaml       data contracts (de-data-contract)
    <track_id>/
      spec.md                    what will be built (DRAFT, APPROVED, COMPLETE)
      decisions.md               question rounds and answers (bigger tracks)
      review_1_<email>.md        fresh-eyes review findings
      amendment_<n>.md           changes to an approved spec
      plan.md                    how it will be built, risks
      tasks.md                   T01..Tnn with owner, depends, checks, budget
      impact_<n>.md              change impact report
      pr_review_<n>.md           merge review
      release_<n>.md             production gate scorecard
      prod_readiness_<n>.md      tasks to fix a NO_GO
  .internal_<email>/             your progress and evidence (one folder per person)
    index.md
    <track_id>/progress.md
  .challenges_<email>/           where the agent struggled, with lessons
    <track_id>.md
```

## The files you should read

| File | When |
|---|---|
| `spec.md` summary | before you reply `approved` |
| `tasks.md` | to see what is done, in progress, blocked, and who owns what |
| `specs/env/<env>-<team>.md` | before choosing compute, and when something is "not allowed" |
| `progress.md` | to see the evidence for a task (queries and numbers) |
| `.challenges_*` | after a hard day: lessons worth adding to `instructions/` |

## Status values

| Where | Values |
|---|---|
| spec header | DRAFT, IN_REVIEW, APPROVED, IN_PROGRESS, BLOCKED, ON_HOLD, COMPLETE, ABANDONED, SUPERSEDED |
| task line | `[ ]` to do, `[~]` in progress, `[x]` done, `[!]` blocked |
| release gate | GO, CONDITIONAL_GO, NO_GO |
| review findings | Blocker, Major, Minor |

## Privacy of the ledgers

Ledgers exist to make the agent's work auditable and to collect lessons, not to rate people. Errors are written with
secrets and personal data removed. Anyone can ask the lead to keep their challenges file out of the repo. Retention is
in `specs/project-profile.md` (default 12 months).
