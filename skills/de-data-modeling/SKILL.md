---
name: de-data-modeling
description: Dimensional and lakehouse data modeling for Databricks, for data modelers and architects. Use when the user asks to design or review a data model, star schema, bus matrix, conformed dimensions, fact grain, dimension design, surrogate keys, SCD per attribute, logical or physical model, ERD or model diagram, or "model review" of an existing gold layer. Produces specs/models/<model>/model.md (business processes, bus matrix, grain, logical and physical model, Mermaid diagram, validation queries), runs a review step and hands the approved model to de-sdd-spec. Never writes pipeline code.
metadata:
  version: "0.1.0"
---

# de-data-modeling: model first, then spec, then build

You design the model that the spec and the pipeline implement. Output is documentation and validation SQL, not
pipeline code (that is `de-sdd-implement`, after an approved spec). Rules and patterns are in
`references/modeling-rules.md`; the output shape is `templates/model.md`.

## Modes

- **Design** (new or extended model): steps 1 to 8.
- **Review** (existing gold or silver layer): step 1, then compare what exists against `references/modeling-rules.md`
  and write findings (Blocker / Major / Minor, each with the fix) into `specs/models/<model>/review_<n>.md`.

## Design steps

1. **Discover (read before you ask).** Project root = folder holding `AGENTS.md`. Read `specs/project-profile.md`
   (including the Environment section from `de-env-check`), existing `specs/models/`, specs and contracts. List
   existing tables and columns with `information_schema.columns` for the named catalogs (structure only, no row
   values). Profile candidate keys and cardinalities with counts only (`count(*)`, `count(DISTINCT key)`).
2. **Business processes and questions.** Ask at most 5 questions per round, with recommended answers: which
   processes (orders, payments, shipments...), which questions and KPIs, who consumes (BI, Genie Agents, ML), latency,
   history needs. Record answers in `specs/models/<model>/decisions.md` (append-only).
3. **Bus matrix.** Processes as rows, conformed dimensions as columns. A dimension used by two processes is conformed:
   one table, one key, shared. Flag dimensions that exist twice under different names.
4. **Grain per fact.** State "one row per ..." and prove it on data: `count(*) = count(DISTINCT <grain columns>)` on the
   source or silver table. Choose the fact type (transaction, periodic snapshot, accumulating snapshot) and classify
   each measure (additive, semi-additive, non-additive).
5. **Dimension candidates.** List every text, code, flag, date and geo field from the sources with cardinality and an
   `Include Y/N` column for the user. Never drop a field silently. Decide per dimension: SCD type per attribute
   group, deterministic surrogate key, unknown row (`-1`), role-playing (dates), junk and degenerate dimensions. Always
   a date dimension.
6. **Physical model on Databricks.** Fully qualified Unity Catalog names, layer and dataset type (streaming table,
   AUTO CDC target, materialized view, metric view), data types, nullability, informational primary and foreign key
   constraints, `CLUSTER BY AUTO` or chosen keys, column comments, PII tags. KPI definitions that BI or Genie Agents
   reuse become Unity Catalog metric views (official `databricks-metric-views` skill for syntax).
7. **Diagram and validation.** A Mermaid `erDiagram` in `model.md`, and validation queries (pass/fail only) for grain
   uniqueness, orphan foreign keys, unknown-row share, one current row per SCD2 key, conformed-dimension consistency,
   and measure reconciliation against silver.
8. **Review and hand-off.** Self-check against the checklist in `references/modeling-rules.md`; for models with more
   than two facts or any conformed dimension, recommend a fresh-eyes review (new chat:
   `@de-goldfish-review specs/models/<model>/model.md`). Ask: "Reply `approved` to approve the model, or tell me what to
   change." On approval, record the verbatim reply in `model.md`, then hand to `de-sdd-spec` (new track, or an
   amendment of an existing track: targets in section 4, entities in 4b, T-xx blocks, acceptance criteria from the
   validation queries).

## Rules

- Names come from the user's answers and the project profile; parameterize the catalog.
- Read structure and counts, never row values, from data tables.
- A model change to keys, grain or SCD type on a built track is a **Major** amendment in `de-sdd-spec`.
- Record struggles (missing access, ambiguous keys) through `de-sdd-tracking`.

## Changelog
- 0.1.0: initial; dimensional rules moved here from de-databricks-current/references/patterns.md; replaces the old
  generic data-modeling skill (partition-by-date advice dropped in favor of liquid clustering).
