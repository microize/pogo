---
name: de-sdd-tracking
description: Owns the work ledgers for spec-driven data engineering on Databricks so a team knows who did what: task claims in tasks.md (and the optional Unity Catalog events table), .internal_<email>/<track_id>/progress.md (evidence per task), .challenges_<email>/<track_id>.md (where the agent struggled), .internal_<email>/worklog.md (time per piece of work outside tracks), task and track start / finish times with manual-effort estimates, and track status. Use for "status", "where are we", "what is left", "who did what", "what did we struggle with", "show challenges", "time report", "productivity report", "how much time did we save", or when another skill must create or update these files. Does not implement tasks.
metadata:
  version: "0.6.0"
---

# de-sdd-tracking: ledgers, claims, status

## Supported topology (say which one applies)

| Topology | Shared files | How claims become visible |
|---|---|---|
| **Databricks Git folder, shared branch** (recommended) | `specs/` in the repo | every person has their own clone; a claim is visible only after **commit and push** (Git folder UI, user action) and the other person **pulls**. Claim = pull, edit one line, commit, push. |
| **Plain workspace folder** (no git) | one copy of `specs/` | last write wins and the file is rewritten whole. Claim = re-open `tasks.md`, edit one line, save, re-open and confirm the line is still yours before starting. |
| **Org mode: Unity Catalog events table** (recommended for more than two people) | `specs/` plus `<catalog>.sdd.task_events` | every claim, tick, block and challenge is one `INSERT`; concurrent, timestamped, queryable. `tasks.md` stays the readable view. Set `sdd_events_table` in `specs/project-profile.md`. |

Events table DDL (admin creates once per catalog; everyone gets `SELECT` and `MODIFY`):

```sql
CREATE TABLE IF NOT EXISTS <catalog>.sdd.task_events (
  event_ts TIMESTAMP, track_id STRING, task_id STRING,
  event STRING,          -- claim | start | verified | tick | block | unclaim | challenge | spec_approved | review | handover | worklog
  email STRING, note STRING);
```
`INSERT INTO <catalog>.sdd.task_events VALUES (current_timestamp(), '<track>', 'T03', 'claim', current_user(), '');`

## Identity (one folder per person)

Resolve the email once per chat, in this order, and write it into the `progress.md` header so later chats reuse it:
1. the path of the open file or Git folder (`/Users/<email>/...`);
2. ask the user;
3. `SELECT current_user()` when a SQL warehouse is available.
Folder names keep the email literally (`.internal_a.b@company.com/`). If the workspace rejects `@`, the project
sets `email_folder_style: _at_` in `specs/project-profile.md` once and everyone follows it.
Never write into another person's `.internal_*` or `.challenges_*`; read them for reports only.

## Files

```
specs/<track_id>/tasks.md                 # shared: order, dependencies, ownership (one line per claim or tick)
.internal_<email>/index.md                # this person's tracks: template templates/index.md
.internal_<email>/<track_id>/progress.md  # evidence and times per task: template templates/progress.md
.internal_<email>/worklog.md              # time per piece of work outside a track: template templates/worklog.md
.challenges_<email>/<track_id>.md         # struggles: template templates/challenges.md, append-only
```

Status vocabulary, used everywhere (spec header, tasks header, progress, index, events):
`DRAFT | IN_REVIEW | APPROVED | IN_PROGRESS | BLOCKED | ON_HOLD | COMPLETE | ABANDONED | SUPERSEDED`.
Task markers: `[ ]` todo, `[~]` in progress, `[x]` done, `[!]` blocked.

## Operations

**Write rhythm.** Ledgers (`progress.md`, `index.md`, challenges) are written **once at the end of each task** (or
when a task blocks), in one edit per file, not after every step; `tasks.md` claim lines are the only mid-task write.
Re-read a file right before writing it; on a save conflict re-read and re-apply once, then log a challenge.

### create (after approval, called by de-sdd-spec)
Copy `progress.md` and `challenges.md` templates into this person's folders, fill the header with email, spec version and
topology, copy the spec-phase times from the spec's `Intake started` / `Approved` header lines into the progress
**Timeline**, add a row to `index.md`, and if org mode is on, `INSERT ... 'spec_approved'`. Create `worklog.md` from its
template the first time this person needs it.

### claim
Only a task whose `depends:` tasks are all `[x]` and that shows no other owner. Set the line to
`- [~] **T03** <title> (owner: <email>, since <YYYY-MM-DD>)`, then sync per topology (push, or save and re-open, or INSERT).
If the line now shows someone else, back off and pick the next eligible task.

### tick / block / unclaim
Change only that task's marker, keep the owner, sync. Append the evidence row to `progress.md` (command or
query, pipeline update id or job run id, result numbers, files, commit or Git folder commit message). On tick, also
update the track's status and done count in `.internal_<email>/index.md`. `[!]` needs a one-line blocker and a challenge entry.
`unclaim` when a person stops without finishing: marker back to `[ ]`, owner removed, note in `progress.md`.

### Time and effort (every task, every piece of work)

The point is a number the team can defend: how long work took with the agent against how long it would have taken by
hand. Times are measured, estimates are labelled as estimates, and nothing is guessed.

- **Clock.** The only clock is the workspace: `current_timestamp()` folded into a query the step already runs (add
  `current_timestamp() AS ts` to the claim-time check and to the verification query; no extra query and no extra
  approval). Never take a time from your own sense of "now"; with no query in a step, write `n/a`, not a guess.
  In org mode the event rows carry `event_ts` and are the source of truth.
- **Per task** (columns in the `progress.md` task log): `Started` (first query after the claim), `Verified` (the
  verification query that passed), `Ticked` (first query after the human's `ok`, normally the next task's start; for
  the last task, the acceptance query), `Agent min` = Verified - Started, `Wait min` = Ticked - Verified (human review
  and idle time), `Fix cycles`, `User-run steps`, `Manual est h` (from the task's `estimate:` line in `tasks.md`).
  Arithmetic is done in the reply, not in a cell.
- **Per track** (`progress.md` **Timeline**): intake started, spec approved, goldfish rounds, implementation started,
  complete, amendments (count, Minor / Major). Spec-phase times come from the spec header.
- **Outside a track** (advice, cost, environment check, model or ontology design, governance assessment, contract, DQ rules, diagnosis,
  release gate): one row in `.internal_<email>/worklog.md` when the deliverable is handed over: date, started,
  finished (first and last query of the work, or `n/a`), skill, request in one redacted line, output file, manual
  estimate, outcome. Propose the manual estimate yourself in the closing message, never blocking:
  `Logged: about 3 h by hand (say "est 5h" to correct).` A correction overwrites the row and marks it `user`.
- **Manual estimate** = time an experienced engineer on this team would need without the agent, for the same output
  and checks. Proposed by the agent with one reason (`2 h: 3 tables, SCD2, hand-written tests`), confirmed or
  corrected by the user at task-list confirmation (tasks) or at hand-over (worklog). Mark the source `agent` or `user`.
- **Rework counts.** Fix cycles, reopened tasks and amendments stay visible next to the time; speed with rework is
  not a saving.
- Org mode: `INSERT ... 'start'` and `'verified'` per task, and one `'worklog'` row per worklog line with
  `note = 'skill=<s>;agent_min=<n>;manual_est_h=<h>;source=agent|user'`.

### productivity report
Scope: a track, a person (`me`), or the team, over a period (default: last 30 days). Read `progress.md` task logs,
`worklog.md` files (or the events table in org mode). Report:
1. Items counted, and items excluded for `n/a` times (say how many; do not fill them in).
2. Elapsed with the agent (Agent min + Wait min) vs manual estimate, per skill and per track type; saving =
   1 - elapsed / manual estimate, shown with the share of estimates confirmed by a user.
3. Rework: fix cycles per task, amendments per track, reopened tasks; challenge count per skill.
4. Against the target in `specs/project-profile.md` (`Productivity target`, for example 80%): met or not, and the three
   skills or task kinds with the lowest saving, as candidates for better instructions.
State in one line that estimates are self-reported and the figure is a trend, not a measurement of people. Never rank
people.

### log challenge
One entry per struggle (template). **Redact before pasting**: tokens, `dapi...`, connection strings, hostnames with
credentials, row values, PII. Paste the error class and message, not query output rows. Resolution is
`RESOLVED`, `WORKAROUND` or `OPEN`; later changes are dated "Update:" lines.

### handover (pass a track or task to a teammate)
1. The current owner (or the lead when the owner is away) says `handover <track_id|T03> to <email>`.
2. Write a handover note at the top of the giver's `progress.md`: date, to whom, state of each open task (done,
   verified, not verified), open challenges, budget used, environment record in use (`specs/env/<env>-<team>.md`),
   next step, and anything only in memory or chat that the next person needs.
3. In `tasks.md`, change the owner on open lines to `(owner: <new email>, from <old email>, since <date>)`; ticked
   lines keep their original owner. Sync per topology; in org mode `INSERT ... 'handover'`.
4. The receiver runs `status`, creates their own ledgers (`create`), copies nothing from the giver's folders, and
   starts with `de-env-check` if their team or environment differs.

### status
1. Read `tasks.md` (order, deps, owners) and every `.internal_*/<track_id>/progress.md` you can read (plain folder) or
   that is on the branch (Git folder); in org mode also `SELECT ... FROM <events table> WHERE track_id = ...`.
2. Report: track and status; done n of m with owner and date per task; in progress and blocked with owner and blocker;
   next claimable task (deps satisfied); open challenges per person. State the topology caveat in one line
   ("Git folder: shows what is pushed"). In a Git folder, flag tasks ticked but not yet committed (no commit carrying
   their `T<nn>` in `progress.md`).
3. `resume` hands off to `de-sdd-implement`.

### who did what
Text claims are self-reported. Cross-check: the Git folder's history and diff in the workspace UI (the user reads
or pastes the commit list), or the events table in org mode. Table: person, tasks claimed and ticked, commits carrying `T<nn>`, challenges
logged, last activity. Disagreements between `tasks.md` and git are listed, not hidden.

### challenges report
Across all `.challenges_*/<track_id>.md` (or all tracks): `OPEN`, `WORKAROUND`, `RESOLVED`, each with person, date,
task, title, lesson. Suggest which lessons belong in `instructions/*.md` or `specs/project-profile.md`.

### archive
When a track is `COMPLETE`, `ABANDONED` or `SUPERSEDED`: set the status in the spec header, `tasks.md` header,
`progress.md` and `index.md`; move nothing. Ledgers older than the retention in `project-profile.md` (default 12 months)
are deleted by the project lead, lessons first copied into `instructions/`.

## Purpose and consent (put this in the project README)

Ledgers exist to make agent work auditable and to turn struggles into reusable lessons, not to rate people.
They are per person, redacted, and anyone may ask the lead to exclude their challenges file from the repo
(`.gitignore` entry) and share only the lessons. Retention is stated in `specs/project-profile.md`.

## Changelog
- 0.6.0: time and effort: task start / verified / ticked times from `current_timestamp()`, manual estimates (agent-proposed, user-confirmed), track timeline, `worklog.md` for work outside tracks, `productivity report`, new event types.
- 0.5.0: QA and gap-analysis fixes: status flags ticked-but-uncommitted tasks in a Git folder; tick updates index.md; evidence carries the update or run id.
- 0.4.0: workspace-only: Git folder UI and bundle Deployments panel replace local CLI and CI steps.
- 0.3.0: ledger writes once per task (fewer save conflicts); handover operation.
- 0.2.0: topology table, UC events table, claim rules with dependencies, status enum, redaction, consent note, index template.
- 0.1.0: initial.
