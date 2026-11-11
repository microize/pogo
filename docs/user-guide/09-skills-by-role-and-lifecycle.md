# 9. Skills by role and lifecycle stage

This page answers one question: **"I am a <role>, and I am at <stage>. Which skill helps me?"**

You still do not need skill names. Type your request in plain words and Genie Code loads the skill. Example requests
for each role are on [page 8](08-roles.md). The full ShopCo story is on [page 3](03-first-task.md).

## The lifecycle

Most data work goes through these stages. Small changes skip some of them.

| # | Stage | What happens | Ends with | ShopCo example (page 3) |
|---|---|---|---|---|
| 0 | **Set up** | install the kit; check what the workspace allows | installed skills, `specs/env/<env>-<team>.md` | "Serverless is on; billing tables not granted yet" |
| 1 | **Discover and advise** | understand the need; choose technology, compute and cost | a recommendation or decision record | "Use Auto Loader in a pipeline on serverless" |
| 2 | **Design** | data model, metrics, Genie Agent, business concepts, contracts, governance rules | `model.md`, `ontology.md`, contracts, `taxonomy.md` | fact_orders, dim_customer, revenue metric view; email tagged as restricted |
| 3 | **Specify and review** | questions, spec, fresh-eyes review, approval, task list | `spec.md` APPROVED, `tasks.md` | spec for `shop_orders_20261112`, 12 tasks |
| 4 | **Build and test** | tasks one at a time; data quality rules and tests | ticked tasks with proof | bronze, silver, gold tables built and checked |
| 5 | **Run and diagnose** | run in dev, check the output, explain and fix failures | runs that passed their checks | "a normal view was read as a stream": fixed |
| 6 | **Optimize** | right-size compute, pick the runtime, fit code to the Spark version, cost | sizing and version reviews | "cluster 88% idle: move to serverless"; replace `input_file_name()` |
| 7 | **Release** | merge review and production check; a person deploys | GO / CONDITIONAL_GO / NO_GO | "GO once the masking policy is applied in prod" |
| 8 | **Operate and govern** | status, handover, governance rechecks, contract changes, productivity | status, assessments, reports | governance score up from 61 to 88; "6 h 40 min vs 32 h by hand" |

## Skills by stage

How to read it: ● = the main skill for that stage; ○ = used in that stage when needed; empty = not used.

| Skill | 0 Set up | 1 Advise | 2 Design | 3 Specify | 4 Build | 5 Run | 6 Optimize | 7 Release | 8 Operate |
|---|---|---|---|---|---|---|---|---|---|
| `de-env-check` | ● | ○ | | ○ | | ○ | ○ | ○ | ○ |
| `de-advisor` | | ● | ○ | ○ | | | ○ | | |
| `de-cost` | | ● | | ○ | | | ● | | ○ |
| `de-data-modeling` | | | ● | ○ | | | | ○ | |
| `de-ontology-design` | | | ● | | | | | | ○ |
| `de-data-contract` | | | ● | ○ | | | | ○ | ● |
| `de-data-governance` | | ○ | ● | | | | | ○ | ● |
| `de-sdd-spec` | | | | ● | | | | | ○ |
| `de-goldfish-review` | | | ○ | ● | | | | | ○ |
| `de-sdd-implement` | | | | | ● | ○ | | | |
| `de-quality-testing` | | | ○ | ○ | ● | ○ | | ○ | ○ |
| `de-run-diagnose` | | | | | ○ | ● | ○ | | ○ |
| `de-spark-runtime` | | ○ | | ○ | | ○ | ● | | ○ |
| `de-release-gate` | | | | | | | | ● | |
| `de-sdd-tracking` | | | | ○ | ○ | ○ | | ○ | ● |
| `de-databricks-current` | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| official `databricks-*` | ○ install | | ○ metric views, UC | | ● syntax | ○ | ○ serverless | | ○ |

`de-databricks-current` is the current-names and patterns reference used throughout; the official `databricks-*`
skills hold product syntax (pipelines, jobs, bundles, Unity Catalog, metric views, serverless).

## Roles by stage

What each role does at each stage, and the skill that helps. "Approves" means the role's reply (`approved`, `ok`) is
the gate; the agent never approves for anyone.

| Stage | Data engineer | Analytics engineer / BI | Data architect | Data modeler | Data steward / governance lead | Tech lead | Workspace admin | Business / product owner |
|---|---|---|---|---|---|---|---|---|
| **0 Set up** | readiness of own environment (`de-env-check`) | - | readiness review (`de-env-check`) | - | admin prerequisites for system tables (`de-data-governance`) | project profile, topology, productivity target | installs the kit, fixes the admin checklist (`de-env-check`) | - |
| **1 Advise** | technology and compute questions (`de-advisor`, `de-spark-runtime`) | serving choice (`de-advisor`) | **owns**: options, trade-offs, decision records (`de-advisor`, `de-cost`) | method choice (`de-data-modeling`) | regulations, scope (`de-data-governance`) | priorities, budget (`de-cost`) | what can be enabled (`de-env-check`) | states the need and the business questions |
| **2 Design** | reviews contracts and models | **owns** semantic layer: metric views, comments, keys, Genie Agent (`de-data-modeling`) | reviews models and contracts (`de-data-contract`, `de-goldfish-review`) | **owns**: bus matrix, grain, star schema or Data Vault, ontology (`de-data-modeling`, `de-ontology-design`) | **owns**: tag taxonomy, steward model, classification (`de-data-governance`) | approves cross-team contracts | - | **approves** definitions, metrics, competency questions |
| **3 Specify** | **owns** the spec and tasks (`de-sdd-spec`); goldfish in a new chat | spec for semantic builds (`de-sdd-spec`) | goldfish reviewer (`de-goldfish-review`) | hands the approved model to the spec | governance requirements in the spec | **approves** major amendments, checks scope | - | **approves** the spec (`approved`) |
| **4 Build** | **owns**: tasks back to back, Validate, tick (`de-sdd-implement`, `de-quality-testing`) | builds metric views and comments as tasks (`de-sdd-implement`) | - | validation queries for the model (`de-data-modeling`) | applies approved tags and comments (owner runs `apply_<n>.sql`) | handovers, claims (`de-sdd-tracking`) | - | validates results when asked (`ok`) |
| **5 Run** | **owns**: run, verify, explain, fix (`de-run-diagnose`) | explains slow dashboards and queries (`de-run-diagnose` Explain mode) | escalations | - | - | stuck tracks (`de-sdd-tracking`) | quota, permission and compute errors (`de-env-check`) | - |
| **6 Optimize** | **owns**: right-size, runtime, version-aware code (`de-spark-runtime`) | warehouse size (`de-spark-runtime`) | compute standards, policies (`de-spark-runtime`, `de-cost`) | - | - | cost per run, upgrade plan (`de-cost`, `de-spark-runtime`) | cluster policies, runtime upgrades (`de-spark-runtime`) | - |
| **7 Release** | PR and prod gate prep (`de-release-gate`) | Genie readiness rows of the gate (`de-release-gate`) | reviews NO_GO findings | - | governance rows of the gate (`de-data-governance` assessment) | **approves** GO; a human deploys prod (`de-release-gate`) | runs the prod deploy if that is their role | told before go-live |
| **8 Operate** | status, handover, failures (`de-sdd-tracking`, `de-run-diagnose`) | certification of gold, Genie benchmarks (`de-data-governance`, `de-data-modeling`) | schema change impact (`de-data-contract`) | model changes as new tracks | **owns**: rechecks, score history, certification and deprecation (`de-data-governance`) | **owns**: status, who did what, challenges, productivity report (`de-sdd-tracking`) | environment rechecks (`de-env-check`) | reviews outcomes, raises the next need |

## Coverage at a glance

| Role | Stages with a main skill | Main skills |
|---|---|---|
| Data engineer | 3, 4, 5, 6 | `de-sdd-spec`, `de-sdd-implement`, `de-quality-testing`, `de-run-diagnose`, `de-spark-runtime` |
| Analytics engineer / BI | 2, 4 | `de-data-modeling` (semantic mode), `de-sdd-implement` |
| Data architect | 1, 2 | `de-advisor`, `de-cost`, `de-data-contract`, `de-goldfish-review` |
| Data modeler | 2 | `de-data-modeling`, `de-ontology-design` |
| Data steward / governance lead | 2, 8 | `de-data-governance` |
| Tech lead | 7, 8 | `de-release-gate`, `de-sdd-tracking` |
| Workspace admin | 0 | `de-env-check`, `install/install_skills` |
| Business / product owner | approves at 2 and 3 | no skill of their own: answers questions and approves |

## Not covered yet

| Role or stage | Gap |
|---|---|
| ML engineer / data scientist | feature tables, training sets and model serving: official `databricks-*` skills only |
| On-call / incident review across jobs | `de-run-diagnose` handles one run at a time; no runbook or incident-review skill |
| Business owner self-service | no skill writes in business language for non-technical owners beyond the spec summary |
