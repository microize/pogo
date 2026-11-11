# Release readiness <n>: <track_id>

| Field | Value |
|---|---|
| Date / by | <YYYY-MM-DD> / <email> |
| Spec | `specs/<track_id>/spec.md` v<version> |
| Bundle target | prod (prod workspace Git folder: <path>; release branch: <release/track-n>) |
| Verdict | GO \| CONDITIONAL_GO \| NO_GO |

## Scorecard

| Area | Result | Evidence |
|---|---|---|
| Bundle and environments | PASS / WARN / FAIL | |
| Identity and grants | | |
| Compute | | |
| Secrets | | |
| Data quality gate | | |
| SLA and schedule | | |
| Observability | | |
| Rollback | | |
| Tests | | |
| Operations | | |
| Governance | | |

## Blockers (NO_GO)

| # | Blocker | Owner | Resolution | Date |
|---|---|---|---|---|

## Conditions (CONDITIONAL_GO)

| # | Condition | Owner | Must be done by |
|---|---|---|---|

## Rollback plan

- Previous release branch: `<release/...>`; steps: switch the prod Git folder to it, deploy `prod` from the Deployments panel (run by <who>).
- Tables with time travel retention at least 7 days: <list>.
- AUTO CDC targets needing backfill on rollback: <list or none>.

## Deploy steps (user-run in the prod workspace, never by the agent)

1. In the Git folder dialog, pull, then create and switch to branch `release/<track_id>-<n>`.
2. Open `databricks.yml`, open the Deployments panel (rocket icon), select target `prod`.
3. Deploy; confirm it finishes without errors (deploying validates the bundle).
4. Run the post-release validation query from the runbook.

## Sign-off

| Role | Name | Date |
|---|---|---|
| Data owner | | |
| Platform | | |
