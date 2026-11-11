# Fixture tests for SQL Lakeflow pipelines

Pipeline unit tests in the editor are Beta and Python-only; SQL pipelines are tested end to end on tiny synthetic data.

1. **Cases first.** One row per behaviour in the spec: late file, out-of-order change, same-timestamp tie, duplicate
   resend, bad row to quarantine, NULL sequence, unknown dimension member. Each case has an id (FX-A...), the input
   records, and the expected result as a pass/fail query.
2. **Files.** Synthetic JSON or CSV under `tests/fixtures/<track_id>/` with fake identities (`example.test` emails,
   "Test User" names). Order-sensitive cases use separate files and record the required modification order.
3. **Isolation.** A separate test volume (never a subfolder of the real landing path, which ingestion would pick up),
   and a `dev_fx` bundle target whose pipeline writes to separate `<schema>_fx` schemas through configuration. Schema
   names must come from configuration, not literals in SQL, for this to work.
4. **Loading in steps.** Upload files with `overwrite=False`; for late-arrival cases run one update, upload the late
   file, run a second update. Record the update ids.
5. **Assertions.** `tests/fixtures/<track_id>/expected.sql` with one pass/fail row per case (same shape as
   `templates/dq-checks.sql`); run on the warehouse after the last update; paste the result into `progress.md`.
6. **Cost.** Dry-run first, then at most two real updates per fixture run; clean the `_fx` schemas only through a
   tracked task (no DROP by the agent; guardrails).
