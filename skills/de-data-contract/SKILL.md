---
name: de-data-contract
description: Data contracts and change impact for Databricks tables. Use when the user asks to define or version a data contract (schema, keys, nullability, CDC strategy, SLA, owners, consumers) for a table, or to assess the impact of a schema or logic change (breaking or not, blast radius via Unity Catalog lineage, migration and rollback plan). Writes specs/contracts/<catalog>.<schema>.<table>.yaml and specs/<track_id>/impact_<n>.md. Does not change tables.
metadata:
  version: "0.5.0"
---

# de-data-contract: define the contract, assess the change

Two modes. Say which one applies in your first line. **Precondition**: an approved spec names the table, or the user
asks for a contract or impact report explicitly; proposals become tasks, this skill does not alter tables.

## Mode A: define a contract

Output: `specs/contracts/<catalog>.<schema>.<table>.yaml` from `templates/contract.yaml`.

1. **Baseline from the live table** when it exists: `DESCRIBE TABLE EXTENDED <t>`, `SHOW TBLPROPERTIES <t>`,
   constraints from `system.information_schema.table_constraints` and `key_column_usage`, tags from
   `system.information_schema.column_tags`. Never guess a schema you can read.
2. **Fill**: owner team and contact, domain, schema (type, nullable, description, `pii`, `sensitivity`),
   primary / natural / foreign keys, nullability rules with downstream impact, CDC strategy
   (`LOG_BASED` / `TIMESTAMP_BASED` / `FULL_SNAPSHOT`, change indicator, delete handling, idempotency),
   compatibility mode, SLA (freshness, availability), consumers.
3. **Version**: semver. Major for any breaking change in `references/breaking-change-catalog.md`,
   minor for additive, patch for docs. First contract is `1.0.0` with a note that no compatibility check ran.
4. **Enforcement on Databricks** (propose as tasks, do not run):
   - `NOT NULL` and `CHECK` constraints are enforced; Unity Catalog `PRIMARY KEY` / `FOREIGN KEY` are **informational** (not enforced), so uniqueness still needs an expectation or a DQ check (see `de-quality-testing`).
   - PII: column tags (`ALTER TABLE t ALTER COLUMN c SET TAGS ('pii' = 'true')`), column masks and row filters.
   - Documentation: `COMMENT ON TABLE / COLUMN` with grain, owner, contract version.
5. Add the contract path to the spec's Targets table and to `specs/project-profile.md`.

## Mode B: change impact

Output: `specs/<track_id>/impact_<n>.md` from `templates/impact-report.md`.

1. **Classify** the change with `references/breaking-change-catalog.md` (schema / logic / configuration / deprecation; breaking or not; version bump).
2. **Map dependencies** from Unity Catalog lineage, not from memory:
   ```sql
   SELECT DISTINCT target_table_full_name, target_type, MAX(event_time) AS last_seen
   FROM system.access.table_lineage
   WHERE source_table_full_name = '<catalog.schema.table>'
     AND event_date >= current_date() - INTERVAL 90 DAYS
   GROUP BY target_table_full_name, target_type
   ORDER BY last_seen DESC;
   -- column level: system.access.column_lineage (filter source_column_name)
   ```
   Query shape and the documented columns: official `databricks-unity-catalog/references/5-system-tables.md`. The live
   table also carries `entity_type` / `entity_id` (notebook, job, dashboard, pipeline) which the official reference
   does not list; use them to find non-table consumers, plus Delta Shares and external consumers named in the contract.
   **When `system.access` is not available** (`INSUFFICIENT_PERMISSIONS`): (a) the lineage REST API for the table
   and its columns, (b) read every pipeline, notebook, job and query file in the project for the table and column
   names, (c) list dashboards, Genie Agents and shares that name the table. State in the report which sources were
   used and that consumers outside the project may be missed; add the grant to `specs/env/<env>-<team>.md`.
3. **Blast radius**: one row per consumer: type, owner, what breaks, severity (Blocker / Major / Minor), action.
4. **Compatibility**: backward, forward, backfill needed, consumer code change needed.
5. **Migration plan** with rollback per step. Prefer additive paths: add new column, dual-write, migrate consumers, then drop; use Delta column mapping for renames only when consumers are updated in the same release; type widening is supported on Delta (2026) so prefer widening to re-creating.
6. **Communication**: who to notify, when, and the contract version they must adopt.
7. Hand the Blockers to `de-sdd-spec` as spec changes and to `de-release-gate` as release conditions.

## Rules

- Read-only on data. Proposals become tasks in `tasks.md`; you do not run `ALTER TABLE`.
- **Owner team is required.** Ask for it (team name and contact channel) before writing; take it from
  `specs/project-profile.md` ("Owner team") when present. Unknown consumers are written as `TBD` and flagged; the
  contract cannot be `active` without an owner team.
- Keep contracts next to specs so a goldfish review can read them.

## Changelog
- 0.5.0: metric-view changes in the breaking-change catalog (rename, expression or filter change, synonyms).
- 0.4.0: QA and gap-analysis fixes: contract path in the description matches the template, "Genie Agent" in the
  impact report, forward-only change row in the breaking-change catalog.
- 0.3.0: documented lineage fallback when system.access is missing; owner team required.
- 0.2.0: precondition; lineage query aligned with the official reference.
- 0.1.0: initial.
