# 2. One-time setup

Everything below happens in the Databricks workspace, in the browser. Nobody needs a laptop install or a command line.
There are three levels. Check with your lead which are already done; as an engineer you usually only do level C.

## A. Workspace (admin, once per workspace)

Done by a workspace admin.

1. Add this kit to the workspace as a **Git folder**: Workspace > Create > Git folder, paste the kit's repository URL.
2. In that Git folder open the notebook `install/install_skills`. Set the widget `scope` to `workspace` and click
   **Run all**. It:
   - copies `skills/de-*` and the 16 official `databricks-*` skills in `install/official/` to
     `/Workspace/.assistant/skills/` (visible to every user; no internet access needed),
   - writes `/Workspace/.assistant_workspace_instructions.md` from `instructions/genie-code-user-instructions.md`,
   - writes a `_VERSION` stamp next to the skills,
   - checks each installed skill against the Git folder and prints `30 ok, 0 failed` (14 + 16).
3. Open any notebook, open Genie Code, start a **new** chat and type `@de-`. You should see the `de-*` skills in the list.

To update later: pull the kit's Git folder (Git dialog > **Pull**) and run `install/install_skills` again.

Only want to try it yourself first? Any user can run the same notebook with `scope` = `personal`. It installs to
`/Users/<you>/.assistant/skills/` and skips the workspace instructions file.

## B. Project (lead, once per project)

1. Create a **Git folder** in the workspace for the project (Workspace > Create > Git folder). A plain folder works too,
   but a Git folder gives history and pull requests.
2. Copy into its root, from the kit's Git folder: `AGENTS.md`, the `instructions/` folder, and an empty `specs/`
   folder (right-click > Copy, or Import). Commit them with the Git dialog (**Commit & Push**).
3. Fill in the last section of `AGENTS.md` ("Project conventions"): catalogs, schema naming, pipeline language (SQL or
   Python), the shared-file topology (`git-folder`, `plain-folder` or `org-events`).
4. Open any file in the project, start a Genie Code chat and type:
   `check this workspace's readiness for data engineering`
   This runs `de-env-check`. It writes `specs/env/<env>-<team>.md` with what you can run here and a checklist for the
   admin (for example "enable serverless", "grant system tables"). Do it once per environment (dev, prod) and team,
   each time from Genie Code in that environment's workspace.
5. Give the admin checklist to your admin.

## C. You (engineer, once)

1. Make sure you can open the project Git folder and that Genie Code is on (the sparkle icon at the right of the editor).
2. Pick compute for checks: in the editor's compute selector attach your team's **SQL warehouse**. The agent runs its SQL
   checks there. Do not use another team's cluster.
3. Read [Everyday use](04-everyday-use.md) once.

That is all. The steps you do yourself (pull, commit and push, deploy a bundle to dev) are buttons in the workspace.
Deploying from the Git folder's **Deployments** panel needs serverless compute; without it, the agent creates the dev
jobs through the Jobs API (Python SDK) after you approve each call, and the spec records that choice.

## How to know setup is complete

| Check | Where | Expected |
|---|---|---|
| Skills visible | new Genie Code chat, type `@de-` | 14 `de-*` skills listed |
| Install verified | last cell of `install/install_skills` | `30 ok, 0 failed` |
| Project rules read | ask "what are the rules of this project?" in a chat opened from a project file | it quotes AGENTS.md |
| Environment known | `specs/env/` in the project | a file for your environment and team, no Blocking items for your goal |
| Git works | Git dialog of the project folder | your branch, **Pull** succeeds |
