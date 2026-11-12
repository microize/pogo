# User guide: Genie Code and the `de-*` skills

Start here. This guide is for everyone who works with data on Databricks: data engineers, analytics engineers, data
architects, data modelers, data stewards, tech leads, admins and business owners. You do not need to read any skill
file to use it.

> **New to data engineering?** (for example, you have only had a short Databricks class) Follow this path:
> 1. [Page 0: Basics](00-basics.md): the words and screens used everywhere, and two safety rules.
> 2. [Page 1](01-what-is-this.md): what the kit is.
> 3. [Page 2](02-setup.md), part C only.
> 4. [Page 3](03-first-task.md), the steps marked **Data engineer**. Skip the others for now.
> 5. Ask your lead for a **small** first task (one table or one rule), not a whole project.

## What this is, in one minute

**Genie Code** is the AI assistant inside the Databricks workspace. On its own, it writes code when you ask.

This kit gives it a **way of working**. When you ask for something new, it:

1. **asks you questions first**, each with a suggested answer,
2. **writes a short plan** (we call it a *spec*) and waits until you say `approved`,
3. **builds one small step at a time**, checks each step, and shows you how to check it too,
4. **explains** errors, logs and slow queries in plain words, and fixes them,
5. **keeps a record** of who did what, how long it took, and what went wrong,
6. **never** deletes tables, changes permissions or touches production. A person does those.

Words like *spec*, *pipeline* or *dev* are explained on [page 0](00-basics.md) and [page 1](01-what-is-this.md).

It also helps you **design** data (models, metrics, Genie Agents, ontologies), **govern** it (owners, sensitive data,
certification) and **choose** the right compute, runtime and cost.

## The example used in this guide

Every page uses the same example, so you can follow one story:

> **ShopCo** is a made-up online shop, invented for this guide (it is not a real company; all names and email
> addresses use the reserved `example.com` domain). It is small. Every day, order files (JSON) and a customer file (CSV) land in a Databricks
> volume (a folder for files). The sales managers want a daily revenue dashboard and a Genie Agent they can ask "What was revenue by
> country last week?". The customer file has email addresses and phone numbers, so it must be protected.

[Page 3](03-first-task.md) follows ShopCo from the first question to production.

## Read in this order

| # | Page | Read it when |
|---|---|---|
| 0 | [Basics: read this first if you are new](00-basics.md) | if your Databricks knowledge is a short class |
| 1 | [What it is and the words we use](01-what-is-this.md) | your first day |
| 2 | [One-time setup](02-setup.md) | before your first task (your admin or lead may have done it) |
| 3 | [The ShopCo example, start to finish](03-first-task.md) | before your first task; it shows every step |
| 4 | [Everyday use: what to type](04-everyday-use.md) | keep it open while you work |
| 5 | [Files and folders in a project](05-files-and-folders.md) | when you wonder what a file is for |
| 6 | [Cost, environments and teams](06-cost-and-environments.md) | before choosing compute or going to production |
| 7 | [Troubleshooting and FAQ](07-troubleshooting.md) | when something looks stuck or wrong |
| 8 | [Roles: where to start](08-roles.md) | to find your starting point if you are not a data engineer |
| 9 | [Skills by role and lifecycle stage](09-skills-by-role-and-lifecycle.md) | to see which skill helps you at each stage |
| 10 | [Skills in action](10-skills-in-action.md) | to see a real screenshot of each skill and how it was tested |

## Five rules to remember

1. **Say what you need in plain words.** You do not need skill names. Genie Code picks the right skill. If you see
   no "Read de-... skill" step, start again with `@` and the skill name ([page 10](10-skills-in-action.md)).
2. **Nothing is built until you reply `approved`.** Read the spec summary first. "ok" or "looks fine" does not count.
3. **Check each step.** After each task you get a short "Validate" note with a query and the expected result. Run the
   query in the SQL editor ([how](00-basics.md#7-two-safety-rules)); if the result matches, reply `ok`.
4. **Dev only.** The agent works only in **dev**, the safe place for building. **Prod** (production) is what the
   business really uses; a person puts work there, and only after the release check says GO (go ahead).
5. **One new chat per piece of work.** Skills load when a chat starts. The project files, not the chat, hold the
   memory, so nothing is lost when you close a chat.

## Who to ask

- A skill behaves wrongly, or you have an idea to improve one: the maintainers of this kit.
- Access, compute, quota or "not allowed" errors: your workspace admin. Show them the checklist in
  `specs/env/<env>-<team>.md` of your project (for example `specs/env/dev-sales.md`).
