# Unity Catalog governance features: status and how to read them

Checked: **2026-11-12** against docs.databricks.com (AWS) and the release notes for September to November 2026.
Recheck when this date is older than 60 days, and say the status whenever you recommend a feature. Azure and GCP
pages can lag; check your cloud's page.

| Feature | Status | Read state with | Notes |
|---|---|---|---|
| Governed tags (tag policies) | GA | `system.information_schema.{catalog,schema,table,column,volume}_tags`; SDK `entity_tag_assignments` | tag permissions `CREATE`, `MANAGE`, `ASSIGN` (account or per tag); assigning also needs `APPLY TAG` on the object. Limits: 50 tags per object, 1,000 column tags per table, 256 characters. Docs: /admin/governed-tags/ |
| System tags (`class.*`, `system.certification_status`) | predefined, read-only | same views | |
| Automated tag assignment, custom classifiers, tag propagation through lineage | Beta | - | do not make them the default path |
| Tags on dashboards, notebooks, apps, Genie Agents | GA (Sep 2026) | - | |
| Data Classification | GA; classification API GA (Oct 2026); auto-tagging configuration Public Preview; classifying views Beta | `system.data_classification.results` (serverless only; account admin until granted; columns unverified, holds sample values) | enabling needs catalog owner or `MANAGE`; new results about every 24 h. Docs: /data-governance/unity-catalog/data-classification |
| ABAC row filter and column mask policies | GA; metastore-level, DENY, views and shared-object policies Beta | `SHOW [EFFECTIVE] POLICIES ON ...`, `DESCRIBE POLICY`, `system.information_schema.abac_policy_definitions` (only where you have `MANAGE`) | governed tags only; serverless or DBR 16.4+; per catalog or schema 100 policies, per table 50, 20 principals per policy. Conflicts fail queries; MV / ST owners must be in `EXCEPT`; clones blocked; AI Search indexes do not inherit. Docs: /data-governance/unity-catalog/abac/policies |
| Column masks and row filters (per table) | GA | `system.information_schema.column_masks`, `row_filters` (columns unverified) | official `databricks-unity-catalog/references/4-fine-grained-access.md` |
| Certify / deprecate (`system.certification_status`) | current AWS page shows no preview label; older copies said Preview: treat as probably GA, unverified | `table_tags` where `tag_name = 'system.certification_status'` | needs `ASSIGN` on the tag and `APPLY TAG`. Docs: /data-governance/unity-catalog/certify-deprecate-data |
| Request for access destinations | GA (Oct 2026) | Access request destinations API / SDK, UI | email, Slack, Teams, webhook; inherited down the hierarchy |
| Discover page and domains | GA (Oct 2026) | UI (API unverified) | curators need `MANAGE DISCOVER` or `MANAGE` on a domain |
| Pages (governed business definitions) | GA (Nov 2026) | UI | `MANAGE PAGES`; can be certified or deprecated; closest to a glossary |
| UC wikis | Beta (Nov 2026) | UI | |
| Genie Ontology | GA (Nov 2026) | - | context layer on UC semantics; see `de-ontology-design` |
| Ownership, comments | GA | `*_owner`, `comment` in information_schema; `SHOW GRANTS`; `*_privileges` views | AI-generated comments: per object in Catalog Explorer, human review required, never evidence of classification |
| `system.access.audit` | Public Preview per the system tables index | SQL | |
| `system.access.table_lineage`, `column_lineage` | available | SQL | external lineage (BI, upstream) GA |
| Data Quality Monitoring (anomaly detection) | GA (Oct 2026) | `system.data_quality_monitoring.table_results` (account admin until granted; columns unverified) | freshness and completeness per schema; billed separately |
| Data Profiling (formerly Lakehouse Monitoring) | GA | profile and drift metric tables in a chosen schema | needs `MANAGE` on the table |
| Governance Hub | Beta / Private Preview (account admins) | UI | posture views and read-only tag recommendations |

Sources: governed tags, tag permissions, data classification, ABAC policies and requirements, certify / deprecate,
access request destinations, Discover page, system tables, anomaly detection, data profiling and AI comments pages
on docs.databricks.com; Databricks release notes Sep, Oct and Nov 2026; Databricks blogs on the ABAC / governed tags
/ classification GA and on Unity Catalog at Data + AI Summit 2026.
