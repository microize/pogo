# Deriving concepts, properties and relationships from tables (reference)

Use these rules as defaults; record any exception in the ontology file with its reason.

## Table classification

| Signals in Unity Catalog and the profile | Classify as | Becomes |
|---|---|---|
| Primary key (declared or 100% distinct, 0 nulls); descriptive columns; referenced by other tables | **Entity** | Concept (class) |
| One row per occurrence with a timestamp and one or more foreign keys (orders, payments, visits, shipments) | **Event** | Concept with relationships to the entities involved (not a plain edge: it has its own properties and time) |
| Two foreign keys forming the key, few or no other columns | **Association** (many-to-many) | Relationship; if it has attributes (role, quantity, valid dates), an association concept |
| Small distinct set (rule of thumb: under ~200 values) of codes with labels; or a lookup table | **Vocabulary** | Controlled vocabulary (concept scheme): term count, and labels only from non-sensitive lookup tables the owner confirms; not a class |
| `valid_from` / `valid_to` / `is_current` or `__START_AT` / `__END_AT` | **History** of an entity | Time-varying properties of that entity; not a separate concept |
| Daily or periodic snapshot of the same entity | **Snapshot** | Properties with "as of" time on the entity; not a separate concept |
| Aggregates and KPIs (gold facts, metric views) | **Measure** | Stays in the semantic layer; link the concept to the metric view |
| Staging, quarantine, audit, run logs, `_test` schemas | **Technical** | Excluded |

The same real-world thing in several tables (CRM customer, billing account, web user) is **one concept with several
source mappings**, not three concepts. Flag the identity question (step 8).

## Properties

- Every non-key, non-technical column of an entity is a candidate property. Drop audit columns (`_ingest_ts`,
  `_source_file`, `_run_id`, `_rescued_data`) and hashes used only for change detection.
- Type mapping for exports:

| Databricks type | XSD | LinkML range |
|---|---|---|
| STRING | xsd:string | string |
| INT, BIGINT | xsd:integer | integer |
| DECIMAL(p,s) | xsd:decimal | decimal |
| DOUBLE, FLOAT | xsd:double | double |
| BOOLEAN | xsd:boolean | boolean |
| DATE | xsd:date | date |
| TIMESTAMP | xsd:dateTime | datetime |
| ARRAY<T> | multi-valued property of T | multivalued: true |
| STRUCT | a nested concept or flattened properties (say which) | class or inlined |

- Amounts carry their currency (a currency column or a fixed currency in the definition); quantities carry their
  unit. Missing units are an open question.
- **Identifier**: the key used to refer to the thing across systems (business key), not the surrogate key, unless
  no business key exists.
- **Sensitivity**: take PII / classification from governed tags; a PII property is listed but marked, and the
  export never includes sample values.
- Hashed values (`*_hash`) are properties only if a consumer needs them for matching; otherwise exclude.

## Relationships

- **Declared**: a foreign key constraint. Evidence level declared.
- **Inferred**: a column whose name matches another table's key (`customer_id` -> `customers.customer_id`, or a
  documented alias) **and** at least 95% of its non-null distinct values exist in the parent key. Report the
  percentage. Below 95%: a candidate with a data-quality finding, not a relationship.
- Cardinality from counts: per parent key, max and average number of children; per child row, number of parents
  (0..1, 1, 0..*, 1..*). A relationship with 0 matches on most rows is optional; say so.
- Naming: a verb phrase from subject to object ("Customer places Order", inverse "Order placed by Customer"). Avoid
  generic names ("has", "related to") unless nothing better fits.
- Self-reference (`parent_id`, `manager_id`): part-of or reports-to; check for cycles with a recursive query before
  calling it a hierarchy.
- Time: when the link changes over time (customer's segment, account's owner), record it as time-varying (from SCD2
  history) rather than a static link.

## Subclasses vs vocabularies

- A type column becomes **subclasses** only when the subsets have different properties (columns mostly NULL for one
  type and filled for another) or different relationships. Otherwise it is a **vocabulary** property.
- Do not create a deep class tree from a category column; two levels is usually enough.

## Identity across sources

- For each concept with several source tables: the candidate match keys (email hash, tax id, external id), the share
  of records that match on each key (counts only), and conflicts (different formats, many-to-one matches).
- Below roughly 90% clean matches, mark the concept "identity unresolved": a knowledge graph built on it will
  duplicate or wrongly merge nodes. Entity resolution is a prerequisite build task.

## Counts-only profile queries (shape)

```sql
-- candidate key
SELECT count(*) AS n, count(DISTINCT <col>) AS n_distinct, count_if(<col> IS NULL) AS n_null FROM <table>;

-- inferred relationship: share of child values found in the parent key
SELECT count(DISTINCT c.<fk>) AS child_values,
       count(DISTINCT CASE WHEN p.<pk> IS NOT NULL THEN c.<fk> END) AS matched
FROM <child> c LEFT JOIN (SELECT DISTINCT <pk> FROM <parent>) p ON c.<fk> = p.<pk>
WHERE c.<fk> IS NOT NULL;

-- cardinality per parent
SELECT max(k) AS max_children, avg(k) AS avg_children
FROM (SELECT <fk>, count(*) AS k FROM <child> GROUP BY <fk>);
```

Combine several checks into one statement with `UNION ALL` of labelled rows to keep warehouse time low.

## Export notes

- OWL in Turtle: one `owl:Class` per concept, `owl:DatatypeProperty` with `rdfs:range` per property,
  `owl:ObjectProperty` with domain, range and `owl:inverseOf` per relationship, `rdfs:comment` from the definition,
  `skos:ConceptScheme` / `skos:Concept` for vocabularies. Mark assumed items with a comment. Use the namespace the
  user gives; never invent a public URL.
- LinkML YAML: classes, slots, enums (vocabularies), `identifier: true` on the identifier slot. LinkML can generate
  JSON Schema, SHACL and Pydantic from it later; that runs in a notebook and is the build track's choice.
- Exports are text in the ontology folder; nothing is loaded anywhere.

## Review checklist

1. Every competency question has a path or a listed gap.
2. Every concept has a definition, kind, identifier, source tables and an evidence level.
3. No concept duplicates another under a different name; same-thing tables are merged with source mappings.
4. Every relationship has a direction, verb-phrase name, inverse, cardinality from counts, and evidence (with %).
5. Code lists are vocabularies, not classes, unless subsets carry different properties.
6. Measures stay in the semantic layer; audit and technical columns are excluded.
7. PII properties are marked from tags; no row values anywhere in the file.
8. Identity across sources is resolved or marked unresolved with match shares.
9. Inferred and assumed items are labelled as such; open questions are listed for the owner.
10. Exports (if any) match the tables and mark assumed items.
