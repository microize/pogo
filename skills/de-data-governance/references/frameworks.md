# Frameworks behind the checks, roles and maturity

What each source contributes, in operational form. The CDMC controls and DMBOK 3.0 status were checked on the web
(2026-11-12); book content is summarised from the books: verify page references before quoting them to an auditor.

## EDM Council CDMC: 6 components, 14 key controls

Components: Governance and accountability; Cataloguing and classification; Accessibility and usage; Protection and
privacy; Data lifecycle; Data and technical architecture.

| # | Key control (short) | Unity Catalog evidence | Checks |
|---|---|---|---|
| C1 | Data control compliance: controls on sensitive data are monitored with metrics and notifications | this skill's scorecard, `history.md` cadence, alerts | score, G17 |
| C2 | Ownership field: sensitive data has an owner in the catalog | `*_owner` columns, `business_owner` / `steward` tags | G01, G02, G03 |
| C3 | Authoritative sources and provisioning points registered | `authoritative` tag, contracts | G18 |
| C4 | Data sovereignty and cross-border movement recorded and controlled | storage locations and regions (admin evidence), sharing | G19 |
| C5 | Cataloguing automatic at creation, across environments | UC itself, comments, domain tags | G04, G05, G06 |
| C6 | Classification automatic and always on (PII, sensitivity, MNPI, client-identifiable, org classes) | Data Classification, `class.*`, governed tags | G07, G08 |
| C7 | Entitlements: access to sensitive data defaults to creator and owner; all access tracked | grants, `system.access.audit` | G11, G12 |
| C8 | Consumption purpose recorded in sharing agreements | Request for access (partial), contracts | G13 |
| C9 | Security controls on sensitive data, with evidence in the catalog | masks, row filters, ABAC policies | G09, G10 |
| C10 | Data protection impact assessments triggered for personal data | `dpia_ref` tag or contract link | G21 |
| C11 | Retention, archiving and purging per schedule | `retention` tag, erasure procedure | G16 |
| C12 | Data quality measured and shared for sensitive data | Data Quality Monitoring, Data Profiling, DQ rules | G15 |
| C13 | Cost metrics for use, storage and movement | `system.billing.usage` with tags | G20 |
| C14 | Lineage for sensitive data at least back to source | `system.access.table_lineage` / `column_lineage` | G14 |

Source: EDM Council "CDMC 14 Key Controls" PDF; Google Cloud's CDMC reference architecture (GitHub
`GoogleCloudPlatform/cdmc`) maps the same controls to catalog tag fields and inspired G03, G16, G18, G19, G21.

## Operating model: roles

| Source | Contribution used here |
|---|---|
| Seiner, *Non-Invasive Data Governance* | **Recognize, do not assign.** People who already define, produce and use data are recognized as stewards. Levels: strategic (executive team), tactical (domain stewards, cross-functional), operational (definers, producers, users), support (IT, security, legal, audit) and the governance team. This skill infers candidates from ownership, writes and reads (lineage) and proposes them. |
| Plotkin, *Data Stewardship* | Business data stewards per domain, technical stewards, project and operational stewards, a stewardship council. Steward metrics: terms defined and approved, issues resolved and time to resolve, rule coverage. |
| DAMA-DMBOK2 (revised 2024; DMBOK 3.0 targeted for 2027, not published) | Bodies: governance council, governance office, stewardship teams. Steward types: chief, executive, enterprise, business, data owner, technical, coordinating. Deliverables: charter, policies and standards, glossary, metadata repository, issue log, scorecard. Metrics in three groups: value, effectiveness, sustainability. |
| Ladley, *Data Governance* | Principles before policies; every policy has an owner and a measure; separate governance (ensure it is done right) from management (do it). |
| Eryurek et al., *Data Governance: The Definitive Guide* | Lifecycle: discover, classify, apply policy by class, monitor and audit. Classification automated at ingest; policies attach to classes, not tables. |
| Dehghani, *Data Mesh* | Federated computational governance: a few global policies (access, privacy, retention, interoperability) enforced by the platform on every data product, domains decide the rest. Measure policy coverage per product. |

### RACI for this kit's governance artefacts

| Artefact or action | Governance lead | Business owner | Steward | Asset owner (UC OWNER group) | Admin | Agent (this skill) |
|---|---|---|---|---|---|---|
| Taxonomy (`taxonomy.md`) | A | C | C | I | C | R (draft) |
| Classification review per column | I | A | R | C | I | R (proposal) |
| Comments and definitions | I | A | R | C | - | R (draft) |
| Tags applied (`apply_<n>.sql` block A) | I | I | C | A / R | - | - |
| Ownership change, grants, ABAC policies (blocks B, C) | A | C | I | C | R | - |
| Certification / deprecation | C | A | R | R | - | R (proposal) |
| Assessment and recheck | A | I | I | I | I | R |

R responsible, A accountable, C consulted, I informed. The agent never holds A.

## Maturity scales (crosswalk)

This skill scores 0 to 5 per CDMC component (`governance-checks.md`, section 3). Equivalents for reporting:

| This skill | DCAM (1 to 6) | Gartner EIM | CMM / DMBOK / IBM |
|---|---|---|---|
| 0 Not started | 1 Not initiated | 0 Unaware | 0 Incomplete |
| 1 Ad hoc | 2 Conceptual | 1 Aware | 1 Initial |
| 2 Developing | 3 Developmental | 2 Reactive | 2 Repeatable / Managed |
| 3 Defined | 4 Defined | 3 Proactive | 3 Defined |
| 4 Managed | 5 Achieved | 4 Managed | 4 Quantitatively managed |
| 5 Automated | 6 Enhanced | 5 Effective | 5 Optimizing |

## Ideas taken from existing open-source work (surveyed 2026-11-12)

| Source | Idea used |
|---|---|
| OpenMetadata (Apache-2.0) | completeness score with quality bands feeding certification; every tag, owner or description change goes through an approval task |
| Google Cloud CDMC reference architecture (Apache-2.0) | one check per CDMC control, tag fields per control |
| Google devrel "knowledge catalog governance" agent (Apache-2.0) | certified-and-classified before an agent may use an asset |
| Databricks Labs DiscoverX | show every generated bulk statement before it runs, batched per schema |
| Bitol Open Data Contract Standard v3.1 (Apache-2.0) | field names for classification, critical data elements and owner / steward roles in hand-offs to contracts |
| DataHub | ownership types (technical owner, business owner, steward) beyond the single UC owner |
| dbdemos ABAC notebook | `CREATE POLICY ... MATCH COLUMNS has_tag_value(...)` pattern |

Gaps none of them covered, which this skill fills: a read-only, scored Unity Catalog audit; governed-tag and ABAC
proposals; reconciling Data Classification with protection; a certification rubric for UC; an approval-gated,
workspace-only flow for Genie Code.
