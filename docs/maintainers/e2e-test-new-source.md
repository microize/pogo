# End-to-end test: add a new data source to an existing pipeline (user role, minimal detail)

Date: 2026-11-12. Workspace: the kit's test workspace (Azure). Kit: `main` at `18054d4`, installed with
`install/install_skills` (`32 ok, 0 failed`).

## Goal of the test

Check that a user who gives **minimal detail** can get a new source integrated into an **existing** pipeline, and that
the kit:
1. understands the existing setup before proposing anything (reads the project, the existing spec, tables, config);
2. asks only the questions it needs, each with a recommended answer;
3. writes a spec and **waits for `approved`** before building;
4. builds task by task in dev, with a Validate check per task;
5. runs only on the all-purpose cluster the user names.

## Setup

| Item | Value |
|---|---|
| Project | Git folder `pogo-test` (track `orders_nb_framework_20261111`: metadata-driven orders pipeline, notebooks + config tables, bronze / silver / gold / DQ, orchestrator notebook) |
| Compute | `cluster_uc_dev`: all-purpose, single node, Dedicated access mode (Unity Catalog), 18 LTS, auto-stop 30 min. No serverless, no SQL warehouse (user's instruction) |
| Catalog | the user's dev catalog (blurred in screenshots) |
| Tester's role | a data engineer who knows the business need but not the kit; answers questions briefly, approves, checks Validate notes |
| Safety rule while acting as user | guide page 0, section 7: Allow reads; Allow dev writes only after `approved`; Skip anything non-dev, DROP / DELETE / GRANT, or not understood |

## Log

Each entry: what the tester intended, what was typed or clicked, what the agent did, and the verdict.

### Step 1. Ask with minimal detail (08:55)

- **Intention:** behave like a busy engineer: say only that a new daily file exists and that it should join the
  existing pipeline. Give no path, format, columns or keys. Name the compute (the user's instruction for this test).
- **Typed** (new chat, from the project's `orchestrator` notebook attached to `cluster_uc_dev`):
  `We now also get a daily payments file from our payment provider. Please add it to our existing orders pipeline. Use only the cluster cluster_uc_dev.`
- **Agent:** one line, "Let me check what I already know about this project before starting.", then the turn ended.
  No skill loaded, nothing done.
- **Verdict:** FINDING (platform behaviour): the first turn stopped early. A user has to nudge it.

### Step 2. Nudge (08:57)

- **Intention:** the shortest natural reply a user would give.
- **Typed:** `go ahead`
- **Agent:** Genie Code showed "This conversation was blocked by the model's content safety filter because it contains
  instructions believed to be trying to extract reasoning content. We are processing the conversation with a
  different model." and continued on another model. It then read its memories, the notebook, the `pogo-test` folder,
  `AGENTS.md`, `spec.md`, `config_loader.py`, `seed_orders`, the instruction files, and asked to list the landing
  volume (SDK `files.list_directory_contents`, read-only).
- **Tester action:** opened the step, read the code (two directory listings), **Allow** (page 0 rule: reading).
- **Agent:** "The AGENTS.md rules require a spec before writing any SQL or pipeline code, even config-row changes.
  Since the framework was explicitly designed so 'a new source = only new config rows', this is a natural small
  track." Then **Read de-sdd-spec skill**.
- **Verdict:**
  - PASS: understood the existing setup before proposing (metadata-driven framework: new source = config rows, no
    new code), and applied the spec-first rule from `AGENTS.md` before writing anything.
  - FINDING: `de-sdd-spec` loaded only after about 20 exploration steps, not on the request itself
    ("add a new file to our pipeline" did not match the description's trigger words).
  - FINDING (test hygiene): it reused a payments schema "from our earlier conversation" (Genie Code memory from the
    earlier skill tests), so the minimal-detail condition is weaker than intended.
  - NOTE: the safety-filter notice is a Genie Code platform event, not caused by the kit.

### Step 3. Clarifying questions (09:00)

- **Agent:** small track, no goldfish review needed; five questions, each with a recommended answer:
  1. file format and landing path: NDJSON in the existing landing volume under `payments/`, like orders (recommended), or CSV;
  2. several payments per order: yes (recommended);
  3. refunds: negative `amount` kept (recommended), or a separate refund flag;
  4. gold: defer `fact_payment` until the model spec is approved; only bronze and silver now (recommended);
  5. SCD1 sequence column: `paid_at` (recommended), or file metadata like orders.
  "Reply defaults to accept all recommendations."
- **Verdict:** PASS: one round, five questions, all with defaults, scoped to what the framework needs; it proposed
  deferring gold instead of guessing a model.

### Step 4. Accept the defaults (09:01)

- **Intention:** a user who trusts the recommendations replies with one word.
- **Typed:** `defaults`
- **Agent:** read the config row format from the existing `seed_orders` notebook, then wrote
  `specs/payments_small_20261112/spec.md` (164 lines), `decisions.md` (17 lines) and a track section in
  `specs/project-profile.md` (13 lines). Plan panel: 9 steps. Summary in chat:
  - **What:** daily NDJSON payment files into the existing `sales_orders` pipeline: bronze `payments_raw`, silver
    `payments` and `payments_quarantine`; gold `fact_payment` deferred to the model spec.
  - **How:** config rows only in `seed_orders` (datasets 106 and 107, DQ rules 1020 to 1027); no new code files.
  - **DQ:** 5 row-level Blocker rules to quarantine, 1 post-load Blocker (key uniqueness), 2 Major warnings (orphan
    order, missing daily file).
  - **Test data:** 2 synthetic files, 6 records (1 dirty row, 1 refund, 1 orphan order).
  - **Acceptance:** 9 criteria AC-P1 to AC-P9, including "existing orders untouched".
  - It ended with: "Reply approved to approve and I'll implement immediately on cluster_uc_dev, or tell me what to change."
- **Verdict:** PASS: the spec reuses the existing framework instead of new code, writes a regression check for
  orders, and waits for `approved`. Only spec files and the project profile were written (allowed before approval).
  NOTE: the files were "pending" until the user clicks **Accept all** (guide page 0).

### Step 5. Approve (09:04)

- **Intention:** read the summary, save the pending files, approve with the exact word.
- **Clicked:** **Accept all** (3 files). **Typed:** `approved`
- **Agent:** "Spec approved. Let me update the spec status, then start implementing." It changed the spec header and the
  profile row (+2 -1, +1 -1), then asked to create `landing/payments/` in the dev volume and upload the 2 sample files.
- **Tester action:** opened the code: synthetic records only, dev volume, new folder. **Allow** (page 0: a dev write
  after approval).
- **Genie Code platform:** blocked the run: "Code execution blocked for safety reasons ... upload with
  overwrite=True ... considered destructive", with Cancel / Run.
- **Tester action:** **Cancel** (a careful user does not force a run the platform calls destructive).
- **Agent:** retried by itself with `overwrite=False`. Tester read it and clicked **Allow**. Upload succeeded.
- **Verdict:**
  - PASS: the approval gate held (nothing built before `approved`); the agent recovered from the block by itself with
    a safer version.
  - FINDING (kit): the first upload used `overwrite=True` for sample data. Kit rule to add: test fixtures are written
    without overwrite, or into a new dated folder, so the platform does not block them.

### Step 6. Build: config rows (09:07 to 09:12)

- **Agent:** edited the existing `seed_orders` notebook (+87 lines, 3 new cells), then asked to run those 3 cells on
  `cluster_uc_dev` as 3 separate approvals:
  1. `MERGE INTO config_sales.dataset_detail` for dataset 106 (bronze `payments_raw`, `files_append` from
     `landing/payments`, JSON, `schemaEvolutionMode=rescue`): "dataset_detail 106 inserted";
  2. `MERGE` dataset 107 (silver `payments`) and row rules 1020 to 1024: inserted;
  3. `MERGE` post-load rules 1025 to 1027: inserted. "Config totals for pipeline 1: 7 active datasets, 45 active DQ rules".
  Then a read to verify the payment rows: "2 datasets (106, 107) and 8 DQ rules (1020-1027)".
- **Tester action:** for each step, expanded the full code and checked it with a text scan for DROP, DELETE,
  TRUNCATE, GRANT, REVOKE, overwrite (none found), catalog `dev_...`, schema `config_sales`. **Allow** each.
- **Verdict:**
  - PASS: idempotent `MERGE` (safe to re-run), dev only, follows the framework's existing seed pattern, no new code.
  - FINDING (kit): `de-sdd-implement` was never loaded and no `tasks.md` was written or claimed; the agent built
    straight from the spec chat, ticking its own 9-step plan panel. For a `small` track the kit expects a short
    `tasks.md`, a claim, and a Validate note per task that the user answers with `ok`. Here there was no Validate
    block for the user.
  - NOTE: 3 separate approvals for 3 cells; acceptable, but one batched cell would be friendlier.

### Step 7. Run the pipeline in dev (09:13)

- **Agent:** "Run orchestrator for sales_orders pipeline" with `dbutils.notebook.run` on the existing orchestrator,
  parameters `catalog=dev_...`, `config_schema=config_sales`, `test_mode=false`, `src_root` = the project's `src`.
- **Tester action:** read the parameters (dev catalog, existing notebook). **Allow** (approved plan, dev only).
- **Agent:** the run took about 6 minutes on the single-node cluster and returned SUCCESS ("Pipeline ran successfully").
- **Verdict:** PASS: the existing generic runners picked up the new datasets from config with no code change.

### Step 8. Acceptance checks (09:20)

- **Agent:** one read-only cell for AC-P1 to AC-P8 (tester scanned it: no INSERT / UPDATE / MERGE / DROP / DELETE /
  CREATE / write), a file search for AC-P9, then a "quick look" that displayed the silver payments rows.
- **Result table from the agent:**

  | AC | Result |
  |---|---|
  | AC-P1 | bronze `payments_raw` = 6 records |
  | AC-P2 | silver `payments` = 5 unique payments |
  | AC-P3 | quarantine = 1 (null `payment_id`, bad amount / currency / date) |
  | AC-P4 | refund P-2005 = -50.00 kept |
  | AC-P5 | orphan order O-9999 logged as WARN |
  | AC-P6 | key uniqueness PASS |
  | AC-P7 | 8 DQ result rows (5 row-level + 3 post-load) |
  | AC-P8 | existing orders and gold unchanged |
  | AC-P9 | only `seed_orders` changed under `src/`: no new code |

- **Tester action:** **Allow** on the reads; **Accept all** on the 4 changed files (`spec.md`, `decisions.md`,
  `project-profile.md`, `seed_orders`).
- **Verdict:**
  - PASS: every acceptance criterion from the approved spec was checked, including the regression check on orders.
  - FINDING (kit guardrail): the "quick look" printed row values of `silver_sales.payments` (synthetic data here, so
    harmless). The kit's guardrail is counts and settings only; a real source would expose amounts and ids in chat.

### Step 9. User asks to check it themselves (09:24)

- **Intention:** the guide (page 0, Rule 2) tells users to check each step themselves; the agent had not offered a
  Validate note, so the user asks for one.
- **Typed:** `How do I check this myself? Give me one query to run, on cluster_uc_dev.`
- **Agent:** built and ran one `%sql` query: 7 rows of check / value / expected (bronze 6, silver 5, distinct ids 5,
  quarantine 1, refund -50, orders unchanged 5, DQ rows 8), with "every row's value should equal expected", and
  offered "Replace active cell content" and "Copy code".
- **Tester action:** read the query (counts only, dev catalog), **Allow**. Did **not** use "Replace active cell
  content" (it would overwrite a cell of the existing `orchestrator` notebook).
- **Verdict:** PASS when asked; FINDING: the Validate note should come without asking (kit rule: one per task, user
  answers `ok`), and the "Replace active cell content" button next to it is a trap on a production notebook: the
  Validate note should say "paste into a new cell of a scratch notebook".

### Not done in this test (left to the user)

- **Commit & Push** of `pogo-test` (the agent offered it; the guide says the person does it in the Git dialog).
- Gold `fact_payment`: deferred by the approved spec.
- Ledgers: no `.internal_<email>/payments_small_20261112/progress.md` evidence and no worklog row were seen in the
  changed-files list (only spec, decisions, profile, seed). See findings.

## Summary

| Requirement of the test | Result |
|---|---|
| Minimal detail from the user | PASS: 4 short user messages (`request`, `go ahead`, `defaults`, `approved`) plus one check question |
| Understood the existing setup first | PASS: read project, spec, framework code, seed config and the landing volume before proposing; chose config-only integration |
| Asked only what it needed | PASS: one round of 5 questions, each with a recommended default |
| Spec before build, waited for `approved` | PASS: nothing built until `approved`; spec status updated on approval |
| Built in dev on the named all-purpose cluster only | PASS: every run on `cluster_uc_dev`; no serverless, no warehouse |
| Integrated and verified | PASS: pipeline SUCCESS; 9 of 9 acceptance criteria; orders unchanged |
| Kit process (tasks, Validate per task, ledgers) | PARTIAL: see findings 2, 4, 6 |

Elapsed: about 30 minutes from request to verified result (including about 6 minutes of pipeline run and the
tester's review of every approval).

## Findings and proposed kit changes

| # | Finding | Severity | Proposed change |
|---|---|---|---|
| 1 | `de-sdd-spec` loaded only after ~20 exploration steps; "add X to our existing pipeline" is not in its triggers | Minor | add "add a new source / file / table to an existing pipeline", "integrate", "onboard a source" to the `de-sdd-spec` description |
| 2 | after `approved` the agent built from the spec chat: no `tasks.md`, no claim, no `de-sdd-implement` | Major | `de-sdd-spec`: after approval of a `small` track, always write a short `tasks.md` and hand over to `de-sdd-implement` in the same chat |
| 3 | sample files uploaded with `overwrite=True`; the platform blocked it as destructive | Minor | `de-sdd-implement` / `de-quality-testing`: test fixtures are written with `overwrite=False` into a new dated folder |
| 4 | no Validate note per task; the user had to ask | Major | `de-sdd-implement`: Validate block is mandatory before any tick, even in a single-turn small track |
| 5 | a "quick look" printed row values | Major (guardrail) | `de-sdd-implement` final check: counts / expected only; never `display(SELECT *)` of a data table |
| 6 | no evidence row or worklog row seen | Minor | `de-sdd-tracking` hook at the end of a small track: progress evidence plus worklog row with `current_timestamp()` |
| 7 | the Validate query was offered with "Replace active cell content" while an existing notebook was open | Minor | Validate note text: "run in a new cell of a scratch notebook (not in pipeline notebooks)" |
| 8 | platform events (first turn ended early; safety filter switched models) | Note | none in the kit; guide page 7 can mention "if it stops after one line, reply `go ahead`" |
| 9 | Genie Code memory from earlier chats supplied the payment schema | Test note | rerun with memories cleared for a strict minimal-detail test |
