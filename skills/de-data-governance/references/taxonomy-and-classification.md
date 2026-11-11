# Tag taxonomy and classification scheme

A starting taxonomy to **propose** as governed tags. The governance lead approves it, an account admin (or a user
with tag `CREATE` / `MANAGE`) creates the governed tags in the UI or API, and owners assign them. Adapt names to an
existing taxonomy rather than adding a second one.

## Rules for governed tags

- Keys: lowercase with underscores. Keys cannot contain `. , - = / :`; keys and values are at most 256 characters;
  at most 50 tags per object and 1,000 column tags per table.
- Prefer allowed-value lists. Use a free value only for names (`steward`, `business_owner`, `dpia_ref`).
- Set sensitivity and personal-data tags **on the column**. ABAC policies match tags set directly on columns; table
  and schema tags inherit down to tables, not to columns.
- System tags (`class.*` from Data Classification, `system.certification_status`) are read, not redefined. A
  `class.*` tag is a detection, not a decision: the review step turns it into `sensitivity` and `personal_data`.
- Deleting a governed tag leaves its values on objects as ungoverned tags, and a policy that references it breaks
  queries; never propose deleting a tag that a policy uses.

## Proposed governed tags

| Key | Level | Allowed values | Purpose | CDMC |
|---|---|---|---|---|
| `sensitivity` | column, table | `public`, `internal`, `confidential`, `restricted` | confidentiality level; drives ABAC and sharing | C6, C9 |
| `personal_data` | column | `none`, `direct`, `quasi`, `special_category`, `criminal` | personal data type (GDPR Art. 4, 9, 10; NIST sensitive PII) | C6, C10 |
| `regulation` | column, table | `gdpr`, `hipaa`, `pci_dss`, `glba`, `dpdpa`, `ccpa`, `sox`, `none` | which rule set applies (one value per object: use the strictest and list the others in `taxonomy.md`) | C6 |
| `domain` | catalog, schema, table | the project's domains (`customer`, `sales`, `finance`, ...) | placement, Discover, stewardship | C5 |
| `criticality` | table | `critical`, `high`, `standard`, `low` | importance; critical data elements get stricter quality and certification rules | C12 |
| `steward` | schema, table | free value: a group name | the recognized operational steward | C2 |
| `business_owner` | catalog, schema, table | free value: a group name or role | accountable business owner (UC has a single technical OWNER) | C2 |
| `authoritative` | table | `true`, `false` | system-of-record / provisioning point | C3 |
| `retention` | table | `p30d`, `p1y`, `p3y`, `p7y`, `p10y`, `legal_hold` | retention period (ISO 8601 style) | C11 |
| `dpia_ref` | table | free value: DPIA id | link to the impact assessment | C10 |
| `layer` | schema, table | `bronze`, `silver`, `gold`, `sandbox` | medallion layer | C5 |

`criticality` replaces vendor "tier" schemes (OpenMetadata Tier1 to Tier5); staleness (no owner, no reads in 90 days)
is computed by check G22, not stored as a tag.

## Sensitivity levels

| Level | Meaning | Typical content | Minimum controls |
|---|---|---|---|
| `public` | approved for anyone | published reference data | owner, comment |
| `internal` | anyone in the company with a need | operational metrics, product catalog | owner, comment, group grants |
| `confidential` | named groups only; harm if disclosed | customer contact data, contracts, salaries, quasi-identifiers | plus classification reviewed, mask or row filter for non-entitled groups, audit review |
| `restricted` | strictly limited; legal or regulatory harm | special categories, card data, national ids, health, credentials, MNPI | plus ABAC policy, no copies in dev without masking, lineage, retention, DPIA where personal |

## Mapping detections to proposals

| Detected (`class.*` or name evidence) | `personal_data` | `sensitivity` | `regulation` |
|---|---|---|---|
| email, phone, name, postal address, IP address, device id | `direct` | `confidential` | `gdpr` (if EU subjects) |
| national ids (SSN, passport, driver's licence, Aadhaar, NINO), biometric | `direct` | `restricted` | `gdpr` / local law |
| date of birth, postcode, gender, job title (combinable) | `quasi` | `confidential` | `gdpr` |
| health, genetic, ethnicity, religion, political opinion, union membership, sex life or orientation | `special_category` | `restricted` | `gdpr` Art. 9, `hipaa` if PHI |
| criminal convictions or offences | `criminal` | `restricted` | `gdpr` Art. 10 |
| card number (PAN), with name, expiry, service code | `direct` | `restricted` | `pci_dss` |
| CVV / CVC, full track, PIN | must not be stored after authorization | `restricted` | `pci_dss`: finding, not a tag |
| bank account, IBAN, income | `direct` / `quasi` | `restricted` / `confidential` | `glba` (US financial) |
| hashed or tokenized identifier | `quasi` (re-identifiable with the key) | `confidential` | as source |

HIPAA PHI: the 18 Safe Harbor identifiers combined with health data. A column is never declared `none` from its name
alone: name-only evidence is `inferred` and needs the owner's confirmation.

## Review workflow (propose, approve, apply)

1. Detection: Data Classification results and `class.*` tags (measured), name and type patterns (inferred).
2. Proposal: this skill writes the proposed `sensitivity` / `personal_data` / `regulation` per column with evidence.
3. Approval: the asset owner (or steward) replies `approved` per block, or edits the proposal.
4. Apply: the owner runs `apply_<n>.sql`. Where the platform supports it (Data Classification auto-tagging, Public
   Preview at the time of writing), the governance lead may switch to automatic tagging for reviewed classes.
5. Protect: the admin applies ABAC policies keyed on the governed tags.
6. Recheck: this skill's recheck mode confirms the change and appends to `history.md`.
