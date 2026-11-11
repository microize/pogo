# 3. Your first task, step by step

This is a real run from our test workspace, shortened. The goal: build a bronze / silver / gold pipeline for order
JSON files. Follow the same steps with your own request.

## Step 1. Open the project and a new chat

Open any file inside the project folder (for example `start.sql`), click the Genie Code icon, then **New chat**.
Opening a file inside the project matters: that is how Genie Code finds `AGENTS.md`.

## Step 2. Say what you need

```
create a medallion architecture for the order JSON files in /Volumes/dev_cat/raw_sales/orders/
(small synthetic data). Project folder: /Users/me@company.com/orders-project
```

You will see "Read de-sdd-spec skill". The agent looks at the files first (for example it noticed amounts stored as
text, time zone offsets, bad rows) and then asks up to 5 questions, each with a recommended answer:

```
1. How should silver keep customer history?  a. SCD Type 2 (recommended)  b. SCD Type 1  c. none
2. What should gold contain?                 a. star schema (recommended) ...
```

## Step 3. Answer

Answer by number, or type `defaults` to accept every recommendation. Add anything it should know:

```
1a, 2a, 3a, 4a, 5a. Use schemas med_bronze, med_silver, med_gold. Keep it small and cheap. Enough, draft the spec.
```

## Step 4. Read the spec, then approve

The agent writes `specs/<track_id>/spec.md` and shows a summary: tables, rules, checks with expected numbers, and
what it could not test. Read the summary. Then reply one of:

- `approved` - start building (big tracks: reply `goldfish` first for a fresh-eyes review in a new chat).
- What to change, in plain words.

"looks fine" or "ok" is **not** approval; the agent will ask again. This is on purpose.

## Step 5. Let it build, and validate each task

After approval it writes `plan.md` and `tasks.md`, then works through the tasks without you typing `next`. After each
task you get a Validate block:

```
T01 done (verified): source has 2 files, 8 records, 11-10 file older than 11-11 file.
Validate: the "Track ..." section of project-profile.md. Expected: 8 records, ...
Reply ok to tick and continue, fix <what> to change it, auto, or stop.
```

- `ok` - you agree; it ticks the task and continues.
- `fix ...` - say what is wrong.
- `auto` - from now on it ticks tasks whose checks passed without waiting for you (you still see the Validate block).
- `stop` - pause.

## Step 6. Do the user-run steps

A few steps are buttons only you can press, all in the workspace:

1. **Deploy the bundle to dev.** Open `databricks.yml` in the project Git folder, click the **Deployments** icon (the
   rocket), choose the `dev` target and click **Deploy**. Copy the result (success, or the error text) back into the
   chat. The Deployments panel is in Public Preview; it deploys only to targets in this workspace.
2. **Commit and push.** Open the Git dialog of the project folder, check the diff, enter the commit message the agent
   suggested (for example `feat(orders_scd2_20261110): T03 bundle`) and click **Commit & Push**.

The agent batches these so you stop only once or twice.

## Step 7. Waiting for pipeline runs

A pipeline update on classic compute takes about 10 minutes to start. The agent says
`say check in about 10 minutes`. Come back and type `check`; it verifies everything in one pass.

## Step 8. When something fails

You do nothing at first. In our run the silver update failed with "orders_valid was read as a stream but is not a
streaming table". The agent read the error, fixed both files, logged the problem in the challenges file, re-ran, and
the checks passed. After 3 failed fix attempts it stops and asks you.

## Step 9. Finish

After the last task it runs every acceptance check and a merge-readiness review, then asks for your final `ok`. Only
then does it set the spec to COMPLETE. Production is a separate step: ask "is this ready for production?" to run the
prod gate; after GO a human deploys from the **Deployments** panel of the project's Git folder in the prod workspace.

## What you should have at the end

- Tables in dev with the expected numbers (the agent shows them; you can query them yourself).
- In `specs/<track_id>/`: spec, plan, tasks (all `[x]` with your name), review files.
- In `.internal_<you>/`: progress with the evidence for each task. In `.challenges_<you>/`: what went wrong and how it
  was fixed.
