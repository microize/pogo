# Governance checks, SQL and scoring

All queries are read-only, counts and metadata only. Replace `${catalogs}` with the quoted catalog list in scope
(`'prod_sales','prod_crm'`). Columns marked **unverified** were not confirmed in the docs at the time of writing:
run `DESCRIBE TABLE <name>` first and adapt the column names; never fall back to `SELECT *` on a results table that
holds sample values.

## 1. The checks

Severity: **Blocker** (sensitive data exposed or unaccountable), **Major** (control missing on data people use),
**Minor** (hygiene). Confidence: `measured`, `inferred`, `assumed`. CDMC = EDM Council Cloud Data Management
Capabilities key control (list in `frameworks.md`).

| Id | Check | Pass when | CDMC | Severity if failed |
|---|---|---|---|---|
| G01 | Owner present and accountable | owner is a group or service principal, not an individual (owner containing `@` is an individual: `inferred`) | C2 | Major; Blocker on sensitive |
| G02 | Owner still active | the owning user or group still exists and is active (SDK `w.users.list` / `w.groups.list`; skipped without access) | C2 | Major |
| G03 | Business owner and steward recorded | governed tags `business_owner` and `steward` on the table, or inherited from the schema | C2 | Minor; Major on sensitive |
| G04 | Table described | table comment of at least 20 characters that is not the table name | C5 | Minor; Major on gold |
| G05 | Columns described | at least 90% of columns have a comment of at least 10 characters | C5 | Minor; Major on gold |
| G06 | Placed in a domain | governed tag `domain` set (table, schema or catalog), or the asset is in a Discover domain (UI check) | C5 | Minor |
| G07 | Classification running | Data Classification enabled on the catalog and results newer than 7 days | C6 | Major |
| G08 | Classification reviewed | every column with a `class.*` system tag also has the governed column tags `sensitivity` and `personal_data`; every table has `sensitivity` | C6 | Major; Blocker when a `class.*` column has neither |
| G09 | Sensitive columns protected | every column with `sensitivity` in (`confidential`, `restricted`) or `personal_data` <> `none` is covered by a column mask, a row filter on the table, an ABAC policy, or a waiver in `instructions/waivers.md` | C9 | Blocker |
| G10 | Policies consistent | no ABAC policy matches zero columns; no sensitivity tag set only at table level where ABAC is used; tags referenced by policies listed as "do not delete" | C9 | Major |
| G11 | Least privilege | no grant on in-scope objects to an individual user, to `account users` / `users`, or of `ALL PRIVILEGES`; on sensitive objects no `MODIFY` beyond the run-as principal | C7 | Major; Blocker on sensitive |
| G12 | Access audited and reviewed | `system.access.audit` readable; distinct principals reading each sensitive table in 30 days listed for owner review | C7 | Major |
| G13 | Access can be requested | a Request for access destination set on the catalog, schema or table | C8 (partial) | Minor |
| G14 | Lineage to source | the table has upstream lineage rows in 90 days, back to an ingestion table or volume | C14 | Major on sensitive and gold; else Minor |
| G15 | Quality measured | Data Quality Monitoring anomaly detection enabled on the schema, a Data Profiling monitor on the table, or Critical rules for it under `tests/` / pipeline expectations | C12 | Major on sensitive and gold |
| G16 | Retention recorded | personal-data tables carry governed tag `retention` (for example `p1y`, `p7y`, `legal_hold`) and the project has an erasure / purge procedure (`de-databricks-current/references/patterns.md`) | C11 | Major on personal data |
| G17 | Certification honest | consumer-facing gold tables and metric views that meet the rubric (section 4) are `certified`; no `certified` asset fails the rubric; `deprecated` assets have no reads in 30 days | C1 | Major |
| G18 | Authoritative source recorded | the system-of-record table for each key entity carries governed tag `authoritative` = `true` | C3 | Minor |
| G19 | Location recorded | storage location and region of sensitive catalogs recorded in `specs/governance/taxonomy.md` (user-run evidence from Catalog Explorer or the admin) | C4 | Minor; Major under data-residency rules |
| G20 | Cost attributable | jobs and pipelines writing in-scope tables carry cost tags (`custom_tags` present in `system.billing.usage`) | C13 | Minor |
| G21 | Impact assessed | personal-data tables carry governed tag `dpia_ref` or the contract links a DPIA | C10 | Major under GDPR; else skipped |
| G22 | Not stale | assets with no reads in 90 days and no group owner are listed as deprecation candidates | lifecycle | Minor |

A check whose source is unreadable is `skipped` with the reason; it scores neither pass nor fail and is listed in the
report's "not measured" box.

## 2. Completeness score per table (0 to 100)

| Points | From |
|---|---|
| 15 | G01 owner is a group or service principal |
| 10 | G03 business owner and steward tags |
| 15 | G04 table comment |
| 15 | G05 column comment coverage (points x share commented, rounded) |
| 5 | G06 domain |
| 15 | G08 classification reviewed (tables with no sensitive column: `sensitivity` tag set) |
| 15 | G09 sensitive columns protected (full points when the table has no sensitive column) |
| 5 | G14 lineage |
| 5 | G15 quality measured |

Skipped checks are removed from the denominator (score = points / available points x 100) and the report says so.
Bands: **Strong** 90 or more, **Good** 75 to 89, **Weak** 50 to 74, **Ungoverned** below 50 (not named Gold / Silver /
Bronze, so they are never confused with medallion layers). Catalog and schema
scores are usage-weighted averages (weight = 1 + reads in 30 days, so unused tables count but do not dominate).
Report the sensitive-asset score on its own line.

## 3. Maturity per CDMC component (0 to 5)

| Level | Meaning | Evidence rule |
|---|---|---|
| 0 Not started | no control | component checks pass on under 10% of assets |
| 1 Ad hoc | some assets, by habit | 10% to 49% pass |
| 2 Developing | most assets, no written rule | 50% to 89% pass, no rule in `taxonomy.md` |
| 3 Defined | rule written and mostly met | rule in `taxonomy.md` and 50% to 89% pass, or 90%+ without monitoring |
| 4 Managed | met and monitored | 90%+ pass and a scheduled recheck (history rows at the agreed cadence) |
| 5 Automated | enforced by the platform | level 4 plus enforcement as code: auto-tagging from classification, ABAC policies, alerts on new untagged sensitive columns |

Components: Governance and accountability (G01 to G03, G17), Cataloguing and classification (G04 to G08), Access
and usage (G11 to G13), Protection and privacy (G09, G10, G21), Data lifecycle (G16, G22, G14), Architecture and cost
(G18 to G20, G15).

## 4. Certification and deprecation rubric

Propose `certified` only when **all** hold: band Strong; owner is a group; at least 95% of columns commented;
sensitivity reviewed (G08) and sensitive columns protected (G09); quality measured (G15) with no open Critical
failure; lineage to source (G14); read in the last 30 days; a data contract exists when the table has consumers
outside the owning team (`specs/contracts/`); a primary key where the grain is known. The owner sets it; the
statement is `SET TAG ON TABLE <t> \`system.certification_status\` = \`certified\`` (needs `ASSIGN` on the tag and
`APPLY TAG` on the object; check the syntax on the certify / deprecate docs page before running).

Propose `deprecated` when: no reads in 90 days and either no group owner or a successor named in a contract or spec;
or the asset is superseded by a track (`SUPERSEDED`). A deprecated asset that is still read is a Major finding with
the readers' count, so consumers can be told before removal. Removal itself is never this skill's step.

## 5. SQL by check family

Run each block once per scope; each returns counts or metadata only.

**Tables, owners, comments (G01, G04)**
```sql
SELECT table_catalog, table_schema, table_name, table_type, table_owner,
       table_owner LIKE '%@%'                                        AS owner_is_user,
       coalesce(length(trim(comment)), 0)                             AS comment_len,
       lower(trim(coalesce(comment, ''))) = lower(table_name)         AS comment_is_name,
       current_timestamp()                                            AS ts
FROM system.information_schema.tables
WHERE table_catalog IN (${catalogs}) AND table_schema <> 'information_schema';
```

**Column comment coverage (G05)**
```sql
SELECT table_catalog, table_schema, table_name, count(*) AS cols,
       count_if(length(trim(coalesce(comment, ''))) >= 10) AS commented
FROM system.information_schema.columns
WHERE table_catalog IN (${catalogs}) AND table_schema <> 'information_schema'
GROUP BY ALL;
```

**Tags at table level (G03, G06, G08, G16, G17, G18, G21)** (also read `schema_tags` and `catalog_tags` the same
way and treat their governed tags as inherited by the tables below)
```sql
SELECT catalog_name, schema_name, table_name,
       max(CASE WHEN tag_name = 'sensitivity' THEN tag_value END)                    AS sensitivity,
       max(CASE WHEN tag_name = 'domain' THEN tag_value END)                         AS domain,
       max(CASE WHEN tag_name = 'system.certification_status' THEN tag_value END)    AS certification,
       count_if(tag_name IN ('business_owner', 'steward'))                           AS owner_tags,
       count_if(tag_name = 'retention')                                              AS retention_tag,
       count_if(tag_name = 'authoritative' AND tag_value = 'true')                   AS authoritative,
       count_if(tag_name = 'dpia_ref')                                               AS dpia_tag
FROM system.information_schema.table_tags
WHERE catalog_name IN (${catalogs})
GROUP BY ALL;
```

**Tags at column level (G08, G09)**
```sql
SELECT catalog_name, schema_name, table_name,
       count(DISTINCT CASE WHEN tag_name LIKE 'class.%' THEN column_name END)                       AS class_cols,
       count(DISTINCT CASE WHEN tag_name = 'sensitivity'
                            AND tag_value IN ('confidential', 'restricted') THEN column_name END)  AS sensitive_cols,
       count(DISTINCT CASE WHEN tag_name = 'personal_data' AND tag_value <> 'none' THEN column_name END) AS personal_cols,
       count(DISTINCT CASE WHEN tag_name IN ('sensitivity', 'personal_data') THEN column_name END)  AS reviewed_cols
FROM system.information_schema.column_tags
WHERE catalog_name IN (${catalogs})
GROUP BY ALL;
```
Columns with a `class.*` tag but no `sensitivity` / `personal_data` tag (G08 list, names only):
```sql
SELECT c.catalog_name, c.schema_name, c.table_name, c.column_name, c.tag_name AS detected_class
FROM system.information_schema.column_tags c
WHERE c.catalog_name IN (${catalogs}) AND c.tag_name LIKE 'class.%'
  AND NOT EXISTS (SELECT 1 FROM system.information_schema.column_tags r
                  WHERE r.catalog_name = c.catalog_name AND r.schema_name = c.schema_name
                    AND r.table_name = c.table_name AND r.column_name = c.column_name
                    AND r.tag_name IN ('sensitivity', 'personal_data'));
```

**Protection (G09, G10)**: `DESCRIBE` first, columns **unverified**.
```sql
DESCRIBE TABLE system.information_schema.column_masks;
DESCRIBE TABLE system.information_schema.row_filters;
DESCRIBE TABLE system.information_schema.abac_policy_definitions;   -- lists only securables where you have MANAGE
```
Then select catalog, schema, table, column and policy or function names only. For the 20 most-read sensitive tables,
`SHOW EFFECTIVE POLICIES ON TABLE <t>` (needs `READ METADATA` or `MANAGE`). A sensitive column is protected when a
mask is on it, a row filter is on its table, or an effective policy's `MATCH COLUMNS` condition matches one of its
column tags (ABAC matches tags set directly on the column only).

**Privileges (G11)**: also `schema_privileges` and `catalog_privileges`.
```sql
SELECT table_catalog, table_schema, table_name, grantee, privilege_type
FROM system.information_schema.table_privileges
WHERE table_catalog IN (${catalogs})
  AND (grantee LIKE '%@%' OR lower(grantee) IN ('account users', 'users') OR privilege_type = 'ALL PRIVILEGES');
```

**Usage, lineage and steward candidates (G14, G22, operating model)**
```sql
-- reads per table in 30 days (usage weight, staleness, top readers)
SELECT source_table_full_name AS t, count(*) AS read_events, count(DISTINCT created_by) AS readers
FROM system.access.table_lineage
WHERE event_date >= current_date() - 30 AND source_table_full_name IS NOT NULL
  AND split_part(source_table_full_name, '.', 1) IN (${catalogs})
GROUP BY ALL;

-- upstream lineage present in 90 days
SELECT target_table_full_name AS t, count(DISTINCT source_table_full_name) AS upstreams
FROM system.access.table_lineage
WHERE event_date >= current_date() - 90 AND target_table_full_name IS NOT NULL
  AND split_part(target_table_full_name, '.', 1) IN (${catalogs})
GROUP BY ALL;

-- steward candidates: who writes and who reads most (identities only, top 3 per table, for proposals)
SELECT t, role, created_by, n FROM (
  SELECT t, role, created_by, n, row_number() OVER (PARTITION BY t, role ORDER BY n DESC) AS rk FROM (
    SELECT target_table_full_name AS t, 'writer' AS role, created_by, count(*) AS n
    FROM system.access.table_lineage
    WHERE event_date >= current_date() - 90 AND split_part(target_table_full_name, '.', 1) IN (${catalogs})
    GROUP BY ALL
    UNION ALL
    SELECT source_table_full_name, 'reader', created_by, count(*)
    FROM system.access.table_lineage
    WHERE event_date >= current_date() - 90 AND split_part(source_table_full_name, '.', 1) IN (${catalogs})
    GROUP BY ALL))
WHERE rk <= 3;
```
Lineage read events are a usage proxy, not a full access log; say so.

**Audit of sensitive tables (G12)**: request parameter names **unverified**; check one row's keys first.
```sql
SELECT request_params.full_name_arg AS t, count(DISTINCT user_identity.email) AS principals_30d
FROM system.access.audit
WHERE event_date >= current_date() - 30 AND service_name = 'unityCatalog' AND action_name = 'getTable'
  AND request_params.full_name_arg IN (<sensitive tables>)
GROUP BY ALL;
```

**Classification and quality results (G07, G15)**: readable only by the account admin until granted;
classification results need a serverless SQL warehouse; columns **unverified**.
```sql
DESCRIBE TABLE system.data_classification.results;           -- then select identifiers, class, confidence, scan time
DESCRIBE TABLE system.data_quality_monitoring.table_results;  -- then latest health state per table
```
Never select sample or example value columns from the classification results.

**Cost attribution (G20)**
```sql
SELECT count_if(size(custom_tags) > 0) AS tagged_rows, count(*) AS rows
FROM system.billing.usage
WHERE usage_date >= current_date() - 30 AND usage_metadata.job_id IS NOT NULL;
```

## 6. Proposal statement shapes (for `apply_<n>.sql`, run by a human)

Header of every apply file: scope, assessment version, approver per block, privilege needed per block, "run in this
order", and "verify with the recheck mode afterwards". Never include GRANT to `account users` or `ALL PRIVILEGES`.

```sql
-- Block A, asset owner (needs APPLY TAG on the object and ASSIGN on the governed tag)
ALTER TABLE prod_crm.gold.dim_customer ALTER COLUMN email SET TAGS ('sensitivity' = 'restricted', 'personal_data' = 'direct');
ALTER TABLE prod_crm.gold.dim_customer SET TAGS ('sensitivity' = 'restricted', 'domain' = 'customer', 'steward' = 'crm_stewards');
COMMENT ON TABLE prod_crm.gold.dim_customer IS '<draft, owner to confirm>';

-- Block B, admin (needs MANAGE on the schema); ABAC, GA; check syntax on the ABAC policies docs page first
CREATE POLICY mask_direct_identifiers
ON SCHEMA prod_crm.gold
COMMENT 'Mask direct personal identifiers for everyone except the PII readers group'
COLUMN MASK prod_crm.governance.mask_string
TO `crm_analysts`
EXCEPT `crm_pii_readers`
FOR TABLES
MATCH COLUMNS has_tag_value('personal_data', 'direct') AS c
ON COLUMN c;

-- Block C, admin: ownership to a group
ALTER TABLE prod_crm.gold.dim_customer OWNER TO `crm_data_owners`;
```
ABAC limits to respect in proposals: policies work only with governed tags; conflicting policies on one column make
queries fail; materialized view and streaming table owners must be in `EXCEPT`; AI Search indexes do not inherit
policies; quotas per catalog, schema and table are in `uc-governance-features.md`.
