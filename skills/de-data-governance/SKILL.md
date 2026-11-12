---
name: de-data-governance
description: Data governance assessment and proposals for Unity Catalog, for data stewards, governance leads and architects. Use when the user asks for a governance audit, scorecard or maturity check, "who owns this data", ownership or steward model, PII or sensitive data classification review, governed tag taxonomy, tag coverage, comment or documentation coverage, certification or deprecation candidates, ABAC policy proposals or "which sensitive columns are not protected", access hygiene review, CDMC or DAMA alignment, or "track governance over time". Reads information_schema and system tables (metadata and counts only), scores each asset against checks mapped to the EDM Council CDMC 14 key controls, and writes specs/governance/<scope>/assessment.md with findings, proposals and a human-run apply script. Advisory only: never runs GRANT, REVOKE, SET TAGS, COMMENT, CREATE POLICY or ownership changes itself.
metadata:
  version: "0.1.1"
---

# de-data-governance: how well governed is this data, and what to fix first

You assess how well the data in Unity Catalog is owned, described, classified, protected, certified and traced, and
you propose fixes ranked by risk and usage. You do **not** change anything: every tag, comment, owner, policy or grant
you propose goes into a reviewed script that a human with the right privilege runs. Proposals are made, approved,
then applied by a person (the same gate as a spec).

Checks, SQL and scoring: `references/governance-checks.md`. Tag taxonomy and classification scheme:
`references/taxonomy-and-classification.md`. Roles, maturity levels and the frameworks behind them:
`references/frameworks.md`. Feature status (GA / Preview / Beta, dated): `references/uc-governance-features.md`.
Output shapes: `templates/assessment.md`, `templates/taxonomy.md`, `templates/history.md`.

## Ground rules

- **Read-only, metadata first.** `system.information_schema` views, `system.access.*` lineage and audit, and the
  classification and data quality results tables. Profiles are counts only. Never select row values; never select the
  sample-value columns of `system.data_classification.results` (they hold real values); run `DESCRIBE TABLE` first
  on any table whose columns are marked unverified, then select named columns, never `SELECT *`.
- **You see what you can see.** `information_schema` shows only objects the current user can access, and
  `abac_policy_definitions` lists only securables where the user has `MANAGE`. Every score states its visibility
  ("of 412 tables visible to <email>") and the report says which checks were skipped for missing access.
- **Batch.** One query per check family per catalog, on the SQL warehouse named in `specs/project-profile.md`
  (classification results need serverless). Fold `current_timestamp() AS ts` into the first and last query for the
  worklog (`de-sdd-tracking`, "Time and effort").
- **Evidence on every finding**: the check id, the CDMC control, the numbers, the query that produced them, and a
  confidence (`measured` from metadata, `inferred` from names or usage, `assumed` needs an owner).
- **Never apply.** `GRANT`, `REVOKE`, ownership transfer, `SET TAGS`, `COMMENT ON`, `CREATE POLICY`, classification
  settings and access-request destinations are written into `apply_<n>.sql` (or a UI step list) for a human, per
  `instructions/security-guardrails.md`. Grants and policies outside dev are proposals for an admin, always.
- **The business owns meaning and risk appetite.** You propose sensitivity levels, owners, stewards and
  certification; a named owner or the governance lead confirms them.
- **Current names and status.** Governed tags, Data Classification, ABAC policies, Discover and domains, Pages,
  certification system tag, Request for access, Data Quality Monitoring, Data Profiling. Status and date per feature
  are in `references/uc-governance-features.md`; say the status whenever you recommend one, prefer GA, and recheck
  release notes if the file is older than 60 days.
- Struggles (missing access to system tables, unverified columns, failed queries) go through `de-sdd-tracking` into
  `.challenges_<your-email>/governance-<scope>.md`, redacted.

## Modes

State the mode in your first line.

| Mode | When | Output |
|---|---|---|
| **Assess** (default) | "governance audit", "scorecard", "how governed is catalog X" | `specs/governance/<scope>/assessment.md` + a row in `specs/governance/history.md` |
| **Taxonomy** | "tag taxonomy", "classification scheme", "which governed tags should we have" | `specs/governance/taxonomy.md` |
| **Operating model** | "who owns this data", "steward model", "RACI", "governance roles" | section 2 of `specs/governance/taxonomy.md` |
| **Protect** | "which sensitive columns are not protected", "propose ABAC policies" | assessment section 5 + policy proposals |
| **Certify** | "what can we certify", "what should be deprecated" | assessment section 6 |
| **Recheck** | "recheck governance", after fixes are applied | new assessment version, delta against the last one |

## Steps (Assess; other modes run the matching subset)

1. **Discover.** Project root = folder holding `AGENTS.md`. Read `specs/project-profile.md` (catalogs, warehouse,
   the Environment section from `de-env-check`), existing `specs/governance/`, `specs/contracts/`, `specs/models/`,
   `specs/ontology/`. Then ask once, up to 5 questions, recommended answer first: scope (catalogs and schemas; default
   the project's prod-facing silver and gold), regulations that apply (GDPR, HIPAA, PCI DSS, GLBA, DPDPA, none),
   whether a tag taxonomy already exists (governed tags in the account, or a document), who the governance lead is,
   and the target maturity (default: level 3 "Defined" for all, level 4 for sensitive data).
2. **Access check.** One query per source to see what is readable: `system.information_schema.tables`,
   `system.access.table_lineage`, `system.access.audit`, `system.data_classification.results`,
   `system.data_quality_monitoring.table_results`, `system.information_schema.abac_policy_definitions`. Unreadable
   sources become a `user-run` prerequisite for an admin (exact grant text, written, not run) and their checks are
   marked `skipped`, never guessed.
3. **Inventory.** Tables, views, columns, owners, comments, tags at every level, masks and row filters, privileges,
   ABAC policies, classification results (class and column only), data quality monitoring state, lineage presence,
   and 30-day usage (read events per table from `system.access.table_lineage`). SQL in
   `references/governance-checks.md`.
4. **Score.** Run checks G01 to G22. Each asset gets a completeness score (weights in the checks file) and a band:
   **Strong** at 90 or more, **Good** at 75, **Weak** at 50, **Ungoverned** below. Each CDMC component gets a
   maturity level from 0 to 5 (`references/frameworks.md`). Sensitive assets are scored on their own line, because
   CDMC applies its controls to sensitive data first.
5. **Reconcile classification with protection.** Join `class.*` system tags and governed sensitivity tags with column
   masks, row filters and ABAC policies. Findings: sensitive column with no protection; policy whose tag matches no
   column (it is silently skipped); sensitivity tag set only at table level (ABAC column matching does not see it);
   a governed tag referenced by a policy (deleting it breaks queries); classification results not reviewed into
   governed tags.
6. **Prioritise.** Risk first (sensitive and unprotected, broad grants on sensitive data), then usage (most-read
   tables without owner, comments or tags), then everything else. At most 15 findings at the top of the report; the
   rest in an appendix table.
7. **Propose.** For each top finding: the object, current value, proposed value, evidence, who must approve, and the
   statement or UI step. Comment drafts are marked `draft`; AI-generated comments are drafts until the owner accepts
   them and are never evidence of classification. Owners are groups or service principals, never individuals;
   stewards are recognized from who already owns, writes and reads the data (`references/frameworks.md`), not
   assigned at random. Certification is proposed only when the asset meets the rubric in the checks file.
8. **Write and hand back.** Fill `templates/assessment.md` into `specs/governance/<scope>/assessment.md` (full
   workspace path; read it back) and the proposed statements into `specs/governance/<scope>/apply_<n>.sql`, grouped
   by approver (asset owner, governance lead, admin) with a header that says who runs it and with what privilege.
   Append one row to `specs/governance/history.md` (template `templates/history.md`; create it on first use). Ask: "Reply `approved` to accept the proposals (a human runs `apply_<n>.sql`), or tell
   me what to change." Record the verbatim reply in `specs/governance/<scope>/decisions.md` (append-only). Log the
   worklog row with a manual estimate.
9. **Hand-offs.** Comments and keys on a model: `de-data-modeling`. Glossary concepts: `de-ontology-design`.
   Contract fields (classification, owner, critical data elements, in ODCS field names): `de-data-contract`. DQ rules
   and monitors for critical data: `de-quality-testing`. Fixes that change pipelines (masking in silver, retention,
   erasure): a `small` track via `de-sdd-spec`. Prod release of new tables: `de-release-gate` reads the latest
   assessment's checks for those tables.

## Certified-before-use (for other skills)

When `de-data-modeling` sets up a Genie Agent or metric view, or `de-release-gate` reviews a prod release, they ask
this skill (or read the latest assessment) whether the source tables have an owner group, comments, sensitivity
classification and no unprotected sensitive column. A table that fails is a WARN with the check ids, not a silent pass.

## Not this skill

- Writing GRANT / mask / row filter / ABAC syntax for a known need: official `databricks-unity-catalog`
  (`references/1-access-control.md`, `4-fine-grained-access.md`); ABAC policy syntax is in this skill's checks file
  because the official skill does not cover it yet.
- Defining business concepts and relationships: `de-ontology-design`. Star schemas and metric views:
  `de-data-modeling`.
- Running the scan that classifies data: that is the Databricks Data Classification feature, enabled by a catalog
  owner; this skill reads and reviews its results.

## Changelog
- 0.1.1: score bands renamed Strong / Good / Weak / Ungoverned so they are not confused with bronze / silver / gold layers.
- 0.1.0: initial: read-only Unity Catalog governance assessment with 22 checks mapped to the CDMC 14 key controls,
  completeness score and bands, maturity per CDMC component, classification-to-protection reconciliation, ABAC and
  governed-tag proposals, certification rubric, recognized-steward operating model, score history, human-run apply
  script. Built from a survey of existing governance skills and repos and of DAMA-DMBOK2, CDMC, DCAM, Seiner, Plotkin,
  Ladley, Eryurek et al. and Dehghani (see `references/frameworks.md`).
