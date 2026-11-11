# 7. Troubleshooting and FAQ

Everything here happened during our tests. Most of it is an environment or display issue, not a mistake in your work.

## The agent

| What you see | Why | What to do |
|---|---|---|
| No "Read de-... skill" step; the answer is generic | the skills are not installed for you, or the chat started before they were | type `@de-` in a **new** chat; if nothing shows, ask the admin to install (setup A) |
| A different skill answered than you expected | your words matched another skill | start the request with the skill name, for example `@de-spark-runtime is this cluster too big?` |
| It refuses to write code | the spec is not approved yet (on purpose) | reply `approved` to the spec summary, or ask for an example in chat only |
| It writes files in your home folder instead of the project | it did not know the project folder | open a file inside the project before chatting, and mention the project path |
| "I stopped because I kept repeating the same action" | Genie Code's loop guard, usually while waiting for a run | reply `continue`; if it was waiting, tell it to stop checking and wait for your `check` |
| A step shows "running" for minutes, but should be quick | the panel stopped updating; the query may be done | look in **Query History**; if it finished, tell the agent "the query finished, continue" (stopping the display does not cancel the query) |
| "Failed to edit", a save conflict, or an edit that hangs | two saves overlapped, or the display stopped | stop it and ask the agent to re-read the file; do not send the request again (the edit was usually saved) |
| Files it wrote are gone later | pending files were never accepted | click **Accept all** on pending files after each step |
| It asks Allow / Skip for every query | Genie Code's safety default | read and allow; or, if your team agreed, use Auto-approve in that chat's drop-down |
| The Allow / Skip prompt does not show the SQL | the prompt has a display limit | check **Query History**, or ask the agent to print the SQL in the chat first |
| Typing `@` opens a picker and eats `@dp.table` | `@` opens the mention picker | press **Escape**, then keep typing |
| A pipeline or job failed or is slow, and the answer is general | the diagnosis skill was not loaded | start with `@de-run-diagnose` and paste the error text |
| It uses old names (DLT, APPLY CHANGES) | an old example in your request | `AGENTS.md` maps old names to new ones; ask "use current names" |
| A time in your progress file shows `n/a` | no query ran in that step, so there was no clock reading | expected; the agent never guesses a time |

## Compute, quota and permissions

| Error text contains | Meaning | What to do |
|---|---|---|
| "No compute is available" / `INVALID_ENVIRONMENT` | nothing is attached | attach your team's SQL warehouse in the editor |
| "Limited capabilities ... SQL warehouse" | no serverless Python here | fine for SQL work; Python steps need a cluster or serverless (admin) |
| `WAITING_FOR_RESOURCES` for a long time | the cluster cannot get machines | ask the agent to read the cluster events; often the quota below |
| `AZURE_QUOTA_EXCEEDED` / `QuotaExceeded` | the regional vCPU quota is full (shared) | stop only your own idle clusters, or ask the platform team; never stop another team's cluster |
| `CLOUD_PROVIDER_RESOURCE_STOCKOUT` | the cloud has no machines of that type right now | try later, or another machine type if the policy allows |
| `INSUFFICIENT_PERMISSIONS ... system.access` | no access to the system tables | admin item; impact reports fall back to reading code |
| governance or sizing report says "skipped: no access" | the classification, data quality, billing or audit tables are not granted to you | give the admin the exact step listed in the report |
| "Metastore storage root URL does not exist" | catalogs cannot be created with SQL here | an admin creates the catalog in Catalog Explorer |
| `NO_SUCH_CATALOG` | the catalog is missing or not visible to you | check the name; ask for USE CATALOG |
| `install_skills` fails writing `/Workspace/.assistant` | `scope` = `workspace` needs a workspace admin | ask your admin, or use `scope` = `personal` to try it yourself |
| No **Deployments** (rocket) icon on `databricks.yml` | bundles in the workspace are in Public Preview, or the file is not in a Git folder | ask the admin to turn on the preview; open the project from its Git folder |
| "... was read as a stream ... not a streaming table" | a normal view is read by a streaming step | the agent fixes it (makes it a streaming view) |
| `input_file_name()` is not supported | removed in runtime 17.3 LTS and later | use `_metadata.file_path`; ask `@de-spark-runtime` for a version review |
| a cast or division error that did not happen before | ANSI mode is on by default in Spark 4 and on serverless | fix the data, or use `try_cast` / `try_divide` where an empty result is correct |

## FAQ

**Can the agent deploy to production?** No. It prepares and checks. After the production check says GO, a person
deploys from the **Deployments** panel in the prod workspace.

**Can it delete a table or change permissions?** No. It suggests a safe alternative, or writes the statement for a
person to run.

**Can it apply tags, masks or resize a cluster?** No. Governance and sizing skills write proposals. The owner or admin
applies them.

**I closed the chat. Is the work lost?** No. Specs, tasks and records are files. Open a new chat, type
`status of <track_id>`, then `next`.

**Two of us want the same task.** The first person to claim it wins. The agent skips tasks owned by someone else and
picks the next one whose earlier tasks are done.

**The spec turns out to be wrong halfway.** Say so. The agent writes an amendment; you approve it. Big changes (keys,
grain, history type, schedule) also get a fresh-eyes review.

**What did it cost?** Ask `how much did this cost`. With access to the billing tables it reads real usage; otherwise it
estimates from the price file and says so.

**How much time did it save?** Ask `productivity report for me, last 30 days`. It compares measured time with the
manual estimates and shows rework next to it.

**How do I suggest an improvement?** Tell the kit's maintainers.
