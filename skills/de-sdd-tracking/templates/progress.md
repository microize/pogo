# Progress: <track_id>

| Field | Value |
|---|---|
| Owner | <email> |
| Spec | `specs/<track_id>/spec.md` v<version>, APPROVED <date> |
| Tasks | `specs/<track_id>/tasks.md` |
| Status | IN PROGRESS \| BLOCKED \| COMPLETE |
| Started | <YYYY-MM-DD> |
| Last update | <YYYY-MM-DD HH:MM> |

**Next:** T01 <title>

## Timeline (times from `current_timestamp()`; `n/a` when no query ran, never a guess)

| Event | Time | Note |
|---|---|---|
| Intake started | <YYYY-MM-DD HH:MM> | from spec header |
| Spec approved | | from spec header |
| Goldfish rounds | | count, Blockers found |
| Implementation started | | first task claimed |
| Complete | | human OK on the final Validate table |
| Amendments | | count Minor / Major |
| Manual estimate, whole track | <h> h (agent \| user) | sum of task estimates plus spec and design |

## Task log

| Date | Task | Status | Files | Verification (command, update or run id, result) | Table version before (optional) | Commit |
|---|---|---|---|---|---|---|
| | T01 | [x] | `databricks.yml` | Deployments panel deploy to `dev` succeeded | - | abc1234 |

## Time per task (see `de-sdd-tracking`, "Time and effort")

| Task | Started | Verified | Ticked | Agent min | Wait min | Fix cycles | User-run steps | Manual est h (source) |
|---|---|---|---|---|---|---|---|---|
| T01 | 2026-11-12 10:02 | 2026-11-12 10:09 | 2026-11-12 10:15 | 7 | 6 | 0 | 0 | 0.5 (user) |

## Decisions taken while implementing (not spec changes)

| Date | Task | Decision | Why |
|---|---|---|---|

## Acceptance criteria results (fill at the end)

| AC | Result | Evidence | Verified by |
|---|---|---|---|
