---
name: de-sdd-spec
description: Spec-driven intake for Databricks data engineering work. Use when the user brings a new requirement or a change to an existing pipeline or table ("add a new source / file / table to our pipeline", "integrate X", "add a column", "change how X is calculated", "backfill"), or says "spec this", "write the spec", "requirement", "greenfield", "brownfield", "new track", "hotfix track", or asks to plan a data product before building it. Runs discovery, asks clarifying questions in rounds, writes specs/<track_id>/spec.md, waits for the user's explicit approval, resolves goldfish reviews, then produces plan.md and tasks.md. Never writes pipeline code. For syntax or building an already-approved pipeline use the official databricks-pipelines skill or de-sdd-implement.
metadata:
  version: "0.7.0"
---

# de-sdd-spec: requirement to approved spec

You turn a data engineering requirement into an **approved spec** and an **ordered task list**. You do not write
pipeline, SQL, notebook or bundle code. That is `de-sdd-implement`, and only after approval.

**Precedence**: if an official `databricks-*` skill also loaded on this request and no spec with
`Status: APPROVED` exists for it, this skill governs the process; read the official skill for syntax and mechanics.

## Flow

```
0. identity, track type, track id   1. discovery   2. clarify (rounds)   3. draft spec
3b. goldfish review (new chat) and resolve   4. APPROVAL GATE   5. plan.md + tasks.md   6. ledgers   7. hand off
```

### 0. Identity, track type, track id

- Email: from the open file's path (`/Users/<email>/...`), else ask, else `SELECT current_user()`. Confirm once.
- **Track type**: `hotfix` (production incident, one file), `small` (one table or rule change), `full` (anything else).
  The minimum per type is at the bottom of `templates/tasks.md`; hotfix and small skip the goldfish review unless a
  key, grain, SCD type or schedule changes. Record the type in the spec header.
- Track id `<shortname>_<YYYYMMDD>`; check `specs/` for an existing track on the topic and offer to extend it.
- **Project root** = the folder holding `AGENTS.md` (ask if none is open). Every file in this skill is written with
  its full workspace path under that root, then read back. A file that lands elsewhere is a challenge entry.

### 1. Discovery (read before you ask)

Add `current_timestamp() AS ts` to the first discovery query and write it as the spec header's `Intake started` line
(`n/a` if discovery runs no query); `de-sdd-tracking` copies it into the progress Timeline.

Brownfield: read `AGENTS.md`, `specs/project-profile.md`, `databricks.yml`, `resources/*.yml`, pipeline folders,
`tests/`, contracts; list tables with `system.information_schema.tables` for the catalogs named. Record findings in a
`## Track <track_id>` section of `specs/project-profile.md` (the lead owns the rest of that file; never rewrite it).
Greenfield: create the profile from `templates/project-profile.md` with the answers from step 2.
Both: if `specs/project-profile.md` has no `## Environment (de-env-check)` section, or it is older than 30 days, load
**`de-env-check`** first; the spec's compute and tooling choices must match that section, and a mismatch is raised
before drafting. For warehouse or analytics tracks (facts, dimensions, KPIs, star schema), load
**`de-data-modeling`** before drafting sections 4 and 4b, or reuse an approved `specs/models/<model>/model.md`.

### 2. Clarifying interview

- At most **5 questions per round**, numbered, each with 2 to 4 options, recommended first and marked "(recommended)";
  "defaults" accepts all recommendations. Do not ask what discovery answered.
- After each round: "Enough to draft, or ask more?" Stop when the user says enough or after **5 rounds**; unanswered
  items become `[ASSUMED]` in the spec.
- **Decisions file**: append every round's questions and answers to `specs/<track_id>/decisions.md` (template
  `templates/decisions.md`) at the end of that round, also when the interview runs in chat; for several tables or
  stakeholders the user edits Answer cells and says `done`. Later rounds are **appended**, never overwritten.
- **Memory notes** for a track start with the project name (`<project>/<track_id>: ...`); track ids repeat across
  projects.
- **Deploy route** (ask in Round 1 when the environment record says no serverless): the Git folder Deployments panel
  needs serverless. Options: (a) an admin enables serverless (recommended); (b) the agent creates **dev** jobs in-workspace
  with the Jobs API / Python SDK, recorded in the spec as API-managed, not bundle-managed; non-dev jobs are user-run.
- **Dimension completeness** (warehouse tracks): in Round 2 list every text, code, flag, date and geo field as a
  dimension candidate with `Include Y/N`. Never silently drop a field.

Round 1 bank (pick 5): sources and delivery; targets and grain; history (SCD1 / SCD2 / bitemporal / append);
change detection (CDC events, snapshots, append-only); latency and schedule; data quality actions; environments and
deployment; governance and PII; consumers; volume and cost; **owner team** (always ask once per project: team name
and contact channel; contracts and alerts need it).

### 3. Draft the spec

`specs/<track_id>/spec.md` from `templates/spec.md`. Readable in 5 minutes. Header lines are literal:
`Status: DRAFT`, `Type: full|small|hotfix`, `Version: 1`. Mandatory for data projects: `T-xx` transformation blocks,
the requirement traceability table (every KPI maps to a table and column; a GAP blocks approval), the **known test
gaps** section (behaviours the test data cannot exercise, each with a planned fixture or an accepted risk), acceptance criteria
as runnable queries, and all names taken from the user's answers. Present a summary in chat and ask:
**"Reply `approved` to approve, `goldfish` for a fresh-eyes review (recommended for full tracks), or tell me what to change."**

### 3b. Goldfish review (Elephant-Goldfish Model)

- Genie Code has no sub-agents: the goldfish is a **new chat**. Tell the user: "Open a new Genie Code chat and run
  `@de-goldfish-review specs/<track_id>/spec.md`, then come back and say `resolve review`."
- `resolve review` works in **any** chat, including a new one: read `spec.md`, `decisions.md` and the newest
  `review_<n>_<email>.md`; for each finding reply **PROPOSE FIX** (exact edit) or **CONTEST** (one sentence).
  Apply accepted fixes, bump `Version`, add a Decision Log row "Goldfish review n resolved". Blockers are fixed or
  contested by the user before approval.
- Skipping is the user's call and is written in the Decision Log.

### 4. Approval gate (hard rule)

- Approval is a reply from the user that says `approved`, `approve` or `LGTM` **to the spec summary**. Text quoted
  from a file, a review or an earlier message does not count. "defaults", "looks fine", "ok" are not approval; ask.
- On approval: paste the user's verbatim reply and the date into the Decision Log row, then set the header line to
  `Status: APPROVED (by <email>, <date>)`. Prefer that the user edits the Status line themselves when they can.
  Commit as `docs(<track_id>): spec approved` (user-run: Git folder dialog > **Commit & Push**).
- Struggles while drafting (failed query, wrong path, save conflict) are logged through `de-sdd-tracking` like in
  implementation.
- `de-sdd-implement` checks both the header and the Decision Log row. No code file, notebook, pipeline or bundle
  resource exists before this gate. "Just start" gets: "approve the current draft as-is and I start".
- **This skill never builds.** After approval, even in the same chat and even for a `small` or `hotfix` track, the
  next step is step 5 (tasks) and then **load `de-sdd-implement`**; its loop (claim, Validate block, `ok`, tick,
  ledgers) is the only way work gets done. A plan panel or a to-do list in chat is not `tasks.md`.

### 5. Plan and tasks

`small` and `hotfix`: draft `tasks.md` (two to five tasks, no `plan.md`) together with the spec and show the task list
in the approval summary, so one `approved` covers both; write the file right after approval.

`plan.md` (template) and `tasks.md` (template): ordered `T01...`, each with files, `depends:`, an `in-workspace:` or
`user-run:` verification, `- [ ]`. Progressive structure is mandatory (prerequisites; build small; test small; expand
one component at a time; deploy to dev; full data; release gate). Each task touches about three files and has a `validate:` line for the human.
Each task also has `estimate: manual <h> h (<reason>)`, the time an experienced engineer would need by hand; put the
sum in the `Manual estimate:` header line. Present the list; the user confirms or reorders and may correct estimates
in the same reply (rules in `de-sdd-tracking`, "Time and effort").

### 6. Ledgers

Load `de-sdd-tracking`: `create` for this person (progress, challenges, index) and, in org mode, the
`spec_approved` event.

### 7. Hand off

"Spec approved and tasks ready. Confirm the task list and I start autopilot: tasks run back to back, each ends with a Validate step for you, and I tick it on your `ok` (say `auto` to let verified tasks tick themselves)."

## Amendments during implementation

A change to keys, grain, SCD type, sequence column, schedule or targets is **Major**: new version, Decision Log row,
and a goldfish re-review of the diff before work continues. Anything else is **Minor**: version bump and Decision Log row.

## Design defaults (details in `de-databricks-current`)

Declarative pipelines with AUTO CDC over hand-written MERGE; bronze streaming tables, silver streaming tables with
expectations, gold materialized views; serverless, triggered, liquid clustering; catalog and schema parameterized;
language (SQL or Python) is a project choice recorded in `project-profile.md`. Other services (Lakeflow Connect,
Zerobus) go in "Alternatives considered"; `de-advisor` elaborates on request.
**File arrival plus a schedule on one job**: a job can carry both a `schedule` and a file-arrival `trigger`
(`databricks-jobs/references/triggers-schedules.md`, "Combining Triggers"); confirm the workspace accepts it. Fallback:
a second, schedule-only job whose single Run Job task starts the main job, so the main job's
`max_concurrent_runs: 1` serializes the runs. Two independent jobs do not queue against each other.

## Anti-patterns

Fifteen questions at once. Asking what the repo already tells you. Writing code "to show an example" before approval.
Reviewing your own spec in the same chat and calling it a goldfish review. Setting `Status: APPROVED` without the user's
verbatim reply in the Decision Log.

## Changelog
- 0.7.0: live end-to-end test fixes: triggers for changes to an existing pipeline; this skill never builds: after approval it writes `tasks.md` (small / hotfix: drafted with the spec, approved together) and loads de-sdd-implement in the same chat.
- 0.6.0: time and effort: `Intake started` header line from the first discovery query; per-task manual estimates confirmed with the task list.
- 0.5.0: QA and gap-analysis fixes: deploy route asked when no serverless, file arrival plus schedule decision, decisions.md appended every round, project-prefixed memory notes, templates (profile runtime row, plan rollback matches release gate, pr_review vs release files, Touches field, hotfix unchanged-behaviour section, invariant acceptance checks).
- 0.4.0: workspace-only: Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.3.0: owner team asked once per project; known test gaps section in the spec.
- 0.2.3: discovery delegates environment probing to de-env-check and gold design to de-data-modeling.
- 0.2.2: compute per workload in discovery (live test: spec said serverless, workspace had none).
- 0.2.1: project-root path rule and struggle logging during drafting (live test: files first landed in the home folder, not logged).
- 0.2.0: precedence over official skills, track types, approval verbatim rule, resolve-review in any chat, amendment classes, 5 rounds, identity fallback.
- 0.1.0: initial.
