# Adding or renaming a skill: checklist (for maintainers)

A new `de-*` skill touches more than its own folder. Skip a step and users will not find the skill, the install count
will be wrong, or Genie Code will route requests to the wrong place. Work through this list in order.

## 1. The skill itself

- [ ] Folder `skills/de-<name>/` with `SKILL.md`. Frontmatter: `name` (same as the folder), `description` (what it does,
      **when to use it** in the user's own words, and what it never does), `metadata.version: "0.1.0"`.
- [ ] Description under 1,024 characters. It is the only thing Genie Code reads to decide whether to load the skill.
- [ ] Only allowed file types in the folder: `.md .py .sql .yaml .yml .json .txt .png .svg` (the install notebook
      rejects others).
- [ ] "Not this skill" section naming the neighbouring skills, so the boundaries are clear.
- [ ] Follows the kit's rules: read-only unless it is a build skill, records struggles in `.challenges_*`, logs time
      (`de-sdd-tracking`, "Time and effort"), never runs GRANT, DROP or production actions.
- [ ] Facts that change over time (feature status, versions, prices) carry a "checked on" date and their source.
- [ ] Changelog entry.

## 2. Routing and counts

- [ ] `AGENTS.md`: a row in "Which skill to load", with the words users actually type.
- [ ] `instructions/genie-code-user-instructions.md`: one line saying when to load it (this text applies in every chat).
- [ ] Skill count, in all four places: `README.md` ("What is in this repo", "Core method vs supporting", install step),
      `install/install_skills.py` header comment, `docs/user-guide/02-setup.md` (twice), and the expected
      `<n> ok, 0 failed` line (de skills + 16 official).
- [ ] `README.md`: a row in the "Skills" table (Owns / Never does) and in "Who it is for" if it serves a role.

## 3. User guide

- [ ] `docs/user-guide/01-what-is-this.md`: a row in "The skills in plain words", with a ShopCo example.
- [ ] `docs/user-guide/04-everyday-use.md`: an example request in "What to type, by situation".
- [ ] `docs/user-guide/05-files-and-folders.md`: any new files or folders it writes.
- [ ] `docs/user-guide/08-roles.md`: the roles that use it.
- [ ] `docs/user-guide/09-skills-by-role-and-lifecycle.md`: its row in "Skills by stage", and the role cells.
- [ ] `docs/user-guide/03-first-task.md`: a step in the ShopCo story, if it is part of the common path.
- [ ] `docs/user-guide/07-troubleshooting.md`: known errors or "skipped: no access" cases.

## 4. Neighbouring skills

- [ ] Each neighbouring skill's "Not this skill" section points to the new skill; version bump and changelog there.
- [ ] `de-databricks-current`: new product names or statuses it relies on.

## 5. Tests

- [ ] `docs/maintainers/skill-trigger-tests.md`: a row in "When to use each skill", at least two "should load" and
      one "should not load" prompts, and every new look-alike pair.
- [ ] Run the new prompts and the look-alike pairs in a fresh Genie Code chat; record results in the log.
- [ ] Run `install/install_skills` with `dry_run` = `yes`, then for real; it must print the new count with 0 failed.

## Renaming or removing a skill

Search the whole repo for the old name (`AGENTS.md`, `README.md`, `instructions/`, `docs/`, every `SKILL.md`). The
install notebook deletes `de-*` folders in the workspace that no longer exist in the repo, so users lose the old skill
on the next install: say so in the release note.
