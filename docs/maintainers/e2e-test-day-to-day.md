# End-to-end test: five day-to-day data engineering requests (easy to complex)

Date: 2026-11-12. Kit: `main` at `434f096` (after the fixes from
[e2e-test-new-source.md](e2e-test-new-source.md)), installed with `install/install_skills` (`32 ok, 0 failed`).

## Why and how

The first end-to-end test (adding a payments file) found that after `approved` the agent built without `tasks.md`,
Validate notes or ledgers, and printed table rows. Those were fixed in general terms (not for that scenario):
- `de-sdd-spec` 0.7.0 never builds and hands over to `de-sdd-implement`;
- `de-sdd-implement` 0.8.0 never skips the Validate block, checks with counts only, and writes fixtures without
  overwrite;
- the guardrails add "no display of data rows to have a look" and "fixtures never overwrite landing files".

This test checks whether those fixes hold, and whether the kit behaves well on **different** kinds of daily work, so
that fixes are not tuned to one scenario.

| # | Level | Request (as a user would type it, minimal detail) | Expected route |
|---|---|---|---|
| S1 | easy | "Did last night's orders load work? How many orders came in?" | `de-run-diagnose`, read-only, no spec |
| S2 | easy | "Amounts in orders should never be negative. Add a check." | `de-sdd-spec` small track, then `de-sdd-implement` (config rule only) |
| S3 | medium | "We also get a daily shipments file from the warehouse. Add it to the orders pipeline." | same kind as the first test: understand the framework, small track, implement with Validate |
| S4 | medium-hard | "Finance wants revenue by region in the daily revenue table." | change to an existing gold table: impact (`de-data-contract` or spec), backfill decision, regression check |
| S5 | complex | "We need a daily net revenue number: payments minus refunds per day and currency, ready for a dashboard." | gold design (`de-data-modeling` or spec section), new table from two sources, DQ, acceptance checks |

Rules for the tester (acting as the user): minimal detail; answer questions with `defaults` unless a default is
wrong; type `approved` only after reading the summary; click **Accept all** when files are pending; **Allow** reads;
**Allow** dev writes only after `approved`, after reading the code (no DROP / DELETE / TRUNCATE / GRANT / overwrite);
**Skip** anything else. Compute: `cluster_uc_dev` only (all-purpose, Unity Catalog, single node); no serverless, no
SQL warehouse. Each scenario starts in a **new** chat from the project's `orchestrator` notebook.

Each step is logged as: intention, what was typed or clicked, what the agent did, verdict (PASS / FINDING / NOTE).

## S1 (easy, read-only): "Did last night's orders load work? How many orders came in?"

- **Typed** (new chat from `orchestrator`): `Did last night's orders load work? How many orders came in? Use only cluster_uc_dev.`
- **Agent:** read its memories and `AGENTS.md`, then **Read de-run-diagnose skill** (loaded by itself). Three steps:
  1. `SELECT` on the audit table (recent runs): tester checked, Allow;
  2. `SELECT ... FROM LIST('/Volumes/.../landing/orders')`: **failed** `NO_SUCH_CATALOG_EXCEPTION ... default.list`
     (`LIST` is a SQL statement, not a table function);
  3. retried by itself with `dbutils.fs.ls(...)` plus table counts: Allow.
- **Answer:** "No nightly load ran last night, so no new orders came in." Reasons with evidence: both jobs are paused
  (as set in T13) and never ran; the landing folder still holds only the two sample files from 11 Nov; the only run
  overnight was this morning's manual payments test (run id given), all steps succeeded, 0 new orders, 6 payments.
  Counts: bronze `orders_raw` 8, silver `orders` 5, quarantine 2, with why 8 becomes 5. "I didn't change anything."
  Offered next steps: unpause the job, or run it once.
- **Verdict:** PASS: right skill without `@`, read-only, counts only, honest "nothing ran" rather than a guess,
  evidence with run id.
  FINDING (minor, kit): one failed query from `FROM LIST(...)`; and the failure was not logged as a challenge (kit
  rule: a failed query is a struggle). Proposed fix: one line in `de-run-diagnose` "list files in a volume with
  `dbutils.fs.ls` or the `LIST '<path>'` statement, never `FROM LIST(...)`", and the challenge rule repeated in its
  read-only checks.

## S2 (easy change): "Amounts in orders should never be negative. Add a check."

- **Typed:** `Amounts in orders should never be negative. Add a check for that in our orders pipeline. Use only cluster_uc_dev.`
- **Agent:** **Read de-sdd-spec skill** as its first skill step (the trigger fix for "change an existing pipeline"
  worked). Discovery: read `seed_orders` and the rules table. One query failed: it guessed a column `run_ts`
  (`UNRESOLVED_COLUMN`); it retried with the right column.
- **Finding the agent made:** "I didn't add anything, because the orders pipeline already has this check": rule 1003
  `valid_amount` (`amount IS NOT NULL AND amount >= 0`), Blocker, on silver orders; 1 negative bronze order is in
  `orders_quarantine` with that reason; silver and gold are clean; payments allow negatives on purpose (refunds).
  Offered an optional post-load backstop.
- **Verdict:** PASS (best possible outcome: no duplicate work, evidence-backed).
  NOTE: one suggested follow-up was "Show the quarantined negative order" (would print a row); not clicked.

### S2b: the user accepts the offer (tests the approval to implement handoff)

- **Typed:** `Yes, add the post-load check that fails the job if a negative amount ever reaches silver orders.`
- **Agent:** read-only pre-check in one query (free rule ids, name not taken, live count = 0, and a dry run of the
  rule expression on four literal test amounts: catches exactly the negative one). Wrote a small-track spec
  (`neg_amount_small_20261112`) and showed in **one approval summary** the rule, what it can and **cannot** test
  ("the job actually failing on a negative row: silver has none, and writing one into it isn't allowed") and the
  task list T01, T02.
- **Tester:** **Accept all**, `approved`.
- **Agent after approval** (fixed behaviour): "Now I'll create tasks.md and progress.md, and add the track to the
  index" (created `tasks.md`, `.internal_<me>/.../progress.md`, edited `index.md`), then "Starting T01".
- **T01:** one cell in `seed_orders` (+12 lines) and a `MERGE` of rule 1018 with a before / after check that the other
  45 rules are unchanged.
  - Genie Code's platform check blocked the `MERGE` ("mutation ... not safe unless explicitly non-destructive and
    reviewed"). In the first test the same kind of `MERGE` ran without a block, so the platform is not consistent.
  - Tester read it: the approved change, dev, idempotent upsert of one config row: clicked **Run**.
  - First attempt failed in the agent's own checksum (`sum(xxhash64(...))` overflow under ANSI) **before** the write;
    it said so ("nothing was written"), fixed the checksum and re-ran.
  - Result: **Validate T01** block with a check / expected / actual table and "Reply ok to tick T01".
- **Tester:** `ok, go on with T02`.
- **T02:** ran the existing `dq_runner` for `sales_orders` (test mode, its own run id) and checked `dq_result` in the
  same call: 12 rules, 9 PASS, 3 WARN, 0 FAIL; rule 1018 PASS. **Validate T02** with the exact query
  (`... run_id = 'neg_t02_r1' AND rule_id = 1018 AND status = 'PASS'`), a suggested commit message per task, and
  "Reply ok to tick T02 and mark the track COMPLETE. The track took about 20 minutes with me, against a 1.x h manual
  estimate."
- **Tester:** **Accept all**, `ok`. Agent: "The track is now COMPLETE", records updated.
- **Verdict:** PASS on everything the earlier test missed: `tasks.md`, ledgers, Validate per task, tick on `ok`,
  COMPLETE only after `ok`, time line against the manual estimate, counts only (no rows displayed).
  FINDINGS (general, fixed): guessed column name; checksum overflow. Added to
  `instructions/data-engineering-conventions.md` "Learned in live tests (2026-11-12)": read columns before the first
  query on a table, list volume files with `dbutils.fs.ls` or `LIST '<path>'`, avoid integer checksum overflow.
  FINDING (guide, fixed): the troubleshooting row "click Cancel on a safety block" was too strict; now: Run when the
  code is exactly the approved dev change and does not delete or overwrite; Cancel otherwise.

## S3 (medium, same kind as the first test): "We also get a daily shipments file from the warehouse. Add it."

- **Typed:** `We also get a daily shipments file from the warehouse. Add it to the orders pipeline. Use only cluster_uc_dev.`
- **Agent:** first message: "This is a new source requirement for the existing orders pipeline, so per the project's
  SDD rules I need to run it through the spec process" (no `go ahead` needed this time). Read the payments spec as a
  template, the pipeline config, and the data model, which "already sketches shipment fields, all [ASSUMED]".
  Two config reads; the first guessed column names and was retried "with correct column names" (the new
  read-columns-first convention was not installed yet at this point).
- **Questions:** one round of 5 (format and path, fields from `model.md`, history SCD1 on `shipment_id` sequenced by
  `ship_ts`, gold `fact_shipment` deferred, DQ), each with a recommended option. Tester: **Accept all**, `defaults`.
- **Spec:** `specs/shipments_small_20261112/spec.md` (175 lines), read back after writing. Summary: bronze
  `shipments_raw` (dataset 108), silver `shipments` (109, SCD1) and quarantine, rules 1028 to 1035, 2 synthetic
  files with 1 dirty and 1 orphan record, AC-S1..S8, "Compute: cluster_uc_dev only, no job submissions".
  - FINDING (minor): the summary did **not** list the tasks (S2b did), so `approved` covered only the spec.
  - Checked: the "specs/shipments..." label is shortened in the UI; the folder is under `pogo-test/specs/`. PASS.
- **Tester:** **Accept all**, `approved`.
- **Agent after approval:** "spec is APPROVED. Now let me write tasks.md and update the ledgers ... Then I'll load
  de-sdd-implement and start working." Created `tasks.md` (+45), `progress.md`, the index row and the project
  profile section, loaded the implementation skill, claimed T01. **PASS** (handoff fix holds in a second scenario).
- **T01 (seed config and samples):**
  - 3 seed cells in `seed_orders` (+92 lines);
  - samples: first try `open(path, "w")` in the new `landing/shipments` folder: Genie Code blocked it ("open in write
    mode ... can overwrite"); tester clicked **Cancel** (guide rule for overwrites); the agent retried with
    `dbutils.fs.put(..., overwrite=False)` (the kit's fixture rule). Allow. **PASS** (recovery).
  - 3 `MERGE` steps (108; 109 plus rules 1028 to 1032; rules 1033 to 1035): tester checked each (no DROP / DELETE /
    overwrite; `MERGE ... UPDATE SET *`), Allow. No platform block this time (inconsistent platform, as in S2b).
  - Verify (read): "2 dataset rows, 8 DQ rules, 2 landing files".
  - **FINDING (major):** then "Let me tick T01 and move to T02": it ticked T01 itself and asked to run the
    orchestrator, with no Validate block and no `ok`. The tester clicked **Skip** and typed `Wait. You ticked T01
    without showing me a Validate step. Show me the T01 check first; I'll reply ok before you run anything for T02.`
    The agent: "You're right, I should have shown the Validate block and waited for your ok before ticking", then a
    proper block: done line, count-only Validate query (check / actual / expected) "run on cluster_uc_dev or SQL
    editor", "Reply ok to confirm T01". Tester: **Accept all**, `ok`.
  - **Fix (general):** `de-sdd-implement` 0.8.1 puts a **stop rule** at the very top: the Validate block ends the
    turn; the next task starts only in a new turn after `ok` (or `auto`). The rule existed in the loop section, but in
    a long turn it was skipped; a turn boundary is easier to follow than a rule in a paragraph.
- **T02 (run and acceptance):** orchestrator run on `cluster_uc_dev` (dev catalog, existing notebook): tester Allow.
