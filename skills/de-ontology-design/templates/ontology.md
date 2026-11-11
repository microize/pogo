# Ontology design: <domain>

Status: DRAFT | Version: 1 | Owner: <email> | Date: <YYYY-MM-DD>
Catalog: `${catalog}` (dev value <catalog>) | Schemas: <list> | Purpose: knowledge graph | GraphRAG | glossary | integration
Decisions: `specs/ontology/<domain>/decisions.md` (append-only)

Evidence levels: **declared** (constraint, governed tag, comment, metric view, contract) | **inferred** (names and
counts, numbers given) | **assumed** (proposal, needs the owner).

## 1. Scope and competency questions

| # | Competency question (business words) | Asked by |
|---|---|---|
| CQ1 | | |

Owner of definitions: <name / team>. Sources in scope: <systems>.

## 2. Concepts

| Concept | Definition | Kind (entity / event / association) | Source tables | Identifier | Evidence | Owner confirmed |
|---|---|---|---|---|---|---|

## 3. Properties

| Concept | Property | Definition | Type | Single / multi | Unit or currency | Source column | Sensitivity | Evidence |
|---|---|---|---|---|---|---|---|---|

## 4. Relationships

| Subject | Relationship (verb phrase) | Object | Inverse | Cardinality | Time-varying | Source (FK or columns) | Evidence (with %) |
|---|---|---|---|---|---|---|---|

## 5. Vocabularies and hierarchies

| Vocabulary or hierarchy | Terms (count only; labels only from a lookup table the owner confirms is non-sensitive reference data) | Source | Broader / narrower | Evidence |
|---|---|---|---|---|

## 6. Identity across sources

| Concept | Sources | Candidate match keys | Match share (counts) | Conflicts | Status (resolved / unresolved) |
|---|---|---|---|---|---|

## 7. Competency question coverage

| CQ | Path (concept -relationship-> concept ...) | Answerable now (yes / partly / no) | Missing data |
|---|---|---|---|

## 8. Excluded tables and why

| Table | Reason (technical, measure, duplicate of concept X, out of scope) |
|---|---|

## 9. Open questions for the owner

1.

## 10. Next steps

- Build (node and edge tables, entity resolution, export or sync): new track via `de-sdd-spec`.
- Semantic layer (metric views, Genie Agents): `de-data-modeling`.
- Contracts for consumers of the graph: `de-data-contract`.

## Changelog

| Version | Date | Change | By |
|---|---|---|---|
| 1 | | initial draft | |

On approval: `Status: REVIEWED (by <owner>, <date>)` and the verbatim reply in this changelog.
