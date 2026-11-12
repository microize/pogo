# Skill trigger tests: when each skill should load (for maintainers)

Genie Code picks a skill by matching the user's words to each skill's `description`. This page says **when each skill
is the right one**, and gives prompts to check that it loads when it should and stays out when it should not.

Run the tests after you change a skill description, add a skill, upgrade the official skills, or when users report that
the wrong skill answered. This file is not installed into `.assistant/skills`; it is for the people who maintain the kit.

## How to run

1. Install the kit (`install/install_skills`). Open a **new** Genie Code chat for each prompt (Effort: Auto).
2. Paste the prompt **without** `@`. The point is to test automatic routing. Stop the turn as soon as the first steps
   show.
3. **Pass:** the steps show "Read `<expected>` skill", or the answer names the expected skill. **Fail:** another skill,
   a built-in skill ("Read skill" with no name), or no skill.
4. Record each result in the log at the end, with the date and the kit `_VERSION`.
5. Keep it cheap: one short turn per prompt, stopped early. Run the "should not load" prompts only for skills whose
   description changed, and for both sides of any look-alike pair you touched.

## 1. When to use each skill

| Skill | Use it when the user wants to... | Not for (use instead) |
|---|---|---|
| `de-env-check` | know what a workspace can run: compute, quota, catalogs, system tables, permissions; or a run failed for an environment reason (no compute, quota, waiting for resources, privileges) | a code or data failure (`de-run-diagnose`); sizing compute (`de-spark-runtime`) |
| `de-advisor` | choose between services, approaches or architectures ("X or Y?", "best way to...", "review this design") | a price or monthly cost (`de-cost`); cluster size or runtime version (`de-spark-runtime`) |
| `de-cost` | know what something costs: per run, per month, serverless vs classic price, real spend; refresh the price file | which product to choose (`de-advisor`); whether a cluster is the right size (`de-spark-runtime`) |
| `de-data-modeling` | design or review a data model, star schema, grain, dimensions, Data Vault, metric views, semantic layer, Genie Agent setup | business concepts and relationships for an ontology (`de-ontology-design`); building the tables (`de-sdd-spec`) |
| `de-ontology-design` | find the concepts, properties and relationships the data supports; design or review an ontology, knowledge graph or glossary terms | building graph tables (`de-sdd-spec`); star schemas (`de-data-modeling`) |
| `de-data-governance` | audit ownership, descriptions, sensitive data, protection, certification; tag taxonomy; steward model; ABAC proposals; governance score over time | writing a GRANT or mask for a known need (official `databricks-unity-catalog`); comments for one model (`de-data-modeling`) |
| `de-data-contract` | write a data contract; know what breaks downstream if a table or column changes | data quality rules (`de-quality-testing`) |
| `de-sdd-spec` | start new work: a requirement, new pipeline or table, small change or hotfix that needs a spec | building after approval (`de-sdd-implement`); product syntax questions (`de-databricks-current`) |
| `de-goldfish-review` | review a spec with fresh eyes, in a **new** chat | a code or PR review (`de-release-gate`) |
| `de-sdd-implement` | build an approved spec: "approved", "implement", "next task", "work on T03" | a one-off query with no spec (no skill, or `de-advisor`) |
| `de-quality-testing` | design data quality rules, expectations, quarantine, unit or pipeline tests | why a check failed last night (`de-run-diagnose`) |
| `de-run-diagnose` | run a pipeline or job and confirm it worked; find why it failed, is slow or gives wrong numbers; **explain** a log, stack trace, Spark UI page, query profile or plan | choosing or sizing compute, runtime versions (`de-spark-runtime`); planning new work (`de-sdd-spec`) |
| `de-spark-runtime` | choose compute and size it; check if a cluster or warehouse is too big, too small or idle; pick a runtime version; know what an upgrade brings or breaks; fit code to the Spark version | explaining a failure or log (`de-run-diagnose`); serverless vs classic and performance mode for a new job (official `databricks-serverless`); price only (`de-cost`) |
| `de-release-gate` | review a PR or merge; decide go / no-go for production | reviewing a spec (`de-goldfish-review`); deploying (nobody: a person deploys) |
| `de-sdd-tracking` | see status, what is left, who did what, struggles, handover, time and productivity reports | doing the next task (`de-sdd-implement`) |
| `de-databricks-current` | translate old names and code (DLT, APPLY CHANGES, Asset Bundles, Workflows); current design patterns (SCD, CDC, medallion); which official reference holds the syntax | designing a model (`de-data-modeling`); choosing a service (`de-advisor`) |

## 2. Prompts per skill

Prompts use the fictional ShopCo example from the user guide (page 3); it is not a real company. Each skill has at least two "should load" prompts in
plain user words and at least one "should not load" prompt that sounds similar.

| Skill | Should load | Should not load (expected instead) |
|---|---|---|
| `de-env-check` | "Check this workspace's readiness for data engineering." / "My run says WAITING_FOR_RESOURCES and quota exceeded. Why?" / "What compute and catalogs can I use here?" | "My pipeline failed with a stack trace." (`de-run-diagnose`) / "Is my cluster too big?" (`de-spark-runtime`) |
| `de-advisor` | "Should we use Auto Loader or Lakeflow Connect for the daily ShopCo files?" / "What is the best way to load order events at 2,000 per second?" / "Review this architecture: files to bronze, silver, gold, then Genie." | "How much will this cost per month?" (`de-cost`) / "Which DBR version should this job use?" (`de-spark-runtime`) |
| `de-cost` | "How much will the daily ShopCo pipeline cost per month on classic vs serverless?" / "What did this job actually cost last month?" / "Refresh prices." | "Which service should we use for ingestion?" (`de-advisor`) / "Is the warehouse oversized?" (`de-spark-runtime`) |
| `de-data-modeling` | "Design a star schema for ShopCo orders and payments." / "Set up a revenue metric view and a Genie Agent on gold sales." / "Review our gold model: is the grain right?" | "What concepts and relationships are in our customer data?" (`de-ontology-design`) / "Build the gold tables." (`de-sdd-spec`) |
| `de-ontology-design` | "What concepts, properties and relationships can we get from the ShopCo sales tables?" / "Design an ontology for customers and products." / "Which glossary terms do our tables support?" | "Build node and edge tables in a graph database." (`de-sdd-spec`) / "Design a star schema." (`de-data-modeling`) |
| `de-data-governance` | "Run a governance audit of catalog dev_shop." / "Which sensitive columns have no mask or policy?" / "Propose a tag taxonomy and who should own the sales schemas." / "What can we certify in gold?" | "Grant SELECT on gold to analysts." (official `databricks-unity-catalog`) / "Write comments for the sales model." (`de-data-modeling`) |
| `de-data-contract` | "We want to drop the region column from fact_orders: what breaks downstream?" / "Write the data contract for gold fact_orders." | "Add a data quality rule for null customer ids." (`de-quality-testing`) |
| `de-sdd-spec` | "New requirement: load the daily ShopCo order files into silver and build a revenue table." / "Start a hotfix track: fact_orders counts cancelled orders twice." / "Small change: add a region column to silver orders." | "What does AUTO CDC do?" (`de-databricks-current`) / "Work on T03." (`de-sdd-implement`) |
| `de-goldfish-review` | "Review the spec specs/shop_orders_20261112/spec.md with fresh eyes." (in a new chat) / "Goldfish review of the ShopCo spec." | "Review this PR." (`de-release-gate`) |
| `de-sdd-implement` | "approved" (after a spec summary) / "Work on T03." / "Implement the next task." | "Write me a quick query for yesterday's orders." (no skill, or `de-advisor`) |
| `de-quality-testing` | "Write data quality rules and unit tests for silver orders." / "Which rows should go to quarantine?" | "The quality check failed last night. Why?" (`de-run-diagnose`) |
| `de-run-diagnose` | "Did my ShopCo pipeline fail?" / "The job is slow today." / "Why are the numbers wrong in gold?" / "Explain this stack trace." / "Explain this query profile." | "Plan a new pipeline." (`de-sdd-spec`) / "Which cluster size should this job use?" (`de-spark-runtime`) |
| `de-spark-runtime` | "Is cluster etl-nightly oversized?" / "Right-size warehouse sales_wh." / "We run DBR 15.4: which functions should we change, and what would 18 LTS give us?" / "Is input_file_name still supported on our runtime?" | "Explain this stack trace." (`de-run-diagnose`) / "How much will this cost per month?" (`de-cost`) |
| `de-release-gate` | "Is shop_orders_20261112 ready for production? Go or no-go." / "Review this PR for merge." | "Deploy to prod now." (should refuse and explain the gate; it never deploys) / "Review the spec." (`de-goldfish-review`) |
| `de-sdd-tracking` | "Where are we on the ShopCo track?" / "Who did what this week?" / "What did we struggle with?" / "How much time did we save this month?" / "Hand over T05 to T07 to ben@example.com." | "Is prod ready?" (`de-release-gate`) / "Work on the next task." (`de-sdd-implement`) |
| `de-databricks-current` | "Convert this DLT code to current syntax." / "What is the new name for Delta Live Tables?" / "Which official reference has the AUTO CDC syntax?" | "Design the star schema." (`de-data-modeling`) |

## 3. Look-alike pairs (test both sides when either description changes)

These are the requests most likely to go to the wrong skill.

| Pair | Tells them apart | Prompt for side A | Prompt for side B |
|---|---|---|---|
| `de-advisor` vs `de-cost` | *which* option vs *how much* it costs | "Auto Loader or Lakeflow Connect?" | "What does Lakeflow Connect cost per month?" |
| `de-advisor` vs `de-spark-runtime` | service or approach vs compute size or runtime | "Pipeline or notebook job for this?" | "How many workers should this job have?" |
| `de-cost` vs `de-spark-runtime` | price vs right size | "Monthly cost of warehouse sales_wh?" | "Is warehouse sales_wh too big?" |
| `de-run-diagnose` vs `de-spark-runtime` | explain or fix a failure vs change compute or runtime | "Why did stage 12 spill to disk?" | "Should we use memory-optimized workers?" |
| `de-run-diagnose` vs `de-env-check` | code or data failure vs environment failure | "Job failed with a schema mismatch." | "Job failed with quota exceeded." |
| `de-data-modeling` vs `de-ontology-design` | tables and metrics vs concepts and relationships | "Design the star schema for sales." | "What concepts does our sales data support?" |
| `de-data-modeling` vs `de-data-governance` | descriptions for one model vs governance across a catalog | "Write comments for the sales model." | "How many tables in dev_shop have no description?" |
| `de-data-governance` vs official `databricks-unity-catalog` | audit and propose vs write the grant or mask syntax | "Which sensitive columns are unprotected?" | "Write a column mask for email." |
| `de-data-contract` vs `de-quality-testing` | schema and consumers vs rules on values | "What breaks if we drop region?" | "Rule: amount must not be negative." |
| `de-goldfish-review` vs `de-release-gate` | spec vs code and release | "Fresh-eyes review of the spec." | "Is this ready for production?" |
| `de-sdd-spec` vs `de-sdd-implement` | before approval vs after approval | "New requirement: ..." | "approved" |
| `de-sdd-tracking` vs `de-release-gate` | progress vs readiness | "What is left on the track?" | "Go or no-go for prod?" |
| `de-spark-runtime` vs official `databricks-serverless` | size, runtime, version fit vs serverless or classic for a new job spec | "Is this cluster oversized?" | "Create a serverless job for this notebook." |

## Results log

| Date | `_VERSION` | Skill | Prompt | Loaded | Pass |
|---|---|---|---|---|---|
