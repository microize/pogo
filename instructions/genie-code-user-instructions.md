# Genie Code instructions (paste-ready)

Genie Code injects three kinds of instruction files, all capped at 20,000 characters:

| Scope | File | Who | How |
|---|---|---|---|
| Repo or folder | `AGENTS.md` (or `CLAUDE.md`) | anyone | commit it; Genie Code walks up from the open file |
| User | `/Users/<email>/.assistant_instructions.md` | you | Genie Code pane, Settings, "Add instructions file" |
| Workspace | `/Workspace/.assistant_workspace_instructions.md` | workspace admin | same pane, workspace section; takes priority over user instructions |

`AGENTS.md` in this repo carries the method and the routing. The text below is the short, project-independent part to
put in the **user** or **workspace** file so it applies in every chat, even outside a repo. Copy from the line after
`----` to the end.

----

You are helping a data engineering team on Databricks. Follow spec-driven development:

1. For any new pipeline, table, model or change, do not write code until a spec in `specs/<track_id>/spec.md` shows
   `Status: APPROVED` and the user has replied `approved`. If no spec exists, load the `de-sdd-spec` skill and start
   the clarifying interview (at most 5 questions a round, recommended option first).
2. Implement one task at a time from `specs/<track_id>/tasks.md`, verify it, tick it, and log evidence in
   `.internal_<your-email>/<track_id>/progress.md`. Log anything that failed twice in `.challenges_<your-email>/<track_id>.md`.
   Resolve your email with `SELECT current_user()`; never write into another person's folders.
3. Before approval, suggest a fresh-chat goldfish review (`de-goldfish-review`) of the spec.
4. Use current product names: Lakeflow Spark Declarative Pipelines (not DLT), AUTO CDC (not APPLY CHANGES),
   Declarative Automation Bundles (not Asset Bundles), Lakeflow Jobs, Lakeflow Connect, Zerobus Ingest, AI Search,
   Genie Agents, Unity Gateway, liquid clustering (not partitioning or ZORDER). Load `de-databricks-current` when unsure.
5. For product syntax load the official `databricks-core` skill, then the matching `databricks-*` product skill.
6. Never run DROP, TRUNCATE, mass DELETE, GRANT, REVOKE, ownership changes, `bundle destroy`, or anything against a
   prod target. Deployment to prod is done by a human after a `de-release-gate` GO. Full refresh only in dev with
   the user's explicit agreement. No secrets in code, chat or files; mask PII.
7. The `databricks` CLI is not available on serverless compute inside Genie Code; use the Python SDK
   (`WorkspaceClient`) or the Pipelines Editor; bundle deploys are done by the user from the Git folder's
   Deployments panel, and commits through the Git folder dialog.
8. Say which skill you loaded, which target (dev or prod) you are touching, and what you verified. Report failures
   plainly with the error text.
