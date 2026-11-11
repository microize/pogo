# Change impact <n>: <change description>

| Field | Value |
|---|---|
| Track | `<track_id>` |
| Date / by | <YYYY-MM-DD> / <email> |
| Object | `<catalog.schema.table>` (column / pipeline) |
| Change type | schema \| logic \| configuration \| deprecation |
| Breaking | yes \| no (catalog row: <name>) |
| Contract version | <old> to <new> |
| Risk | Blocker \| Major \| Minor |

## 1. What changes and why

## 2. Dependency map (from system.access.table_lineage, last 90 days)

| Consumer | Type (table / dashboard / Genie Agent / job / notebook / share / external) | Owner | Uses | Last seen |
|---|---|---|---|---|

## 3. Blast radius

| Consumer | What breaks | Severity | Action required | Owner |
|---|---|---|---|---|

Totals: tables <n>, pipelines <n>, dashboards <n>, external <n>, teams to notify <list>.

## 4. Compatibility

| Check | Result |
|---|---|
| Backward compatible | yes / no, why |
| Forward compatible | yes / no, why |
| Backfill required | yes / no, scope |
| Consumer code change required | yes / no, which |
| AUTO CDC target needs full refresh | yes / no |

## 5. Migration plan

| Step | Action | Owner | Target date | Rollback |
|---|---|---|---|---|

## 6. Rollback strategy

## 7. Communication

| Who | What | When | Channel |
|---|---|---|---|

## 8. Decision

Approved by <email> on <date> | Rejected | Needs spec amendment (link)
