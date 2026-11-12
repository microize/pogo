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
  The run took about 10 minutes (9 datasets on a single node) and succeeded (run id `ship_t02_...`, 34 rules, 4 steps).
  Acceptance checks: one count-only query (check / actual / expected, `display()` of counts, not rows): bronze 6,
  silver 5 and 5 distinct ids, quarantine 1, orphan WARN 1, key unique PASS 1, 8 DQ rows, orders unchanged 5,
  payments unchanged 6; a file search for AC-S8 (only `seed_orders` mentions shipments under `src/`). Then the
  **Validate T02** block and "Reply ok to tick T02 and complete the track" (this time it waited).
- **Tester:** **Accept all**, `ok`. Agent: "Track shipments_small_20261112 is COMPLETE ... Spec items not met: none.
  Items built not in the spec: none. You still need to Commit & Push with message
  `feat(shipments_small_20261112): T01-T02 complete`."
- **Verdict:** PASS with one major finding (auto-tick of T01, fixed in 0.8.1) and one minor (no task list in the
  summary, fixed in `de-sdd-spec` 0.7.1). Compared with the first test (payments): tasks, ledgers, Validate blocks,
  fixtures without overwrite, counts only, "not met / not requested" list and Commit & Push reminder all present.

Fixes after S3 were pushed (`b9a64da`) and installed (`32 ok`) before S4.

## S4 (medium-hard, change an existing gold table): "Finance wants revenue by region in the daily revenue table."

- **Typed:** `Finance wants revenue by region in the daily revenue table. Use only cluster_uc_dev.`
- **Agent:** **Read de-sdd-spec skill** first. Discovery, then: "this would be a new track `region_revenue_20261112`,
  small; changing the grain normally calls for a fresh-eyes review". It reported `fact_daily_revenue_by_segment`
  (dataset 105, `sql_overwrite`, 4 rows) and claimed **"No region field exists anywhere"**, proposing a
  country-to-region mapping table.
- **FINDING (major, discovery):** wrong. `silver_sales.orders.region` exists. Cause found later in the chat: its
  search used `information_schema.columns ... ilike '%region%'`, which returned **no rows** for this catalog, while
  `DESCRIBE` shows the column. An absence claim was made from one metadata source without confirming.
- **Tester (a user who knows the data):** `Our orders already carry a region (silver orders has a region column).
  Finance means that one, not a country mapping. Please re-check and adjust the questions.`
- **Agent:** ran `DESCRIBE` plus the `information_schema` search (metadata only, Allow), then a grouped profile
  (counts and sums by region, status, currency: aggregates only, Allow). "You're right, I missed it ... My first
  discovery only described the gold tables ... I'll log this miss as challenge C1." Reconciled: non-cancelled silver
  revenue 570.50 equals the gold total, so region only splits rows; APAC appears only in quarantine; bronze has no
  region (silver derives it from the shipping field). Revised questions: where (column in the existing table,
  recommended), name (`order_region`), missing region (UNKNOWN plus a Major warning above 10%, today 2.6%), cleaning.
- **Tester:** `defaults`.
- **Spec v1:** `order_region` in the gold table and its test copy (UNKNOWN for missing); rule 1013 (grain unique)
  extended; new Blocker rules (missing region 1019, region totals = silver totals 1038); warnings (UNKNOWN share
  1036, unexpected region value 1037); same rules for the test pipeline. **Expected live result worked out before
  building:** 5 rows instead of 4, totals unchanged per currency, warning 1036 fires once (UNKNOWN 20% of one day's
  EUR revenue), test table stays 10 rows. **Impact flagged:** "Anything reading this table that assumes one row per
  day, segment and currency will now need to sum across regions. I've assumed no dashboard reads it yet; please
  confirm." Challenges C1 (missed column) and C2 (wrong column name) logged in `.challenges_<me>/`. "As you chose,
  next is the fresh-eyes review. Open a new Genie Code chat and run `@de-goldfish-review ...`".
- **Verdict so far:** PASS on depth (impact, reconciliation, expected results, challenge log, goldfish for a grain
  change). FINDING fixed in general terms (conventions): "an absence claim ('no column X') needs `DESCRIBE` of the
  candidate tables, not only `information_schema`; search silver and bronze before proposing a new source of truth."
- **Fresh-eyes review:** new chat, typed `Goldfish review with fresh eyes of specs/region_revenue_20261112/spec.md
  ...`: **Read de-goldfish-review skill**, read only the spec.
  The reviewer **ran queries** (DESCRIBE, a config read, a simulation of the new grain) and one
  `select * from gold...fact_daily_revenue_by_segment` (4 aggregate rows, no personal data).
  - FINDING (minor): `de-goldfish-review` says it reads only the spec and the files it references; querying data
    (and `SELECT *` of a gold table) is outside that. Fix: the reviewer may run metadata and count-only checks to test
    a claim, never `SELECT *`.
  - FINDING (process): the guardrail change ("no SELECT * to have a look") is in the kit's `instructions/`, but
    `pogo-test` has its own copy of `instructions/` and was not updated. Kit updates to `instructions/` do not reach
    existing projects. Fix: release note and a sync step in setup (see "Changes made").
  - Review result: "READY FOR APPROVAL" with 0 Blocker, 3 Major, 5 Minor, written to `review_1_<me>.md`:
    G1 rule 1036 written in words, not SQL (and the zero-revenue case); G2 unknown whether the `sql_overwrite` loader
    can add a column; G3 "nobody reads the table" only assumed; plus 5 minors (constraint wording, UNKNOWN values,
    fixture coverage, an out-of-date grain comment, catalog placeholder).
- **Resolve:** typed `resolve review` (it landed in the review chat because the tab switch failed; the kit allows
  resolving in any chat). **Read de-sdd-spec skill**. Investigated before proposing:
  - G2: read the gold loader: it creates the table once, fails if columns differ, and **writes by position**: "the
    first run with the new query will fail unless the column is added to the table first, in the same position as
    in the query". A real defect caught by the review.
  - G3: lineage not readable (no `system.access`; logged as challenge C3); fallback: no view references the table,
    and a workspace search found only `seed_orders`.
  - A table of proposed exact edits per finding; "Reply accept all, or name the ids". Tester: `accept all`.
  - It tested the rewritten rule 1036 SQL on a simulated fact before asking for approval.
- **Approval summary:** spec v2 and "Tasks, approved together with the spec": T01 config and column, T02 run both
  pipelines "after you give the go", T03 close-out ("Commit & Push is yours"). Tester: **Accept all**, `approved`.
- **After approval:** **Read de-sdd-implement skill**, **Read de-sdd-tracking skill**; header set to `Status:
  APPROVED (by <me>, 2026-11-12)` with a Decision Log row quoting "approved"; `tasks.md` and progress ledger created.
  "Starting T01: config change. Files: seed_orders, seed_orders_fixtures. Verification: column order, AC-R9, rule
  rows, config validation." Claimed.
- **T01:**
  - `ALTER TABLE ... ADD COLUMN order_region STRING AFTER customer_segment` on the live and test fact tables, guarded
    by "if not in columns", with `DESCRIBE HISTORY` versions recorded first (rollback points: version 6 live, 4 test).
    Genie Code blocked it ("adding a column is a mutation"); tester read it (approved change, dev, additive) and
    clicked **Run**.
  - Config `MERGE`s for datasets 105 / 205 and rules 1019, 1036 to 1038, 2020 to 2023 (rule rows 54 to 62). The
    tester's keyword scan flagged "drop": it was a SQL comment and the value `sql_overwrite`; Allow.
  - Verify: column order, AC-R9 on literal values, 10 rules active, dry run of the new queries without writing
    (5 rows live, 10 test), config validation passes; transition risk named ("until T02 rebuilds the live table,
    its 4 rows have a NULL order_region; rule 1019 would fail").
  - **Validate T01** block: "Validate (SQL editor, or a new cell of a scratch notebook on cluster_uc_dev)", count-only
    query; **then it stopped** (stop rule 0.8.1 works).
- **Tester:** **Accept all**, `ok, go with T02`. T02: orchestrator for the live and test pipelines (dev, existing
  notebook): Allow.
- **T02:** both pipelines ran in the session on `cluster_uc_dev` (no job submitted): `sales_orders` 8.1 min,
  `sales_orders_fixtures` 6.9 min, SUCCESS through all four steps, no FAILED audit rows. It read the result tables'
  columns before querying them. Acceptance (count-only): order_region present; 0 duplicate keys; 5 rows with
  2026-11-11 RETAIL EUR split into EMEA 60.00 and UNKNOWN 15.00; totals EUR 270.50 and USD 300.00 unchanged; rule
  1036 WARN once; 1038 PASS; 1019 and 1037 PASS; test data 10 rows all PASS; no failed rules. All exactly as the spec
  predicted before building. Validate T02 block; stopped. Tester: **Accept all**, `ok`.
- **T03 (close-out):** progress ledger (+55 lines), index, a runbook note for the new grain; final acceptance run;
  "Spec items not met: none. Built but not requested: none. The ALTER step and AC-R1b came from goldfish finding G2,
  which is in the Decision Log." **"Track time: about 57 minutes with the agent (including the spec, the goldfish
  review and 15 minutes of pipeline runs) vs a 2.0 h manual estimate."** Validate block with expected values.
  Tester: `ok`. A separate approval was spent on `SELECT current_timestamp()` for the completion time (minor: the
  kit says fold it into an existing query). Agent: "Track region_revenue_20261112 is now COMPLETE ... with a Decision
  Log row quoting your ok", plus the Commit & Push messages to use.
- **Verdict:** PASS. Biggest value of the kit seen so far: the fresh-eyes review caught a defect (positional loader
  write) that would have failed the first run. Biggest gap: discovery claimed a column did not exist (fixed by the
  absence-claim convention).

## S5 (complex, new gold measure from two sources): "Finance needs a daily net revenue number, payments minus refunds per day and currency, ready for a dashboard."

- **Typed:** the request plus `Use only cluster_uc_dev.`
- **Agent:** **Read de-sdd-spec skill**; discovery of payment and refund tables (metadata) and of the payment rules.
  - FINDING (major, guardrail): one discovery step ran `display(SELECT payment_id, order_id, amount_raw, ...
    FROM silver_sales.payments_quarantine)`: data rows in chat (synthetic data here). The counts-only rule was only in
    `de-sdd-implement` and in the kit's guardrails (which `pogo-test` does not have, see S4). **Fix:** `de-sdd-spec`
    0.7.2: "discovery queries return metadata, counts, distinct counts and grouped totals only, never rows of data
    tables", plus the absence-claim rule from S4. The tester's helper missed it too (it only caught `SELECT *`);
    tightened.
  - Findings it reported: no refunds feed (a refund is a negative payment amount, e.g. P-2005 -50.00); one orphan
    payment already warned by rule 1026; currencies never mixed. A preview of the result on today's data (4 rows).
  - Round 1, 5 questions with recommended options: how to spot a refund; which date decides the day (`paid_at` UTC);
    where the result goes (new table `gold_sales.fact_daily_net_revenue` recommended; metric view or extra columns as
    options); which payments count (all valid, including orphans and cancelled orders, "since this is a cash view");
    which checks (duplicate key and totals Blockers, negative-day warning); plus "should this track build the
    dashboard itself? I'll assume table only". "Once you answer, I'll write the spec ... and two to three tasks for
    one approval."
  - FINDING (minor): `de-data-modeling` was not loaded although this is a new gold fact for a dashboard;
    `de-sdd-spec` says to load it for facts and KPIs. The design was sound (grain, measures, checks), but no
    `model.md` was updated. Left as is (judgement call for a one-table fact); noted for the next trigger review.
- **Tester:** `defaults`. Spec v1 summary: target and grain (one row per day and currency), columns (gross payments,
  refunds as a positive number, net revenue, counts), refund rule, which payments count, built as config dataset
  110 with no new code, rules 1039 (duplicate key, Blocker), 1040 (totals match silver, Blocker), 1041 (negative
  day, warning), expected result (EUR 195.50 and USD 200.00 on 11-10; EUR -50.00 and USD 100.00 on 11-11; total
  445.50 equals silver), not included (dashboard, currency conversion, refunds feed), **tasks T01 to T03 in the
  summary**, manual estimate about 3 h, "skips the fresh-eyes review" (small track). Tester: **Accept all**,
  `approved`.
- **After approval:** **Read de-sdd-implement**, **Read de-sdd-tracking**, approval timestamp, `tasks.md`, ledgers.
- **T01:** new last cell in `seed_orders` (dataset 110, rules 1039 to 1041). Applying it took three attempts: the
  agent extracted the `MERGE` statements from the notebook source at run time and its `# MAGIC` prefix stripping
  failed twice before the third version worked. Genie Code blocked the `MERGE` once; tester read it (approved dev
  config) and clicked **Run**.
  - NOTE (tester error): the tester's helper auto-allowed the first of these steps because the `MERGE` text was
    built at run time; it was the approved change, so no harm, but every later write was read by hand.
  - Verify: config validation passes (10 datasets, 41 rules); the table query previews 4 rows and 445.50; rule
    previews 1039 = 0, 1040 = 0, 1041 = 1; and a **negative test**: rule 1040 caught a deliberately broken copy of
    the data in a temporary view (one changed and one missing row: 2 failures).
  - Validate block "run in the SQL editor, or a new cell of a scratch notebook on cluster_uc_dev, not a pipeline
    notebook"; "verified, but not ticked until you say ok". Tester: **Accept all**, `ok, go with T02`.
- **T02:** snapshot, then only the gold and DQ steps of the pipeline (not bronze and silver) on `cluster_uc_dev`.
- **T02 results:** run `nr_t02_r1`: gold step wrote 4 rows to the new table and rewrote the other gold tables with no
  data change; DQ 22 rules, 15 PASS, 7 WARN, 0 FAIL. Run `nr_t02_r2`: a second gold pass to prove a re-run gives the
  same result. AC-NR1 to AC-NR7 pass. Validate block; waited. Tester: **Accept all**, `ok`.
- **T03 (PR review) loaded `de-release-gate`:** listed files with a shell cell (`ls`, `grep`; read-only; minor:
  `AGENTS.md` says use the file tools, not shell cells). Verdict **BLOCK**: "B1: no test for the new calculation
  (Blocker) ... a missing test I should have planned"; logged as challenge C2. Proposed **amendment 2 (Minor)**:
  T02b unit tests and T02c runbook section, and asked for `approved`. Tester: `approved`.
  - **T02b:** `tests/orders_nb_framework/unit/test_net_revenue.py`, 11 tests on hand-made rows in temporary views
    (nothing written to tables): payment and refund on the same day and currency, zero amount, refund-only day,
    23:59:59 vs 00:00:00 UTC, two currencies, and each rule failing on bad input. Run through the existing
    `test_common` notebook (which gained two optional widgets). A **mutation test** proved the tests fail on a
    deliberately broken transform. Validate; waited.
  - **T02c:** runbook section 9 (table, business rules, the expected 1041 warning, what to do when 1040 fails, with a
    diagnostic query it tested as a count).
  - **Second review `pr_review_2.md`: APPROVE** (B1, A1, N2 resolved; secrets grep clean; no cache folders).
- **Close:** tester `ok. I'll do the Commit & Push myself later; close the track.` Final acceptance rerun: AC-NR1 to
  NR7 pass, 53 tests pass, existing revenue table unchanged (identical checksum), re-run identical. "Not met: nothing.
  Built beyond the original spec: clustering and gold step order (amendment 1); the tests and runbook (amendment 2,
  which you approved); optional widgets on test_common." **"Time: about 45 minutes from request to close, against a
  4.5-hour manual estimate."**
- **FINDING (major, process):** amendment 1 was recorded as approved because "your ok on T01 covered it". An `ok`
  to a Validate block is not approval of a spec change. **Fix:** `de-sdd-implement` 0.8.2: "An ok to a Validate block
  ticks the task only; it never approves an amendment. Ask for the amendment on its own line and quote that reply."
- **FINDING (minor, repeated in S4 and S5):** three separate approvals were spent on `SELECT current_timestamp()` only.
  **Fix:** `de-sdd-implement` 0.8.2: "Never run a query only to get a timestamp."
- **Verdict:** PASS. The release gate caught a real gap (no test for new logic) and the agent closed it through an
  approved amendment, with a mutation test proving the tests work.

## Summary

| # | Request | Skills used | User messages | Result | Time with agent vs manual estimate |
|---|---|---|---|---|---|
| S1 | Did last night's load work? | de-run-diagnose | 1 | honest "nothing ran", evidence with run id, counts only | about 3 min (no estimate; read-only) |
| S2 | Amounts never negative: add a check | de-sdd-spec, then de-sdd-implement | 1, then 5 for the backstop | found the rule already exists; backstop rule 1018 built with tasks, ledgers, Validate per task | about 20 min vs 1.x h |
| S3 | Add a daily shipments file | de-sdd-spec, de-sdd-implement, de-sdd-tracking | 6 (plus one correction) | 2 datasets and 8 rules by config only; 10 acceptance checks pass; orders and payments unchanged | about 35 min (manual estimate in tasks.md) |
| S4 | Revenue by region in the daily revenue table | de-sdd-spec, de-goldfish-review, de-sdd-implement, de-sdd-tracking | 8 (plus one correction) | grain change with impact check, review caught a positional-write defect, results exactly as predicted | about 57 min vs 2.0 h |
| S5 | Daily net revenue (payments minus refunds) for a dashboard | de-sdd-spec, de-sdd-implement, de-sdd-tracking, de-release-gate | 8 | new gold fact, 3 rules, release gate blocked for a missing test, tests and runbook added by amendment, gate approved | about 45 min vs 4.5 h |

**What the fixes from the first test changed (S2 to S5 vs the payments test):**
- After `approved` the agent loaded `de-sdd-implement` and `de-sdd-tracking` every time (4 of 4), wrote `tasks.md`,
  ledgers and the approval row, and ended each task with a Validate block.
- Sample files: the second attempt always used a safe form (`overwrite=False`, a new folder).
- One regression in S3 (auto-tick of T01) led to the stop rule; S4 and S5 then stopped after every Validate block.

**Where the kit added the most value:** the fresh-eyes review (S4: a loader that writes by column position would
have failed the first run) and the release gate (S5: no test for new logic), plus up-front expected results that the
runs then matched exactly.

**What still needs a person:** correcting wrong discovery (S4 region column), clicking **Run** on Genie Code's
generic write blocks, Commit & Push, and the dashboard itself.

## Findings and changes made

| # | Scenario | Finding | Severity | Change |
|---|---|---|---|---|
| 1 | S3 | ticked T01 and started T02 in the same turn, no Validate, no `ok` | Major | `de-sdd-implement` 0.8.1 stop rule at the top: the Validate block ends the turn |
| 2 | S3 | small-track approval summary lacked the task list | Minor | `de-sdd-spec` 0.7.1: the summary ends with the task list |
| 3 | S1, S2, S3 | failed queries from guessed columns, `FROM LIST(...)`, integer checksum overflow | Minor | `instructions/data-engineering-conventions.md`, "Learned in live tests (2026-11-12)" |
| 4 | S4 | "no region field exists anywhere" (information_schema incomplete) | Major | conventions plus `de-sdd-spec` 0.7.2: absence claims need `DESCRIBE` in every layer |
| 5 | S4 | goldfish reviewer ran `SELECT *` on a gold table | Minor | `de-goldfish-review` 0.4.1: metadata and counts only |
| 6 | S4 | kit `instructions/` updates do not reach existing projects | Major (process) | user guide page 2, "To update later": compare and copy `AGENTS.md` and `instructions/` into each project |
| 7 | S5 | discovery displayed quarantine rows | Major (guardrail) | `de-sdd-spec` 0.7.2: discovery is counts / metadata only |
| 8 | S5 | an amendment counted as approved from a task `ok` | Major | `de-sdd-implement` 0.8.2: `ok` never approves an amendment |
| 9 | S5 | approvals spent on timestamp-only queries | Minor | `de-sdd-implement` 0.8.2 |
| 10 | S2, S3, S4, S5 | Genie Code platform blocks writes inconsistently | Note | user guide page 7: Run when the code is exactly the approved dev change and non-destructive |
| 11 | S5 | `de-data-modeling` not loaded for a new gold fact | Minor | not changed (judgement call for a one-table fact); watch in trigger tests |
| 12 | S5 | shell cell (`ls`, `grep`) used to list project files | Minor | not changed (rule already in `AGENTS.md`); watch |

**Test method notes (honest):** the tester used a small browser helper to expand and pre-check Allow prompts. It
missed one write in S5 (statements built at run time) and two row displays (S4 goldfish, S5 discovery); those were
caught on review afterwards and are logged above. Writes were otherwise read by hand before Allow. Screenshots
stopped working mid-test (the page became too heavy), so steps after S1 are logged from page text.
