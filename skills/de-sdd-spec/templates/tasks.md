# Tasks: <track title>
Budget: pipeline updates planned <n> / used 0; cluster minutes est <x> / actual 0 (de-sdd-implement updates this)

Track id: `<track_id>` | Spec v<version> | Track type: full | small | hotfix | Status: IN_PROGRESS
Legend: `[ ]` todo, `[~]` in progress, `[x]` done, `[!]` blocked

Rules
- One task per turn. Claim only a task whose `depends:` are all `[x]` and that has no other owner; claim line:
  `- [~] **T03** <title> (owner: <email>, since <YYYY-MM-DD>)`, owner stays when ticked. Sync after every claim or tick
  (Git folder dialog: pull, then Commit & Push; save and re-open in a plain folder; INSERT in org mode). See `de-sdd-tracking`.
- Each task names its verification **and** a `validate:` line: what the human runs or opens to accept it (query, UI path,
  expected result). The agent ticks after the human's `ok` (or immediately in `auto` mode).
- Each task names its verification. `in-workspace:` is what a Genie Code session runs itself (SQL on the attached
  warehouse, SDK `WorkspaceClient()`, Pipelines Editor Validate / Run, `pytest.main([...])` in a notebook cell);
  `user-run:` is what a human does in the workspace UI (bundle Deployments panel, Git folder dialog, admin settings)
  and pastes the result into `progress.md`. A task is not ticked on a claim of success.
- Progressive structure is mandatory: smallest slice, small data, expand one component at a time, deploy, full data, gate.
  No task scales up before the small-data task passed.
- `test_mode` / `limit_rows` below are parameters **you add** to the pipeline configuration; they are not platform features.

## Phase A: Prerequisites

- [ ] **T01** Project profile section for this track
  - files: `specs/project-profile.md` (append a `## Track <track_id>` section; the lead owns the rest of the file)
  - depends: none
  - verify in-workspace: the section lists catalog, schemas, compute, deployment, run-as identity, topology
- [ ] **T02** Connectivity and permissions smoke test
  - depends: T01
  - verify in-workspace: `SELECT 1`; `SHOW GRANTS ON SCHEMA <catalog>.<schema>` shows the run-as principal; source readable (list one file, `SELECT count(*) FROM <src> LIMIT 1`, or one API page)
- [ ] **T03** Bundle skeleton with `dev` and `prod` targets, variables for catalog and schema
  - files: `databricks.yml`, `resources/<pipeline>.yml`
  - depends: T01
  - verify in-workspace: open the pipeline in the Pipelines Editor and run **Validate** (dry run); user-run: Deployments panel on `databricks.yml` > deploy target `dev` succeeds (deploy validates the bundle first; paste the result)

## Phase B to D: build core, test small, validate small (first component only)

- [ ] **T04** Bronze streaming table `<table>` from `<source>` (one source, one table)
  - files: `src/<pipeline>/bronze_<table>.py` (or `.sql`)
  - depends: T02, T03
  - verify in-workspace: dry run passes; dev update with `limit_rows` (SDK `pipelines.start_update` or the editor Run button); `SELECT count(*) FROM <bronze>` > 0; `SELECT count(*) FROM <bronze> WHERE _rescued_data IS NOT NULL` = 0; event log has no ERROR
  - validate: schema matches the contract; sample rows look right

## Phase E: expand one component at a time (build, test, validate per component)

- [ ] **T05** Silver cleaning view plus expectations (spec section 7)
  - depends: T04
  - verify in-workspace: expectation metrics in `event_log('<pipeline-id>')` show the expected pass rates on the small run
- [ ] **T06** AUTO CDC flow into `<silver table>` (`stored_as_scd_type` per spec; syntax from `databricks-pipelines/references/auto-cdc-*.md`)
  - depends: T05
  - verify in-workspace: AC1 and AC2 from the spec; `SELECT key, count(*) ... WHERE __END_AT IS NULL GROUP BY key HAVING count(*) > 1` = 0 rows
- [ ] **T07** Gold materialized view `<mv>`
  - depends: T06
  - verify in-workspace: hand-computed result for one key matches
- [ ] **T08** Tests under `tests/` (pipeline unit tests, unit tests, DQ SQL)
  - depends: T07
  - verify in-workspace: pipeline unit tests pass in the Pipelines Editor, or `pytest.main([...])` in a notebook cell; summary pasted into `progress.md`

## Phase F: deploy and platform test (dev target, small data)

- [ ] **T09** Deploy the bundle to dev and run the job end to end with `test_mode=true`
  - depends: T08
  - verify user-run: Deployments panel > deploy target `dev` succeeds; in-workspace: **Run now** on the deployed job via SDK `w.jobs.run_now` (paste run id and state), every target table has rows and the schemas match

## Phase G: scale up and verify (dev target, full data)

- [ ] **T10** Full-data run and acceptance criteria
  - depends: T09
  - verify in-workspace: run with `test_mode=false`; every acceptance criterion in spec section 15 recorded in `progress.md` with its result; runtime within SLA headroom
- [ ] **T11** Operate: schedule, notifications, freshness alert, runbook note
  - depends: T10
  - verify in-workspace: job shows a schedule or trigger, a failure notification to a channel, and one saved SQL alert

## Phase H: release gate (user-run deploy)

- [ ] **T12** `de-release-gate` prod scorecard; the user runs the prod deploy
  - depends: T11
  - verify: `specs/<track_id>/release_<n>.md` verdict GO or CONDITIONAL_GO with owned conditions; user-run: a human deploys target `prod` from the prod workspace's Git folder Deployments panel (never the agent) and pastes the result

## Minimum per track type

- **hotfix** (production incident, one file): T01 section, one fix task with in-workspace verification, release gate PR mode. Spec is the one-paragraph "Goal" plus acceptance query; goldfish review skipped and recorded.
- **small** (one table or one rule change): T01, one build task, one test task, release gate. One-page spec, no goldfish review unless a key, grain or SCD type changes.
- **full**: everything above.
