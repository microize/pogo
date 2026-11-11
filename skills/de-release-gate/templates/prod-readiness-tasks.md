# Prod-readiness tasks: <track_id> (from release gate <n>)

Track type: small | Source: `specs/<track_id>/release_<n>.md` | Owner team: <team>
Each FAIL and WARN from the scorecard becomes one task. Human-only steps are marked `user-run` or `admin`.

- [ ] **P01** Prod environment checked (`de-env-check` in the prod workspace): compute, quota share, system tables
  - depends: none | verify: `specs/env/prod-<team>.md` exists, no Blocking items
- [ ] **P02** Prod catalog and schemas exist; names in bundle `prod` target variables
  - depends: P01 | admin: create catalog / schemas | verify: `SHOW SCHEMAS IN <prod catalog>`
- [ ] **P03** Service principal for `run_as`, with least-privilege grants (written for a human)
  - depends: P02 | admin: create SP, run the GRANT statements | verify: `SHOW GRANTS` lists only the needed privileges
- [ ] **P04** Bundle `prod` target: `mode: production`, `run_as`, `workspace.host`, `root_path`, no personal paths
  - depends: P03 | verify user-run: in the prod workspace's Git folder, the Deployments panel lists the `prod` target and the dev target deployed without errors
- [ ] **P05** Job: schedule or trigger per spec, `max_concurrent_runs: 1`, retries, timeout, DQ checks task failing on Critical
  - depends: P04 | verify: job definition in bundle; dev run of the job succeeded
- [ ] **P06** Alerts: failure notifications to a team channel; freshness and volume alert or Data Profiling
  - depends: P05 | verify: alert definitions present; test notification received
- [ ] **P07** Governance: PII tags and masks per contract; contracts `active` with owner team
  - depends: P02 | verify: `information_schema.column_tags`; contract status
- [ ] **P08** Rollback and runbook: release-branch plan, retention >= 7 days, backfill plan for AUTO CDC targets, runbook page
  - depends: P04 | verify: runbook file; `SHOW TBLPROPERTIES` retention
- [ ] **P09** Open follow-ups from the PR gate closed or accepted in the Decision Log
  - depends: none | verify: each finding has a task or a dated acceptance
- [ ] **P10** Re-run the prod gate
  - depends: P01..P09 | verify: verdict GO; the human deploys `prod` from the Deployments panel in the prod workspace
