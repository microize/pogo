# de-env-check: checks, evidence and consequences

Run in this order. Use SQL on a running warehouse and the read calls available in Genie Code (compute listing,
cluster and pipeline reads; `WorkspaceClient()` in a Python cell only if Python compute exists).

## 1. Identity and rights

| Check | How | Record |
|---|---|---|
| Who am I | `SELECT current_user()` | email |
| Admin | `SELECT is_account_group_member('admins')` (say which group check was used) | yes / no / unknown |
| Metastore privileges | `SHOW GRANTS ON METASTORE` (rows for my groups) | CREATE CATALOG, CREATE EXTERNAL LOCATION, ... |

## 2. Compute

| Check | How | Record |
|---|---|---|
| SQL warehouses | warehouse list: name, state, size, serverless, auto-stop | which one to use for checks and SQL tasks |
| Clusters | cluster list: name, state, node type, workers, `data_security_mode`, auto-termination | **access mode NONE ("No isolation shared") cannot read Unity Catalog**; SINGLE_USER / USER_ISOLATION can |
| Serverless notebooks / jobs | available compute list in Genie Code; a "Limited capabilities" banner on a SQL warehouse means no serverless Python | yes / no |
| Serverless pipelines | not visible from a validate; if unknown, ask the admin and record "unknown" | yes / no / unknown |
| Quota signal | events of recent clusters for `AZURE_QUOTA_EXCEEDED_EXCEPTION`, `QuotaExceeded`, long `WAITING_FOR_RESOURCES`; sum the cores of running clusters | cores in use; regional limit if known |

## 3. Unity Catalog

| Check | How | Record |
|---|---|---|
| Catalogs | `SHOW CATALOGS`; `SELECT current_catalog()` | list; default catalog (queries must name the catalog when the default is not the project's) |
| Metastore storage root | metastore summary `storage_root`, or the error "Metastore storage root URL does not exist" | if absent, SQL `CREATE CATALOG` fails: a human creates catalogs in Catalog Explorer with a location |
| External locations | external location list | which one new catalogs can use |
| Landing volumes | `SHOW VOLUMES IN <catalog>.<schema>` for the named source | exists / missing |
| Create rights | `SHOW GRANTS ON CATALOG <dev catalog>` | USE CATALOG, CREATE SCHEMA |

## 4. System tables

| Check | How | Needed by |
|---|---|---|
| Lineage | `SELECT 1 FROM system.access.table_lineage LIMIT 1` | `de-data-contract` blast radius |
| Billing | `SELECT 1 FROM system.billing.usage LIMIT 1` | cost reporting |
| Query history | `SELECT 1 FROM system.query.history LIMIT 1` | diagnosis |

`INSUFFICIENT_PERMISSIONS ... USE SCHEMA on Schema 'system.access'` means an account admin must enable the schema
and grant `USE SCHEMA` and `SELECT`.

## 5. Tooling

| Check | Record |
|---|---|
| Project folder type | Git folder or plain folder (decides claim sync in `de-sdd-tracking`; bundles and the Deployments panel need a Git folder) |
| Bundle Deployments panel | open `databricks.yml` in the Git folder: the deployments (rocket) icon is shown (Public Preview; deploys only to targets in this workspace) |
| Skills installed | list `/Workspace/.assistant/skills` and `/Users/<me>/.assistant/skills`: `de-*` and official `databricks-*` |
| Genie Code approval mode | per-step Allow or per-chat Auto-approve (a human setting; never change it) |

## 6. Team scope (many teams in one workspace)

| Check | How | Record |
|---|---|---|
| Team's compute | warehouses and clusters whose owner, tags (`team`, `cost_center`) or permissions (`CAN_USE`, `CAN_ATTACH_TO`, `CAN_RESTART`) include this team | the only compute the agent may use |
| Cluster policies | policy list and which the team may use | node types and sizes allowed; design within them |
| Other teams' compute | running clusters not owned by the team (names only) | counts against shared quota; never use, start or stop |
| Quota share | cores in use by all running clusters vs the regional limit (if known) | team's agreed share, or "ask the platform team" |
| Catalog ownership | `SHOW CATALOGS`, owners | which catalogs belong to the team; read only those (guardrails) |

## 7. Other environments (dev / staging / prod in other workspaces)

Genie Code sees only its own workspace. For each other environment the project uses, someone with access opens
Genie Code in that workspace (same project Git folder) and runs `de-env-check` there; the result is written to
`specs/env/<env>-<team>.md` and the environment index row. Until then the environment is "unknown", never a copy of
another environment's findings.
- Compare each bundle target's `workspace.host` with the environment index; a target without a checked environment
  is a release-gate finding.

## Error signatures (route here from any skill)

| Error text contains | Meaning | Admin item |
|---|---|---|
| `INVALID_ENVIRONMENT` / "No compute is available" | no compute attached or none exists | start or grant a SQL warehouse; enable serverless |
| `AZURE_QUOTA_EXCEEDED_EXCEPTION` / `QuotaExceeded` | regional vCPU quota | raise the quota, or stop other clusters during runs |
| update stuck in `WAITING_FOR_RESOURCES` | cluster cannot get nodes | read cluster events first |
| "Metastore storage root URL does not exist" | no default storage for SQL `CREATE CATALOG` | create the catalog in the UI with a location |
| `INSUFFICIENT_PERMISSIONS` on `system.*` | system schema not enabled or granted | enable and grant |
| `NO_SUCH_CATALOG_EXCEPTION` | catalog missing or not visible | create, or grant USE CATALOG |
| 401 / expired token on a Git folder pull or push | Git credential expired | user updates the Git credential in Settings > Linked accounts |

## Consequences table

| Finding | Design consequence |
|---|---|
| no serverless pipelines | classic pipeline compute, smallest shape, Photon off in dev, shutdown delay about 5 min; MVs fully recompute; about 10 min start per update, so pre-check SQL on the warehouse and batch verifications |
| no Python compute | verification in SQL only; no polling loops; "say check in N minutes" |
| low vCPU quota | one classic workload at a time; record "stop cluster X during runs" |
| no-isolation cluster only | that cluster cannot read UC tables; do not use it for project data |
| no metastore storage root | catalogs are created by a human in the UI |
| no system.access | impact analysis falls back to the lineage API and code reading; say so in every impact report |
| no CLI in Genie Code | bundle deploys are user-run from the Deployments panel and batched; runs and checks use the Pipelines Editor, SDK and SQL; dev pipeline reads SQL from the project folder |
| no Deployments panel (no Git folder) | create the project as a Git folder; until then pipelines are created and run in the Pipelines Editor only |
