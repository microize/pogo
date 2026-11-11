# Governance assessment: <scope>

Status: DRAFT | REVIEWED (by <email>, <YYYY-MM-DD>) | Version: 1 | Assessed by: <email> | Date: <YYYY-MM-DD HH:MM> (from `current_timestamp()`)
Scope: catalogs <list>, schemas <list> | Regulations: <gdpr, ...> | Target maturity: <3 overall, 4 sensitive>
Visibility: <n> tables and views visible to <email>; checks skipped for missing access: <ids or none>
Taxonomy: `specs/governance/taxonomy.md` v<n> | Previous assessment: v<n-1>, <date> | Decisions: `decisions.md`

## 1. Summary

| Measure | Now | Previous | Target |
|---|---|---|---|
| Overall completeness (usage-weighted) | <n> (<band>) | | |
| Sensitive assets completeness | <n> (<band>) | | |
| Sensitive columns unprotected | <n> | | 0 |
| Tables without a group owner | <n> | | 0 |
| Column comment coverage | <n>% | | 90% |
| Assets certified / meeting the rubric | <n> / <n> | | |

Top three risks in one line each. Not measured: <checks and why>.

## 2. Maturity per CDMC component (0 to 5)

| Component | Level | Evidence (checks, pass %) | Next level needs |
|---|---|---|---|
| Governance and accountability | | | |
| Cataloguing and classification | | | |
| Access and usage | | | |
| Protection and privacy | | | |
| Data lifecycle | | | |
| Architecture and cost | | | |

## 3. Top findings (at most 15, risk first, then usage)

| # | Severity | Check | CDMC | Object | Finding (numbers) | Reads 30 d | Confidence | Proposal | Approver |
|---|---|---|---|---|---|---|---|---|---|
| F1 | Blocker | G09 | C9 | | | | measured | | |

## 4. Scores per table

| Table | Owner | Score | Band | Failed checks | Reads 30 d | Sensitive cols (protected / total) |
|---|---|---|---|---|---|---|

## 5. Classification and protection

| Table | Column | Detected class | Proposed `sensitivity` | Proposed `personal_data` | Protected by | Evidence |
|---|---|---|---|---|---|---|

Policy hygiene (G10): policies matching nothing, table-only sensitivity tags, tags that policies depend on.

## 6. Certification and deprecation

| Asset | Proposal (certify / deprecate / keep) | Rubric items met | Missing | Readers 30 d |
|---|---|---|---|---|

## 7. Ownership and stewardship

| Scope (domain / schema / table) | UC owner now | Proposed owner group | Proposed steward (recognized from) | Proposed business owner |
|---|---|---|---|---|

## 8. Prerequisites for an admin (user-run)

| Need | Why | Exact step (not run by the agent) |
|---|---|---|

## 9. Apply plan

`apply_<n>.sql`: block A (asset owners: tags, comments), block B (admin: ABAC policies, masks), block C (admin:
ownership, grants), block D (UI steps: classification enablement, access-request destinations, domains). Run in
order, then ask for a `recheck`.

## Appendix: all findings

| Severity | Check | Object | Finding | Proposal |
|---|---|---|---|---|

## Changelog

| Version | Date | By | Change |
|---|---|---|---|
| 1 | | | initial assessment |
