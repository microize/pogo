# Version review: <scope (job, pipeline, folder)>

By: <email> | Date: <YYYY-MM-DD> | Catalog: `de-spark-runtime/references/runtime-versions.md` checked <date>
Runtime now: <DBR x / serverless env n / warehouse channel> = Apache Spark <version> | Found from: <system.compute.clusters / job environment / user>
Target considered: <runtime or "none"> | Files scanned: <list>

## 1. Fix now (works on the current runtime)

| # | File:line | Code does | Use instead | Available since | Why (speed, correctness, simplicity) |
|---|---|---|---|---|---|

## 2. Breaks or changes on upgrade

| # | File:line | Code does | Breaks on | Do instead |
|---|---|---|---|---|

## 3. Gains from upgrading

| Feature or function | Needs | What it would replace here | Expected gain |
|---|---|---|---|

Upgrade effort: <low / medium / high> because <reasons>. Test plan: dev run on the target runtime, row counts, key
uniqueness and checksums (`de-quality-testing` invariants), run time (`de-run-diagnose`).

## 4. Not in the catalog

Functions or patterns found that the catalog does not cover (checked against release notes, or left open): <list>.

## 5. Next steps

Tasks to add (`small` track via `de-sdd-spec`, or `T<nn>` lines in the current track): <list>.
