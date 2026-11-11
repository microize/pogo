# Data Vault on Databricks (reference)

Use only when the method-selection table in `SKILL.md` step 3 points here: many volatile sources for the same
business entities, a strong audit or "load everything, decide later" requirement, or frequent source changes. The
vault is the integration layer (silver); consumers still read a star schema or metric views built on top of it.

## Building blocks

| Object | Holds | Key | Load pattern on Databricks |
|---|---|---|---|
| **Hub** | one row per business key of an entity (customer, product) | hash key = `sha2(coalesce(upper(trim(<business key>)), '<null-token>'), 256)`; composite keys joined with `concat_ws('||', ...)` after the same coalesce; also the business key itself | insert only new keys: streaming table with dedup on the hash key, or `MERGE ... WHEN NOT MATCHED THEN INSERT` |
| **Link** | one row per relationship between hubs (order-customer-product) | hash of the concatenated hub business keys, fixed order and delimiter | insert only, like hubs |
| **Satellite** | descriptive attributes of a hub or link, with history | parent hash key + `load_ts` | insert a new row only when `hashdiff` (hash of all attributes) changes; AUTO CDC SCD type 2 is an acceptable equivalent |
| **Reference table** | code lists shared across the vault | code | small table, replace on change |
| **PIT table** (point in time) | per hub key and snapshot date, the satellite row valid at that date | hub hash key + snapshot date | rebuilt or appended per snapshot; speeds up star-schema builds |
| **Bridge table** | pre-joined hub and link paths for common queries | path keys + snapshot date | materialized view |

## Rules

- Every row carries `load_ts` and `record_source`; hubs and links never update or delete rows.
- Hash keys: one function, one delimiter (e.g. `||`), keys trimmed and upper-cased first, NULL replaced by a fixed
  token, documented in the model. Changing the hashing later rebuilds the whole vault.
- One satellite per source and rate of change; do not merge sources into one satellite.
- Business rules (derivations, cleansing, deduplication across sources) go into a **business vault** layer, not the
  raw vault.
- Same-as links record that two hub keys are the same real-world thing (entity resolution output); never overwrite
  hub keys to merge them.
- Gold stays dimensional: dimensions from hubs plus satellites (via PIT), facts from links plus their satellites.
  Run the same grain and join-trap checks as any star schema.
- Cost: a vault has many more tables and joins than a star schema; state the extra compute in the spec (`de-cost`)
  and use PIT and bridge tables where the star-schema build is slow.

## Validation queries (pass/fail)

| Check | Query shape |
|---|---|
| Hub key unique | `count(*) = count(DISTINCT hub_hk)` |
| Link endpoints exist | no link row whose hub keys are missing from their hubs (anti join count = 0) |
| Satellite no duplicate versions | `count(*) = count(DISTINCT parent_hk, load_ts)` |
| Satellite only on change | no two consecutive rows per parent with the same `hashdiff` |
| Record source present | `count_if(record_source IS NULL) = 0` on every vault table |
