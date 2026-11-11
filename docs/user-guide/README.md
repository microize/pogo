# User guide: data engineering with Genie Code and the `de-*` skills

Start here. This guide is for engineers who are new to the setup, including junior engineers. It explains what the
setup is, how to start, and what to type day to day. You do not need to read the skill files to use it.

## In one paragraph

Genie Code is the AI assistant built into the Databricks workspace. On its own it writes code when you ask. This
package teaches it a **way of working**: it asks you questions first, writes a short plan called a **spec**, waits for
you to approve it, then builds the pipeline **one task at a time**, checking each step and telling you how to check it
too. It also keeps a record of who did what, warns you about cost, and refuses dangerous actions such as dropping
tables or deploying to production.

## Read in this order

| # | Page | Read it when |
|---|---|---|
| 1 | [What it is and the words we use](01-what-is-this.md) | first day |
| 2 | [One-time setup](02-setup.md) | before your first task (your lead or admin may have done it) |
| 3 | [Your first task, step by step](03-first-task.md) | first task; it walks through a real example |
| 4 | [Everyday use: what to type](04-everyday-use.md) | keep it open while you work |
| 5 | [Files and folders in a project](05-files-and-folders.md) | when you wonder what a file is for |
| 6 | [Cost, environments and teams](06-cost-and-environments.md) | before choosing compute or going to prod |
| 7 | [Troubleshooting and FAQ](07-troubleshooting.md) | when something looks stuck or wrong |

## The five rules to remember

1. **Say what you need in plain words.** You do not need to know skill names; Genie Code picks the right one.
2. **Nothing is built before you reply `approved` to the spec.** Read the spec summary before you approve it.
3. **Check each task** with the "Validate" step the agent gives you, then reply `ok`.
4. **Dev only.** The agent never deploys to production, never drops tables and never changes permissions. A human
   does those, after the release gate says GO.
5. **Start a new chat for each new piece of work.** Skills load at the start of a chat; the project files, not the chat,
   are the memory.

## Who to ask

- The method or a skill behaves wrongly: the maintainers of this repo.
- Access, compute, quota or "not allowed" errors: your workspace admin, with the checklist in
  `specs/env/<env>-<team>.md` of your project.
