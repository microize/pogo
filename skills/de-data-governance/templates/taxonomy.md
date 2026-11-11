# Governance taxonomy and operating model: <organization or project>

Status: DRAFT | APPROVED (by <governance lead email>, <YYYY-MM-DD>) | Version: 1 | Owner: <governance lead>
Applies to: catalogs <list> | Regulations: <list> | Recheck cadence: <monthly> | Score history: `history.md`

## 1. Governed tags

Start from `de-data-governance/references/taxonomy-and-classification.md`; keep only what the organization will
maintain. One row per tag; created in the account by <admin>, assigned by asset owners.

| Key | Level | Allowed values | Meaning of each value | Who assigns | Used by policies |
|---|---|---|---|---|---|
| `sensitivity` | column, table | public, internal, confidential, restricted | | asset owner after steward review | yes |

## 2. Operating model

Principle: recognize the people who already define, produce and use the data; do not assign stewardship at random.

| Domain | Business owner (accountable) | Steward group (recognized from) | Technical owner (UC OWNER group) | Governance contact |
|---|---|---|---|---|

RACI: as in `de-data-governance/references/frameworks.md`, with changes recorded here.

## 3. Rules (each with an owner and a measure)

| # | Rule | Owner | Measured by (check id) | Target |
|---|---|---|---|---|
| R1 | Every table in scope is owned by a group | | G01 | 100% |
| R2 | Every column with personal data carries `personal_data` and `sensitivity` on the column | | G08 | 100% |
| R3 | No restricted column is readable unmasked outside its entitled group | | G09 | 0 exceptions without waiver |
| R4 | Gold tables and metric views are certified before Genie or BI use | | G17 | 100% |

## 4. Locations and residency (C4)

| Catalog | Storage location / region | Allowed regions | Evidence (who confirmed, date) |
|---|---|---|---|

## 5. Waivers

Deviations are recorded in `instructions/waivers.md` with expiry; list their ids here.

## Changelog

| Version | Date | By | Change |
|---|---|---|---|
