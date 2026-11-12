# 2. One-time setup

Everything happens in the Databricks workspace, in your browser. Nobody installs anything on a laptop.

There are three levels. Ask your lead which ones are already done. As an engineer, you usually only do level C:
**skip A and B unless you are the admin or the lead.** New words are explained on [page 0](00-basics.md).

| Level | Who | How often | ShopCo example |
|---|---|---|---|
| A. Workspace | workspace admin | once per workspace | the ShopCo admin installs the kit for everyone |
| B. Project | tech lead | once per project | the lead creates the `shopco-orders` project folder |
| C. You | each person | once | each engineer opens the project and attaches a SQL warehouse |

## A. Workspace (admin)

1. Add the kit to the workspace as a **Git folder**: Workspace > Create > Git folder, then paste the kit's repository
   URL.
2. In that Git folder, open the notebook `install/install_skills`. Set the widget `scope` to `workspace`. Click
   **Run all**. The notebook:
   - copies the 16 `de-*` skills and the 16 official `databricks-*` skills into `/Workspace/.assistant/skills/`,
     so every user sees them (no internet access needed),
   - writes `/Workspace/.assistant_workspace_instructions.md` (short rules that apply in every chat),
   - writes a `_VERSION` file next to the skills,
   - checks every installed file and prints `32 ok, 0 failed` (16 + 16).
3. Open any notebook, open Genie Code, start a **new** chat and type `@de-`. You should see the `de-*` skills.

**To update later:** in the kit's Git folder click **Pull**, then run `install/install_skills` again.

**Want to try it alone first?** Anyone can run the same notebook with `scope` = `personal`. It installs only for you
(`/Users/<you>/.assistant/skills/`).

## B. Project (tech lead)

1. Create a **Git folder** for the project (Workspace > Create > Git folder). A plain folder also works, but a Git
   folder gives you history and pull requests.
   *ShopCo:* `/Users/lead@example.com/shopco-orders`.
2. Copy three things from the kit's Git folder into the project's root: `AGENTS.md`, the `instructions/` folder and
   an empty `specs/` folder. Save them with the Git dialog: **Commit & Push**.
3. Fill in the last section of `AGENTS.md`, "Project conventions":
   *ShopCo:* dev catalog `dev_shop`, schemas `bronze_sales`, `silver_sales`, `gold_sales`, pipeline language SQL,
   topology `git-folder` (how teammates share files: here, through the Git folder).
4. Open a notebook in the project (attached to the team's SQL warehouse), start a Genie Code chat and type:
   ```
   check this workspace's readiness for data engineering
   ```
   The agent writes `specs/env/<env>-<team>.md`: what you can run here, and a checklist for the admin (for example
   "enable serverless" or "grant access to the system tables"). Do this once per environment (dev, prod) and team,
   from inside that environment's workspace.
5. Give the admin checklist to your admin.
6. Optional: in `specs/project-profile.md`, set the **productivity target** (for example "80% time saved against
   manual estimates") so the productivity report can compare against it.

## C. You (each person)

1. Ask your lead for the **project folder path** and your **team's SQL warehouse name**. Open the folder from the left
   sidebar > **Workspace**. Check that Genie Code is on: the sparkle icon on the right of a notebook or file.
2. In the project folder, open a notebook (or create an empty one called `chat`). In the **compute selector** (the
   drop-down at the top right), choose your team's **SQL warehouse** (compute that runs SQL). Start your Genie Code
   chats from this notebook; the agent runs its checks on that warehouse. Do not use another team's compute.
3. Learn three habits, explained on [page 0](00-basics.md#6-where-to-click):
   - click **Accept all** after the agent writes files, or the changes are lost;
   - **Allow** only reading queries; **Skip and ask** when unsure (safety rules on page 0);
   - run each Validate query in the SQL editor before replying `ok`.
4. Read [page 3](03-first-task.md) once.

Some steps are buttons that only you can press: **Pull**, **Commit & Push**, and **Deploy** to dev. The agent tells you
when; [page 3, step 7](03-first-task.md#step-7-press-the-buttons-only-you-can-press) shows where to click. Ask your
lead whether you may deploy to dev yourself.

**No serverless?** (Your environment file in `specs/env/` says so. If you are not sure, skip this.) Deploying from the Git folder's **Deployments** panel needs serverless compute. Without it, the agent
creates the dev jobs through the Jobs API, after you approve each call, and writes that choice into the spec.

## How to know setup is complete

| Check | Where | You should see |
|---|---|---|
| Skills visible | new Genie Code chat, type `@de-` | 16 `de-*` skills |
| Install verified | last cell of `install/install_skills` | `32 ok, 0 failed` |
| Project rules read | ask "what are the rules of this project?" in a chat opened from a project file | it quotes `AGENTS.md` |
| Environment known | `specs/env/` in the project | a file for your environment and team, with nothing blocking your goal |
| Git works | Git dialog of the project folder (click the branch name at the top of a file) | the branch name your lead gave you; **Pull** succeeds |
