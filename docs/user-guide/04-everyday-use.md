# 4. Everyday use: what to type

Always open a file in the project first, then a **new chat** for each new piece of work. Write in plain words; include
the project folder path if the chat might not know it.

## Short replies the agent understands

| You type | Meaning |
|---|---|
| `defaults` | accept every recommended answer in the current question round |
| `enough` | stop asking, draft the spec |
| `approved` | approve the spec or an amendment (only this word counts, not "ok") |
| `goldfish` | ask for a fresh-eyes review before approving |
| `resolve review` | go through the review findings and propose fixes |
| `ok` | the task's Validate step looks right: tick it and continue |
| `auto` | tick tasks whose checks passed without waiting for me |
| `next` | continue with the next task |
| `check` | the run I was told to wait for should be done now: verify it |
| `stop` | pause here |
| `status` | where is this track, who did what, what is left |

## Common requests by situation

| Situation | Example |
|---|---|
| New pipeline or table | `build a pipeline that loads daily customer CSVs from <path> into silver with SCD2` |
| Small change to existing work | `add a region column to silver orders from the shipping region field (small change)` |
| Production bug | `hotfix: gold fact_orders double counts cancelled orders` |
| Continue work from yesterday | `status of track <track_id>` then `next` |
| Something failed | `the dev pipeline <name> failed today, find out why and what to change` |
| Data quality | `propose data quality rules and tests for <tables>` |
| Data model (modellers) | `design the dimensional model for order analytics: revenue by day, segment, country` |
| Choose a technology | `advise: Zerobus, Lakeflow Connect or Auto Loader for 2,000 events per second?` |
| Cost | `how much does the daily pipeline cost, and would serverless be cheaper or faster?` |
| Contract and impact | `write the data contract for <table> and tell me what breaks if we drop <column>` |
| Before merging | `review this track for merge` |
| Before production | `is <track_id> ready for production? go / no-go` |
| Hand work to a teammate | `hand over tasks T05 to T07 of <track_id> to alex@company.com` |
| Workspace problems | `check this workspace's readiness` or `recheck` |
| Price list is old | `refresh prices` |

## Working with teammates

- **Each person has their own ledgers** (`.internal_<email>/`, `.challenges_<email>/`). Write only in your own.
- **Tasks have owners.** The agent claims a task in `tasks.md` with your email before working on it, and skips tasks
  someone else holds.
- **Git folder**: in the folder's Git dialog, **Pull** before you start and **Commit & Push** after each ticked task (the
  agent suggests the commit message `feat(<track_id>): T03 ...`). A job runs whatever is in the Git folder, so keep
  it at a ticked, committed state. Plain folder: the agent re-reads the file before saving to avoid overwriting a teammate.
- **Going on leave?** Ask for a handover. The agent writes a note with everything the next person needs and moves your
  open tasks to them.

## Approvals inside Genie Code

Genie Code asks **Allow / Skip** before running SQL or API calls. Read the short code, then allow. Read-only queries
(`SELECT`, `SHOW`, `DESCRIBE`, `LIST`) are safe. Be careful with anything that writes, and refuse anything outside dev.
There is a per-chat **Auto-approve** toggle in the drop-down of a pending step; use it only if your team agreed to, and
never in a workspace with production data.

## Habits that save time

- One chat per track or question; long chats get slow and lose focus. The files carry the memory.
- Keep your team's SQL warehouse attached in the editor.
- When the agent asks a question, answer all of it in one reply.
- Read the spec summary before `approved`. Changing a spec later is possible but costs time.
- If the agent seems stuck on a step that already finished (see [Troubleshooting](07-troubleshooting.md)), tell it
  "the query finished, continue" instead of starting over.
