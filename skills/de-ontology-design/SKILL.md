---
name: de-ontology-design
description: Ontology and knowledge-graph design from data already in Databricks, for data modelers and architects. Use when the user asks which concepts, entities, properties or relationships the data supports, to design or review an ontology or concept model, to prepare data for a knowledge graph or GraphRAG, or for glossary terms from tables. Produces specs/ontology/<domain>/ontology.md (concepts, properties, relationships, vocabularies, identity, competency-question coverage, each with evidence) from Unity Catalog metadata and counts-only profiles; optional OWL or LinkML text. Advisory only: never builds graph tables, loads a graph database or changes data.
metadata:
  version: "0.1.2"
---

# de-ontology-design: what concepts our data can support

You tell the user which concepts, properties and relationships the data in Unity Catalog can support for an ontology
or knowledge graph, how strong the evidence is, and what is missing. You do **not** build the graph: no node or edge
tables, no graph database loads, no pipeline code. Building is a separate track (`de-sdd-spec`), using this design as
its input.

Rules for turning tables and columns into concepts: `references/derivation-rules.md`. Output shape:
`templates/ontology.md`.

## Ground rules

- **Read-only.** Metadata from `information_schema` and Unity Catalog; profiles are counts only (`count`,
  `count(DISTINCT ...)`, null counts, overlap counts). Never select row values (one exception: labels of a code or lookup table the owner confirms is non-sensitive reference data); never print PII. Batch the profile:
  **at most three approvals per run** (one inventory, one profile, one overlap / cardinality pass), each a single
  Python cell that runs all its `spark.sql` reads and prints one summary, never one query per table. Run on the compute
  the user names; otherwise a Unity Catalog-capable one (the team's SQL warehouse, or a Dedicated / Standard cluster),
  never a no-isolation cluster (`UC_NOT_ENABLED`).
- **Evidence on every item.** Each concept, property and relationship is marked **declared** (PK/FK constraint,
  governed tag, comment, metric view, existing contract), **inferred** (name and count evidence, with the numbers) or
  **assumed** (your proposal, needs a business owner). Never present inferred or assumed items as facts.
- **The business owns the meaning.** You propose names and definitions; the user or a named owner confirms them.
  Open questions go in the file, not into silent choices.
- Record struggles (no access to `information_schema` or lineage, ambiguous keys, failed queries) through
  `de-sdd-tracking` in `.challenges_<your-email>/ontology-<domain>.md`, redacted.
- Current names: Unity Catalog governed tags, metric views, Discover domains, Pages (glossary) and Genie Ontology (GA per
  the Nov 2026 release notes; see `de-databricks-current`), all optional. Sensitivity of properties comes from the
  governed tags that `de-data-governance` proposes.

## Steps

1. **Discover (read before you ask).** Project root = folder holding `AGENTS.md`. Read `specs/project-profile.md`
   (including the Environment section from `de-env-check`: which SQL warehouse to use), existing `specs/ontology/`,
   `specs/models/` and `specs/contracts/`. Then ask for scope once, up to 5 questions in one message, recommended
   answer first. Domain and purpose (knowledge graph, GraphRAG, glossary,
   integration across sources); catalogs and schemas in scope (default: silver and gold, not bronze); the
   **competency questions** the result must answer (3 to 10, in business words); known source systems for the same
   entities; who owns definitions. Record the answers in `specs/ontology/<domain>/ontology.md` section 1 and in
   `specs/ontology/<domain>/decisions.md` (append-only).
2. **Inventory (read before proposing).** In one batched pass: `information_schema.tables` and `.columns` (names,
   types, comments), `.table_constraints` / `.key_column_usage` (PK/FK), `.table_tags` / `.column_tags`, metric
   views in scope, existing `specs/models/`, `specs/contracts/` and spec glossaries. Column and table lineage from
   `system.access.column_lineage` only if granted (say so if not).
3. **Profile (counts only).** For candidate keys: rows vs distinct values and nulls. For candidate relationships
   (FK-like columns without constraints): share of child values found in the parent key. For category columns:
   distinct count (small sets are vocabularies). Rules and thresholds: `references/derivation-rules.md`.
4. **Propose concepts.** Classify each table: entity, event, association, vocabulary, snapshot / history, or
   technical (staging, quarantine, audit: excluded). Merge tables that describe the same real-world thing into one
   concept with several source mappings, and flag the identity question.
5. **Propose properties.** Attributes become properties with datatype (XSD type in the export), cardinality
   (single / multi), unit or currency, identifier flag and sensitivity (from tags). Measures and KPIs stay in the
   semantic layer (metric views), not in the ontology; link them instead.
6. **Propose relationships.** From declared FKs first, then inferred ones that pass the overlap rule. Give each a
   verb-phrase name and direction ("Customer places Order"), its inverse, and cardinality from the counts.
   Relationships that carry their own attributes (quantity, role, valid dates) become association or event concepts.
7. **Hierarchies and vocabularies.** Self-references (`parent_id`) become part-of or broader / narrower links; type
   or category columns become controlled vocabularies (SKOS-style concept schemes), and become subclasses only when
   the subsets carry different properties.
8. **Identity and conflicts.** One identifier per concept; for concepts fed by several sources, list the candidate
   match keys and the conflicts found (different key formats, overlapping but unequal populations). Resolving
   identity is a build task, not this skill's; record it as a prerequisite.
9. **Check against the competency questions.** For each question, write the path of concepts and relationships that
   answers it, or list the missing data. A question with no path is a gap, not a reason to invent a relationship.
10. **Write, review and hand back.** Fill `templates/ontology.md` into `specs/ontology/<domain>/ontology.md` (full
    workspace path; read it back). Self-check against the checklist in `references/derivation-rules.md`. For more than
    about 15 concepts or more than one domain, recommend a fresh-eyes review (new chat:
    `@de-goldfish-review specs/ontology/<domain>/ontology.md`). Ask: "Reply `approved` to accept the design, or tell me
    what to change." On approval, set `Status: REVIEWED`, record the owner and the verbatim reply in the changelog and
    `decisions.md`. Export only when asked: OWL in Turtle text or LinkML YAML text, generated from the tables in the file,
    with assumed items marked in comments. End with: open questions for the owner, gaps, and next steps (build track
    via `de-sdd-spec`; semantic layer via `de-data-modeling`; contracts via `de-data-contract`).

## Review mode

When the user already has an ontology or glossary (file, Pages, an OWL file): map each concept and property to tables
and columns, and report: concepts with no data, data with no concept, type and cardinality mismatches against the
profile, and competency questions it cannot answer. Findings as Blocker / Major / Minor, with the evidence.

## Not this skill

- Building node or edge tables, entity resolution pipelines, exports or syncs to a graph database: a build track via
  `de-sdd-spec`, then `de-sdd-implement`.
- Star schemas, metric views and Genie Agent setup: `de-data-modeling`.
- Schema change impact on consumers: `de-data-contract`. Rules that validate data: `de-quality-testing`.

## Changelog
- 0.1.2: live test fixes: profiling sent about 12 separate queries (12 approvals); now at most three batched cells. Compute: the one the user names, else a Unity Catalog-capable one.
- 0.1.1: status of Domains, Pages and Genie Ontology updated; sensitivity from de-data-governance tags.
- 0.1.0: initial: concepts, properties, relationships, vocabularies, hierarchies and identity proposed from Unity
  Catalog metadata and counts-only profiles, with evidence levels and competency-question coverage; optional OWL or
  LinkML text export. Advisory only.
