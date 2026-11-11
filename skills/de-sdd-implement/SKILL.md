---
name: de-sdd-implement
description: Task-by-task implementation of an approved data engineering spec on Databricks. Use when the user says "implement", "next task", "work on T03", "run the approved plan", or replies "approved" after a spec exists. Claims and executes specs/<track_id>/tasks.md one task at a time with verification, records evidence in .internal_<email>/, logs struggles to .challenges_<email>/, and never changes the spec without the user's approval.
metadata:
  version: "0.5.0"
---

# de-sdd-implement: claim one task, verify, tick, repeat

## Preconditions (every time you are loaded)

1. `specs/<track_id>/spec.md` header reads `Status: APPROVED (...)` **and** its Decision Log has a row quoting the
   user's approval reply. Either missing: stop and load `de-sdd-spec`.
2. `tasks.md` exists with `depends:` on every task. If not, `de-sdd-spec` step 5.
3. This person's `.internal_<email>/<track_id>/progress.md` exists (`de-sdd-tracking` create). Email resolution
   order: open file path, ask, `SELECT current_user()`; read it from the `progress.md` header afterwards.
4. Several open tracks: ask which (list from `specs/` and `index.md`) unless named.
5. Topology known (`project-profile.md`: git-folder, plain-folder, org-events); it decides how claims sync.

## The loop

Pick **this person's `[~]` task**, else the first `[ ]` task whose `depends:` are all `[x]` and that has no owner.
If none is eligible because another person holds the dependency, say so and stop; do not skip ahead.

1. **Claim** through `de-sdd-tracking` (edit one line, then sync: Commit & Push in the Git folder dialog, save and re-open in a plain
   folder, INSERT in org mode). If the line now shows someone else, back off. Announce: "Starting T03: <title>.
   Files: ... Verification: ...".
2. **Re-read the spec sections** the task touches (targets, rules, expectations, acceptance criteria).
3. **Implement**, following `instructions/data-engineering-conventions.md` and `python-pyspark-conventions.md`.
   Syntax comes from the official `databricks-pipelines` references (`auto-cdc-*.md`, `expectations-*.md`,
   `streaming-table-*.md`, ...), `databricks-dabs`, `databricks-jobs`. In Genie Code do not run `databricks-core`'s
   CLI floor check or profile selection; go straight to the reference files. Small diffs; show them.
4. **Verify** exactly as the task says. `in-workspace:` checks you run (SQL, event log query, SDK
   `pipelines.start_update`, Pipelines Editor validate or run, `pytest.main` in a notebook cell).
   `user-run:` checks a human does in the workspace UI (bundle **Deployments panel** on `databricks.yml` in the
   Git folder, Git folder dialog, admin settings); ask for the result and paste it. A task is never ticked on an
   unverified claim.
5. **Record** in `progress.md`: task, files, verification command and result numbers, timestamp, commit message if any.
   Tick `[x]` in `tasks.md` and sync.
6. **Commit** when in a Git folder: user-run in the Git folder dialog > **Commit & Push** with message
   `feat(<track_id>): T03 <title>`; review the diff there first.
7. **Hand the task to the human** with a **Validate** block, then wait (see "Autopilot"). Tick only after the human's
   OK, unless they chose `auto`.

## Autopilot (default after approval)

The user should only have to answer questions, validate results and approve changes. After the plan is confirmed,
run the tasks **back to back** without waiting for `next`:

- Per task: claim, implement, verify in-workspace, then show:
  ```
  T05 done (verified): <one line of what changed>
  Validate: <exact query or UI path the human runs>   Expected: <numbers or state>
  Reply ok to tick and continue, fix <what> to change it, or stop.
  ```
- On `ok` (or "looks good", "done", "next"): tick, record, continue with the next eligible task.
- `auto`: tick tasks whose in-workspace verification passed without waiting, still showing the Validate block;
  stop only for a decision, an amendment, a user-run step, a failure after three fix cycles, or the end.
- **Errors fix themselves first**: a failed verification or run goes to `de-run-diagnose` (classify, add a
  `T<nn>-fix` line, fix, re-run) for up to three cycles before asking the human; every cycle is a challenge entry.
- **Fewer user-run steps**: batch them (one Deployments-panel deploy to `dev` for several tasks), and in the **dev** target
  point the pipeline `libraries` / `root_path` at the project folder's absolute workspace path so you can edit
  files and run updates with the SDK (`WorkspaceClient().pipelines.start_update`) without redeploying. Prod always
  deploys from the bundle.
- Waiting on a run: poll in **one** call that loops with a timeout (Python cell with `WorkspaceClient().pipelines.get_update` every 30 s, max 20 min, print state changes and cluster events on failure), not one tool call per poll; each call costs the human an approval. With no Python compute (SQL warehouse only, or a cluster that would break a quota), do not poll: tell the human "say `check` in about N minutes" and then verify everything in one pass.
- **Budget per track**: `tasks.md` header holds `Budget: pipeline updates planned <n> / used <m>; cluster minutes
  est <x> / actual <y>`. Update it after every update; when used exceeds planned, say so in the Validate block and
  ask before spending more than one extra update.
- **Dry-run first**: before the first real update after adding a dataset or changing a dataset's type, run a
  validate-only update (`start_update(validate_only=True)` or the editor's Dry run); in dev the cluster stays up for
  the shutdown delay, so the real update right after reuses it.
- **Stuck step**: when a SQL step still shows running well past its expected time, check the warehouse query
  history (`system.query.history` or the Query History page) before calling it failed; a stopped display is not a
  cancelled query. Say what you found.
- Cost: pre-check SQL on the warehouse before starting classic compute; small data until the "full data" phase;
  one update per verification, not one per edit.
- Finish: when the last task is ticked, run every acceptance criterion, show a final Validate table, and set
  `Status: COMPLETE` only after the human's OK.

## Missing prerequisite (catalog, schema, volume, compute, grant)

Stop, mark the task `[!]`, log a challenge, and ask who provides it. Never search or read another project's catalogs,
volumes or tables as a substitute source, and never create catalogs or grants yourself.

## When you struggle (mandatory)

Trigger: the same step fails twice, a verification fails, a workaround was needed, a feature is Preview-only, or a
permission, compute or quota error blocks you.
1. Challenge entry through `de-sdd-tracking` (attempts, redacted error, cause, resolution or `OPEN`, lesson).
2. Mark `[!]` if still blocked, name what you need (grant, secret, decision).
3. Never narrow the spec silently to make a task pass.

## When the spec is wrong

Stop. One paragraph on the mismatch and the proposed amendment. Wait for `approved`. Major amendments (keys, grain,
SCD type, sequence column, schedule, targets) also need a goldfish re-review of the diff (`de-sdd-spec`,
"Amendments"). Then version bump, Decision Log row, `tasks.md` adjusted, continue.

## Fixes found while running (de-run-diagnose)

A fix to pipeline code is work: add a task line `T<nn>-fix` under the current task with files and verification, claim
it, then edit. No edits without a task line.

## Guardrails

`instructions/security-guardrails.md` applies: dev target only; no destroy, deploy or full refresh on non-dev;
no DROP / TRUNCATE / GRANT; secrets in secret scopes. Prod deployment is a human step after `de-release-gate`.

## Done

All tasks `[x]`, acceptance criteria recorded with results in `progress.md`, `tasks.md` header `Status: COMPLETE`,
spec header `Status: COMPLETE`, index updated. Offer a review pass: list any spec-to-code gap as new tasks under
"Review fixes" and wait for the user's go.

## Changelog
- 0.5.0: workspace-only: Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.4.0: budget per track, dry-run before the first real update of a new dataset, stuck-step check via query history.
- 0.3.0: autopilot after approval (tasks back to back, Validate block per task, `auto` mode, self-fix via de-run-diagnose, dev SDK iteration without redeploy, cost pre-checks), from the live autonomy test.
- 0.2.1: missing-prerequisite rule (live test: agent probed another project's volume).
- 0.2.0: approval check includes Decision Log row; dependency-aware claims with sync per topology; in-workspace vs user-run verification; fix-as-task rule; amendment classes.
- 0.1.0: initial.
