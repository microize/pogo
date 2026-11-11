# 7. Troubleshooting and FAQ

These all happened during our tests. Most are environment or display issues, not mistakes in your work.

## The agent

| What you see | Why | What to do |
|---|---|---|
| No "Read de-... skill" step; it answers generically | skills not installed for you, or the chat started before they were | type `@de-` in a new chat; if nothing shows, ask the admin to publish (setup A) |
| It refuses to write code | the spec is not approved yet (by design) | reply `approved` to the spec summary, or ask for a chat-only example |
| It writes files in your home folder instead of the project | it did not know the project root | open a file inside the project before chatting, and mention the project path |
| "I stopped because I kept repeating the same action" | Genie Code's loop guard, usually while waiting for a run | reply `continue`, and if it was waiting, tell it to stop polling and wait for your `check` |
| A step shows "running" for minutes, but should be quick | the panel display hung; the query may already be done | look in Query History; if it finished, tell the agent "the query finished, continue" (stopping the display is not cancelling the query) |
| "Failed to edit", a save conflict, or an edit that hangs | two saves overlapped, or the display hung | stop it and ask the agent to re-read the file; do not re-send the request (the edit was usually saved) |
| Files it wrote are gone later | pending assets were never accepted | click **Accept all** on pending files after each step |
| It asks Allow / Skip for every query | Genie Code's safety default | read and allow; or, if your team agreed, use Auto-approve in that chat's drop-down |
| The Allow / Skip prompt does not show the SQL text | display limit of the prompt | check **Query History** for the statement, or ask the agent to print the SQL in chat first |
| Typing `@` opens a picker and eats `@dp.table` | `@` opens the mention picker | press **Escape**, then keep typing the decorator |
| A pipeline or job failed, errored or is slow | a general answer skips the diagnosis method | start the question with `@de-run-diagnose` and paste the error text |
| It answers with old names (DLT, APPLY CHANGES) | an old snippet in the request | the project's AGENTS.md maps old to new; ask "use current names" |

## Compute, quota and permissions

| Error text contains | Meaning | What to do |
|---|---|---|
| "No compute is available" / `INVALID_ENVIRONMENT` | nothing attached | attach your team's SQL warehouse in the editor |
| "Limited capabilities ... SQL warehouse" | no serverless Python here | fine for SQL work; Python steps need a cluster or serverless (admin) |
| `WAITING_FOR_RESOURCES` for a long time | the cluster cannot get machines | ask the agent to read cluster events; often the quota below |
| `AZURE_QUOTA_EXCEEDED` / `QuotaExceeded` | regional vCPU quota full (shared) | stop only your own idle clusters, or ask the platform team; never stop another team's cluster |
| `CLOUD_PROVIDER_RESOURCE_STOCKOUT` | Azure has no machines of that type right now | try later or another node type (policy permitting) |
| `INSUFFICIENT_PERMISSIONS ... system.access` | no access to system tables | admin item; impact reports fall back to code reading |
| "Metastore storage root URL does not exist" | catalogs cannot be created with SQL here | an admin creates the catalog in Catalog Explorer |
| `NO_SUCH_CATALOG` | catalog missing or not visible | check the name; ask for USE CATALOG |
| `install_skills` fails writing `/Workspace/.assistant` | `scope` = `workspace` needs a workspace admin | ask your admin to run it, or use `scope` = `personal` to try it yourself |
| No **Deployments** (rocket) icon on `databricks.yml` | bundles in the workspace are Public Preview, or the file is not in a Git folder | ask the admin to enable the preview; open the project from its Git folder |
| "... was read as a stream ... not a streaming table" | a view with checks read by a streaming step | the agent fixes it (streaming view); it is in the conventions |

## FAQ

**Can the agent deploy to production?** No. It prepares and checks; after the prod gate says GO a person deploys from
the **Deployments** panel in the prod workspace.

**Can it drop a table or change permissions?** No. It proposes a safe alternative, or writes the statement for a human.

**I closed the chat. Is the work lost?** No. Specs, tasks and ledgers are files. Open a new chat and type
`status of <track_id>`, then `next`.

**Two of us want the same task.** The first claim wins. The agent skips tasks owned by someone else and picks the next
one whose dependencies are done.

**The spec is wrong halfway through.** Say so. The agent writes an amendment; you approve it. Big changes (keys, grain,
history type, schedule) also get a fresh-eyes review.

**Where do I see what it cost?** Ask `how much did this cost`; with system tables it reads actual usage, otherwise it
estimates from the price file and says so.

**How do I suggest an improvement to a skill?** Tell the repo maintainers.
