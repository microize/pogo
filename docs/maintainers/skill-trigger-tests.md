# Skill trigger tests (for maintainers)

Genie Code picks a skill from its `description`. These prompts check that each skill loads when it should and stays
out when it should not. Run them after changing a description, after an official-skill upgrade, or when users report
the wrong skill answering. Not installed into `.assistant/skills`; this file is for the people who maintain the kit.

## How to run

1. Install the kit (`install/install_skills`), open a **new** Genie Code chat in agent mode per prompt.
2. Paste the prompt **without** `@` (the point is automatic routing). Stop the turn as soon as the first steps show.
3. Pass: the steps show "Read `<expected>` skill" (or the expected skill is named in the answer). Fail: another
   skill, a built-in skill ("Read skill" with no name) or no skill.
4. Record results in the table at the end with the date and the kit `_VERSION`. Cost: one short turn per prompt; stop
   early to keep it cheap. Run the "should not" prompts only for skills whose description changed.

## Prompts

| Skill | Should load | Should not load (expected instead) |
|---|---|---|
| de-sdd-spec | "New requirement: ingest daily order files into silver and build a revenue table." / "Start a hotfix track for the null region bug." | "What does AUTO CDC do?" (de-databricks-current) |
| de-goldfish-review | "Review the spec specs/x/spec.md with fresh eyes." (in a new chat) | "Review this PR." (de-release-gate) |
| de-sdd-implement | "approved" (after a spec) / "Work on T03." | "Write me a quick query for yesterday's orders." (none or de-advisor) |
| de-sdd-tracking | "Where are we on the orders track?" / "What did we struggle with?" | "Is prod ready?" (de-release-gate / de-env-check) |
| de-advisor | "Should we use a declarative pipeline or a notebook job for this?" | "How much will this cost per month?" (de-cost) |
| de-env-check | "Check the environment: what compute and catalogs do I have?" / "Why does my cluster say quota exceeded?" | "My pipeline failed with a stack trace." (de-run-diagnose) |
| de-cost | "How much will this job cost per month on classic vs serverless?" | "Which service should we use?" (de-advisor) |
| de-data-modeling | "Design a star schema for orders and payments." / "Set up metric views and Genie on our gold layer." | "What concepts and relationships are in our data?" (de-ontology-design) |
| de-ontology-design | "What concepts, properties and relationships can we get from our sales tables?" / "Design an ontology for customers and products." | "Build node and edge tables in Neo4j." (de-sdd-spec, build track) |
| de-data-contract | "We want to drop the region column: what breaks downstream?" | "Add a DQ rule for nulls." (de-quality-testing) |
| de-quality-testing | "Write DQ rules and unit tests for silver orders." | "The DQ step failed last night, why?" (de-run-diagnose) |
| de-run-diagnose | "Did my pipeline fail?" / "The job is slow today." / "Why are the numbers wrong in gold?" | "Plan a new pipeline." (de-sdd-spec) |
| de-release-gate | "Is this ready for prod? Go or no-go." / "Review this PR." | "Deploy to prod now." (should refuse and explain the gate, not deploy) |
| de-databricks-current | "Convert this DLT code to current syntax." / "What's the new name for Delta Live Tables?" | "Design the star schema." (de-data-modeling) |

## Results log

| Date | `_VERSION` | Skill | Prompt | Loaded | Pass |
|---|---|---|---|---|---|
