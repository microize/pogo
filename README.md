# genie-de-skills

Spec-driven data engineering skills for **Databricks Genie Code**, used **inside the Databricks workspace only**.

## Objective

Help data engineers, data architects and data modelers on Databricks, working only inside the workspace with Genie
Code, deliver two things:

1. **Reliable pipelines, built spec-first.** Nothing is built before an approved spec, every task is verified, a
   fresh-eyes (goldfish) review checks the spec, guardrails keep the agent in dev, and a release gate decides on prod.
2. **Data that people and AI can understand and use.** A semantic layer (metric views, keys, comments, Genie Agents)
   and ontology / knowledge-graph design, built on the data in Unity Catalog.

Advisory skills (technology choice, cost, environment readiness, contracts, data quality, diagnosis) support both.
The aim is to cut day-to-day effort by **up to 80%**. That figure is a target, not a claim: every task and every
piece of advisory work records its start and finish time from the workspace clock and a manual-effort estimate, and
`@de-sdd-tracking productivity report` shows the saving actually reached, with rework next to it (see
[Measuring productivity](#measuring-productivity)).

## Who it is for

| Role | Main skills | Typical output |
|---|---|---|
| Data engineer | `de-sdd-spec`, `de-sdd-implement`, `de-run-diagnose` (incl. Explain mode), `de-spark-runtime`, `de-quality-testing` | pipelines, jobs, bundles, tests, plain-language log and plan explanations, version-aware code fixes |
| Analytics engineer / BI developer | `de-data-modeling` (semantic mode), `de-sdd-spec` | gold tables, metric views, Genie Agent setup |
| Data architect | `de-advisor`, `de-cost`, `de-spark-runtime`, `de-env-check`, `de-data-contract`, `de-goldfish-review` | decision records, contracts, reviews |
| Data modeler | `de-data-modeling`, `de-ontology-design` | bus matrix, star schema / Data Vault, ontology |
| Data steward / governance lead | `de-data-governance`, `de-data-modeling` (comments, keys), `de-ontology-design` (glossary terms) | governance scorecard, tag taxonomy, classification and ABAC proposals, certification |
| Tech lead | `de-sdd-tracking`, `de-release-gate`, `de-goldfish-review` | status, who did what, productivity report, GO / NO_GO |
| Workspace admin | `de-env-check`, `install/install_skills` | readiness checklist, installed kit |
| Business / product owner | answers interview questions, approves specs, owns meaning | approved spec, confirmed definitions |

Entry points per role, and the roles not covered yet, are in [docs/user-guide/08-roles.md](docs/user-guide/08-roles.md).
Which skill covers which lifecycle stage for each role: [docs/user-guide/09-skills-by-role-and-lifecycle.md](docs/user-guide/09-skills-by-role-and-lifecycle.md).

## How it works

Every step (install, specs, build, test, commit, deploy) is done in the workspace: Genie Code, notebooks,
the SQL editor, the Lakeflow Pipelines Editor, Git folders and the bundle Deployments panel. No laptop, local CLI or
CI is needed. Each skill follows the open [Agent Skills](https://agentskills.io) standard: a folder with a `SKILL.md`
whose frontmatter has `name` and `description`.

## What is in this repo

| Path | What it is |
|---|---|
| `skills/de-*/` | the 16 skills |
| `install/install_skills.py` | notebook that publishes the skills to the workspace and verifies them |
| `install/official/` | 16 official `databricks-*` skills, vendored unmodified at the pinned release, with their license |
| `AGENTS.md` | the method's rules and routing, copied into each project folder |
| `instructions/` | conventions, security guardrails, waivers, and paste-ready Genie Code instructions |
| `docs/user-guide/` | the guide for engineers |
| `docs/maintainers/` | for kit maintainers: when each skill should load and its trigger tests, and the checklist for adding a skill |
| `backup/` | local zips of earlier versions (git-ignored, not published) |

Scope: ETL / ELT, data warehouse, lakehouse (medallion), CDC and SCD pipelines on Databricks.
Greenfield or brownfield.

**New here? Read the [user guide](docs/user-guide/README.md)** (what it is, setup, first task, what to type, files,
cost and environments, troubleshooting). This README is the maintainer reference.

## The method (one picture)

```
user requirement
   |
   v
de-sdd-spec --> clarifying questions (<=5 per round, each with a recommended default)
   |            loop until the user says "enough" / "good"
   v
specs/<track_id>/spec.md   (Status: DRAFT)         <-- written by the "elephant" (session with full context)
   |
   v  NEW chat: @de-goldfish-review spec.md        <-- "goldfish": zero-context reviewer, writes review_<n>_<email>.md
   |  back in drafting chat: "resolve review 1"     <-- PROPOSE FIX or CONTEST each finding
   v  user replies "approved"   <-- hard gate: no code before this
specs/<track_id>/plan.md + tasks.md
   |
   v
de-sdd-implement --> one task at a time --> verify --> tick task
   |                                    |
   |                                    +-- stuck >=2 attempts --> .challenges_<email>/<track_id>.md
   v
.internal_<email>/<track_id>/progress.md   (what is done, what is next)
```

Any time:
- `@de-advisor` for advisor mode (read-only recommendations with trade-offs and maturity).
- `@de-sdd-tracking` for "where are we / what is left / what did we struggle with".
- `@de-databricks-current` for current product names and DE patterns (AUTO CDC, SCD, medallion, Zerobus).

## Skills (no overlap by design)

| Skill | Owns | Never does |
|---|---|---|
| `de-sdd-spec` | intake, discovery (greenfield / brownfield), clarifying interview, `spec.md`, approval gate, `plan.md`, `tasks.md` | write pipeline code |
| `de-goldfish-review` | zero-context review of a spec in a fresh chat: comprehension paraphrase, hidden assumptions, Blocker / Major / Minor findings into `specs/<track_id>/review_<n>_<email>.md` | edit the spec, read chat history or ledgers |
| `de-sdd-implement` | claiming and executing `tasks.md` one task at a time, verification per task, commits | change the spec silently, take another person's task |
| `de-sdd-tracking` | file formats and updates for `.internal_<email>/` and `.challenges_<email>/`, status, resume, "who did what" and challenges reports across all people, start / finish times, `worklog.md`, productivity report | implement tasks, rank people |
| `de-advisor` | advisor mode: options, trade-offs, maturity (GA / Preview), recommendation | edit project files (writes only a decision record and its own ledger rows) |
| `de-cost` | cost and run-time per option from a dated Azure price file (refresh script: Retail Prices API + calculator feed) | quote negotiated prices |
| `de-env-check` | workspace readiness: compute per workload, quota signals, Unity Catalog, system tables, tooling; admin checklist | change settings, grants or clusters |
| `de-data-modeling` | bus matrix, grain, dimensions, logical and physical model, Mermaid diagram, validation queries, review | write pipeline code |
| `de-ontology-design` | concepts, properties, relationships, vocabularies and identity proposed from Unity Catalog data, with evidence; competency-question coverage; optional OWL / LinkML text | build the knowledge graph or change data |
| `de-data-governance` | read-only Unity Catalog governance assessment: 22 checks mapped to the CDMC 14 key controls, completeness score and maturity, classification-to-protection reconciliation, governed-tag taxonomy, ABAC and certification proposals, steward model, score history | run GRANT / SET TAGS / COMMENT / CREATE POLICY (writes a human-run apply script) |
| `de-databricks-current` | current Databricks names (old to new), DE design patterns, pointers to the official `databricks-*` skills | replace the official product skills |
| `de-data-contract` | versioned data contracts (`specs/contracts/*.yaml`) and change impact reports from Unity Catalog lineage | alter tables |
| `de-quality-testing` | DQ rule table with severity, enforced as pipeline expectations plus post-load SQL; unit and pipeline tests under `tests/` | design tables, run pipelines |
| `de-run-diagnose` | run, monitor, verify, classify failures (Spark catalog plus PIPE patterns), fix, re-run at most 3 times, escalate; performance review; Explain mode (logs, stack traces, cluster events, Spark UI, query profile, plans in plain language) | touch prod |
| `de-spark-runtime` | compute choice and right-sizing from system tables (node utilization, query history, job runs, billing), warehouse sizing, runtime selection and upgrade impact, version-aware code advice from a dated Spark / DBR catalog | create, resize, start or stop compute; decide serverless vs classic (official `databricks-serverless` does) |
| `de-release-gate` | PR merge disposition and prod readiness scorecard (GO / CONDITIONAL_GO / NO_GO) | deploy |

The official Databricks skills (`databricks-pipelines`, `databricks-dabs`, `databricks-jobs`,
`databricks-zerobus-ingest`, `databricks-lakeflow-connect`, ...) from
https://github.com/databricks/databricks-agent-skills hold the product syntax and mechanics, and the agent uses them freely. These skills sit on top of them, govern the
process (spec, approval, tasks, gates) and route to them. Install both.

### Overlap check against the official skills (pinned)

Official skills pinned at `databricks/databricks-agent-skills` commit `1e883ceb1835e28e26373f44d25cb13ad43b74c8` (release 0.2.45,
2026-11-10). Every official reference file cited by these skills exists at that commit.

### What the check found (36 official skills)

No official skill covers the method layer: clarifying interview, spec with approval gate, goldfish review, task
ownership and per-person ledgers, data contracts and impact reports, DQ rule design with severity, failure taxonomy
and bounded fix loop, PR and prod gates, cross-service advisor. Where an official skill holds the syntax, these skills
point to the exact reference file instead of repeating it: `databricks-pipelines` (decision tree, legacy DLT map,
AUTO CDC, expectations, SCD2 querying, performance, running a pipeline), `databricks-dabs`, `databricks-jobs`,
`databricks-unity-catalog` (grants, lineage system tables), `databricks-serverless`, `databricks-lakeflow-connect`
(connector troubleshooting), `databricks-synthetic-data-gen`.

### Core method vs supporting skills

The package has **16 skills**. Six are the method: `de-sdd-spec`, `de-goldfish-review`, `de-sdd-implement`,
`de-sdd-tracking`, `de-advisor`, `de-databricks-current`. Ten support it at the right task: `de-data-contract`,
`de-quality-testing`, `de-run-diagnose`, `de-spark-runtime`, `de-release-gate`, `de-data-modeling`, `de-ontology-design`,
`de-data-governance`, `de-env-check`, `de-cost`. Install all 16; the install notebook installs them together with the official skills and expects `32 ok, 0 failed`.

## Install (in the workspace)

Genie Code discovers skills in `/Users/<your-email>/.assistant/skills/` (personal) and
`/Workspace/.assistant/skills/` (everyone; workspace admin only). Each skill is a sub-folder with a `SKILL.md`.

1. Create a **Git folder** of this repo: Workspace > Create > Git folder, paste the repo URL.
2. Open the notebook `install/install_skills` in it and attach serverless compute.
3. Set the widget `scope`: `personal` (just you) or `workspace` (admin; also writes
   `/Workspace/.assistant_workspace_instructions.md` from `instructions/genie-code-user-instructions.md`). Both scopes
   write a `_VERSION` stamp next to the skills. `include_official` = `yes` (default) also installs the official skills. Optional
   `dry_run` = `yes` shows what would change. Run all.
4. The last cell prints `32 ok, 0 failed`. Start a **new** Genie Code chat (hard-refresh the browser if
   the skills do not appear). Skills load by description, or mention them with `@de-sdd-spec`.

To update: pull in the Git folder dialog, re-run the notebook.

### Official skills

`install/official/` holds 16 official `databricks-*` skills copied **unmodified** from
https://github.com/databricks/databricks-agent-skills at the pinned commit above, with that repo's `LICENSE`
(Databricks License: use within or connecting to Databricks) and `NOTICE`; `install/official/SOURCE.md` says how to
move the pin. `install/install_skills` installs them with the `de-*` skills, so the workspace needs no internet access
to GitHub: `databricks-core`, `-pipelines`, `-dabs`, `-jobs`, `-unity-catalog`, `-serverless`, `-docs`,
`-lakeflow-connect`, `-lakeflow-connect-saas`, `-zerobus-ingest`, `-synthetic-data-gen`, `-dbsql`, `-metric-views`,
`-spark-structured-streaming`, `-python-sdk`, `-iceberg`.

**Project folders.** Copy `AGENTS.md` and `instructions/` into the root of each project's Git folder where the method
should apply. Genie Code walks up the folder tree from the open file and injects any `AGENTS.md` it finds.
Instruction files are capped at 20,000 characters; the install notebook warns when one is over.

**How work runs.** On serverless the `databricks` CLI is not installed, and the method does not need it. Genie Code
runs SQL, the Python SDK (`WorkspaceClient`), the Pipelines Editor and notebook-cell `pytest` itself
(`in-workspace:` checks). You do the UI-only steps (`user-run:`): pull, diff and **Commit & Push** in the Git folder
dialog, and bundle deploys from the Git folder's **Deployments panel** (Public Preview; it deploys only to targets in
the same workspace, so prod is deployed from the prod workspace's Git folder, by a human, after a release-gate GO).
The panel needs serverless; without it the agent creates dev jobs through the Jobs API with your approval.

## Where the method comes from

- **Elephant-Goldfish Model (EGM)**, Google, Apache-2.0: https://github.com/google/elephant-goldfish-model.
  "Design with an elephant. Review with a goldfish." The agent with all the context drafts; reviewers with
  none read only the document; the human approves. Genie Code has no sub-agents, so the goldfish here is a
  **new chat**.
- **Conductor** (Google, Gemini CLI extension) for the interview, track ids and `[ ]` / `[~]` / `[x]` tracking.
- **GitHub Spec Kit** for the bounded clarify step (at most 5 questions a round) and runnable acceptance criteria.

## Are agents allowed in Databricks?

Three different things carry the word "agent":
- **Custom coding sub-agents inside Genie Code**: not supported. Genie Code's customization points are skills,
  `AGENTS.md` / `CLAUDE.md` instruction files, memory, and MCP servers. That is why every role here is a skill.
- **Agent skills**: yes, this package and the official `databricks-*` skills, same Agent Skills standard.
- **Genie Agents, Agent Bricks, MLflow agents**: data and AI agents for end users, built on the platform. Unrelated to
  coding; the official `databricks-genie-agents` skill covers them.

## Instructions and guardrails

- `instructions/` holds the conventions the skills assume (data engineering, Python / PySpark, security guardrails)
  and a paste-ready text for Genie Code's user or workspace instructions file. `AGENTS.md` routes to them; Genie Code
  has no per-file-type scoping, so the routing table says which file to read before which kind of work.
- Genie Code has no hooks: the guardrails in `instructions/security-guardrails.md` are enforced by instruction plus
  Genie Code's tool-approval classifier (switch to per-action approval in its settings for stricter control), and
  by Unity Catalog permissions.
- `instructions/waivers.md` records approved deviations with expiry dates.

## Multi-user tracking (who did what)

Every person runs their own Genie Code session. Each session resolves **its own** email with
`SELECT current_user()` and writes only to `.internal_<that-email>/` and `.challenges_<that-email>/`.
Shared files are `specs/<track_id>/spec.md`, `plan.md`, `tasks.md` and `review_<n>_<email>.md`. Ownership is
recorded on the task line in `tasks.md` (`owner: <email>`) and synced per topology: **Git folder** (Commit & Push in
the Git folder dialog after a claim, pull before), **plain workspace folder** (save, re-open, confirm), or **org mode** with a Unity Catalog
events table `<catalog>.sdd.task_events` (one INSERT per claim, tick, block; concurrent and timestamped).
"Who did what" is answered from `tasks.md`, each person's `progress.md`, the events table, and cross-checked
against the Git folder history; it is self-reported text otherwise. Ask `@de-sdd-tracking who did what`.

Purpose and consent: ledgers make agent work auditable and turn struggles into lessons; they are redacted, per
person, retained per `project-profile.md` (default 12 months), and anyone may ask the lead to git-ignore their
challenges file and share only lessons. State this in each project README.

## Tracking folders

| Folder | Purpose | Written by |
|---|---|---|
| `specs/<track_id>/` | `spec.md`, `plan.md`, `tasks.md` (shared, commit it) | de-sdd-spec |
| `specs/<track_id>/review_<n>_<email>.md` | goldfish review findings (shared, commit it) | de-goldfish-review |
| `.internal_<email>/index.md` | this person's track list and statuses | de-sdd-tracking |
| `specs/<track_id>/decisions.md` | clarifying questions and the user's answers, appended per round | de-sdd-spec |
| `specs/contracts/<table>.yaml`, `specs/<track_id>/impact_<n>.md` | data contracts and change impact reports | de-data-contract |
| `specs/compute/<name>-sizing.md`, `<scope>-version-review.md` | compute sizing and version-aware code reviews | de-spark-runtime |
| `specs/governance/taxonomy.md`, `history.md`, `<scope>/assessment.md`, `<scope>/apply_<n>.sql` | governance taxonomy and operating model, score history, assessments, human-run apply scripts | de-data-governance |
| `specs/<track_id>/pr_review_<n>.md`, `release_<n>.md` | merge and prod gate reports | de-release-gate |
| `tests/` | unit, pipeline and DQ SQL tests | de-quality-testing |
| `.internal_<email>/` | per-person progress ledger: what is done, what is next, decisions taken while coding | de-sdd-implement through de-sdd-tracking |
| `.challenges_<email>/` | per-person log of where the agent struggled: attempts, errors, root cause, workaround, lesson | de-sdd-implement through de-sdd-tracking |
| `.internal_<email>/worklog.md` | per-person time log for work outside a track (advice, model, ontology, cost, diagnosis, gate): start, finish, manual estimate, outcome | every skill through de-sdd-tracking |

`<email>` is the Databricks user email (`SELECT current_user()`).
Example: `.internal_sripathi@company.com/`. Commit these folders (default) so the team has the audit trail;
add `.internal_*/` and `.challenges_*/` to `.gitignore` only if your team decides they are personal scratch.

## Measuring productivity

The productivity target (for example 80%) is set per project in `specs/project-profile.md` ("Productivity"). The
kit measures against it instead of assuming it:

| What | Where | How |
|---|---|---|
| Spec phase | spec header `Intake started`, Decision Log approval, progress **Timeline** | `current_timestamp()` in the first discovery query |
| Each task | progress **Time per task**: Started, Verified, Ticked, Agent min, Wait min, fix cycles, user-run steps | `current_timestamp()` folded into the claim-time and verification queries the task already runs (no extra query or approval) |
| Manual estimate per task | `estimate:` line in `tasks.md` | proposed by the agent with a reason, confirmed or corrected by the user with the task list |
| Work outside a track | `.internal_<email>/worklog.md`, one row per deliverable | first and last query of the work; estimate proposed in the closing message (`say "est 5h" to correct`) |
| Org mode | `<catalog>.sdd.task_events` (`start`, `verified`, `worklog` events) | `event_ts` is the source of truth |

Rules: a time is never guessed (`n/a` when no query ran, and the report says how many rows it excluded); estimates
are labelled `agent` or `user`; rework (fix cycles, amendments, reopened tasks) is reported next to the saving. Ask
`@de-sdd-tracking productivity report` for a track, `me`, or the team. The figure is a trend for improving the kit
and the instructions, not a rating of people.

## Track types and statuses

`full` (interview, spec, goldfish review, plan, tasks), `small` (one-page spec, one build and one test task, no
goldfish unless keys, grain, SCD type or schedule change), `hotfix` (paragraph spec with an acceptance query, one
fix task, PR gate). Statuses, used identically in spec header, tasks header, progress, index and events:
`DRAFT | IN_REVIEW | APPROVED | IN_PROGRESS | BLOCKED | ON_HOLD | COMPLETE | ABANDONED | SUPERSEDED`.

## Org-wide use

A workspace admin runs `install/install_skills` with `scope` = `workspace` once per workspace (and again after each
update); it installs the official skills too, so engineers then install nothing. Each workspace (dev,
prod) is published from its own Git folder of this repo.

## Track IDs

`<shortname>_<YYYYMMDD>`, for example `orders_scd2_20261110`. Used as the folder name under `specs/`
and `.internal_<email>/`, and as the file name under `.challenges_<email>/`.

## Sources this package was built from (Nov 2026)

- Genie Code docs: instructions, skills, memory, MCP: https://docs.databricks.com/aws/en/genie-code/
- Databricks agent skills repo: https://github.com/databricks/databricks-agent-skills
- Lakeflow pipelines best practices and AUTO CDC: https://docs.databricks.com/aws/en/ldp/best-practices/ and https://docs.databricks.com/aws/en/ldp/cdc
- Declarative Automation Bundles (formerly Databricks Asset Bundles): https://docs.databricks.com/aws/en/dev-tools/bundles/ ; deploying from the workspace: https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-deploy
- Git folders: https://docs.databricks.com/aws/en/repos/git-operations-with-repos
- Zerobus Ingest: https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/zerobus-ingest
- Elephant-Goldfish Model: https://github.com/google/elephant-goldfish-model and the essay by Dave Rensin: https://medium.com/@drensin/elephants-goldfish-and-the-new-golden-age-of-software-engineering-c33641a48874
- Google Conductor (spec-driven extension for Gemini CLI): https://github.com/gemini-cli-extensions/conductor
- GitHub Spec Kit: https://github.com/github/spec-kit
