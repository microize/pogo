# Databricks notebook source
# MAGIC %md
# MAGIC # Install the skills for Genie Code
# MAGIC
# MAGIC Run this notebook **from a Git folder of this repo** in the Databricks workspace. It installs two sets from the repo,
# MAGIC so no internet access is needed:
# MAGIC - the 16 `de-*` skills of this kit (`skills/`)
# MAGIC - 16 official `databricks-*` skills, vendored unmodified at a pinned release (`install/official/`, see `SOURCE.md`)
# MAGIC
# MAGIC | Widget | Values | Effect |
# MAGIC |---|---|---|
# MAGIC | `scope` | `personal` | installs to `/Users/<you>/.assistant/skills` (any user) |
# MAGIC | | `workspace` | installs to `/Workspace/.assistant/skills` for everyone and writes `/Workspace/.assistant_workspace_instructions.md` (workspace admin only) |
# MAGIC | `include_official` | `yes` / `no` | also install the official `databricks-*` skills |
# MAGIC | `dry_run` | `no` / `yes` | `yes` prints what would change and writes nothing |
# MAGIC
# MAGIC Both scopes write a `_VERSION` stamp next to the skills and check that `AGENTS.md` and `instructions/*.md` stay
# MAGIC under Genie Code's 20,000 character cap (a `WARN` line names any file over it).
# MAGIC The last cell verifies every installed file against this repo and prints e.g. `32 ok, 0 failed` (16 + 16).
# MAGIC Start a **new** Genie Code chat afterwards.

# COMMAND ----------

dbutils.widgets.dropdown("scope", "personal", ["personal", "workspace"])
dbutils.widgets.dropdown("include_official", "yes", ["yes", "no"])
dbutils.widgets.dropdown("dry_run", "no", ["no", "yes"])
SCOPE = dbutils.widgets.get("scope")
OFFICIAL = dbutils.widgets.get("include_official") == "yes"
DRY = dbutils.widgets.get("dry_run") == "yes"

# COMMAND ----------

import datetime
import io
import os
import re

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat, ObjectType

w = WorkspaceClient()
me = w.current_user.me().user_name

nb_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
repo_root = "/Workspace" + nb_path.rsplit("/install/", 1)[0]          # filesystem view of the Git folder
de_root = f"{repo_root}/skills"
official_root = f"{repo_root}/install/official/skills"
if not os.path.isdir(de_root):
    raise RuntimeError(f"skills/ not found next to install/: {de_root}. Run this notebook from a Git folder of the repo.")


def skill_dirs(root, prefix=""):
    if not os.path.isdir(root):
        return []
    return sorted(d for d in os.listdir(root) if d.startswith(prefix) and os.path.isfile(f"{root}/{d}/SKILL.md"))


SETS = [("de", de_root, skill_dirs(de_root, "de-"))]
if OFFICIAL:
    SETS.append(("official", official_root, skill_dirs(official_root)))
de_names = set(SETS[0][2])

target_root = "/Workspace/.assistant/skills" if SCOPE == "workspace" else f"/Users/{me}/.assistant/skills"
print(f"user={me} scope={SCOPE} include_official={OFFICIAL} dry_run={DRY}\ntarget={target_root}")
for label, root, names in SETS:
    print(f"{label} ({len(names)}) from {root}: {', '.join(names)}")

# COMMAND ----------

# Safety check before anything is installed: only expected file types, no symbolic links, no hidden binaries.
# URLs to domains outside the list below are printed for a quick human look (not an error).
ALLOWED_EXT = {".md", ".py", ".sql", ".yaml", ".yml", ".json", ".txt", ".png", ".svg"}
BINARY_OK = {".png"}
KNOWN_DOMAINS = ("databricks.com", "databricks.net", "azuredatabricks.net", "readthedocs.io", "github.com",
                 "githubusercontent.com", "microsoft.com", "azure.com", "apache.org", "w3.org", "example.com")
problems, review = [], {}
for label, root, names in SETS:
    for skill in names:
        for dirpath, dirnames, files in os.walk(f"{root}/{skill}"):
            for n in dirnames + files:
                if os.path.islink(f"{dirpath}/{n}"):
                    problems.append(f"symbolic link: {dirpath}/{n}")
            for f in files:
                full = f"{dirpath}/{f}"
                ext = os.path.splitext(f)[1].lower()
                if ext not in ALLOWED_EXT:
                    problems.append(f"unexpected file type: {full}")
                    continue
                with open(full, "rb") as fh:
                    data = fh.read()
                if ext not in BINARY_OK and b"\x00" in data:
                    problems.append(f"binary content in a text file: {full}")
                if ext not in BINARY_OK:
                    for dom in set(re.findall(r"https?://([A-Za-z0-9.-]+)", data.decode("utf-8", "replace"))):
                        if not dom.endswith(KNOWN_DOMAINS):
                            review.setdefault(dom, full[len(repo_root) + 1:])
for dom, where in sorted(review.items()):
    print(f"review URL domain {dom}  (first seen in {where})")
if problems:
    raise RuntimeError("Safety check failed, nothing installed:\n" + "\n".join(problems))
print(f"safety check ok ({len(review)} URL domains to glance at)")

# COMMAND ----------

def upload(path: str, data: bytes):
    if DRY:
        print(f"DRY write {path} ({len(data)} bytes)")
        return
    w.workspace.mkdirs(path.rsplit("/", 1)[0])
    w.workspace.upload(path, io.BytesIO(data), format=ImportFormat.AUTO, overwrite=True)


def source_files(root: str, skill: str):
    for dirpath, _, files in os.walk(f"{root}/{skill}"):
        for f in sorted(files):
            full = f"{dirpath}/{f}"
            yield full, full[len(root) + 1:]          # (filesystem path, relative path like de-x/SKILL.md)


# Remove de-* folders in the target that no longer exist in the repo. Other skills are never deleted.
try:
    remote = [o.path.rsplit("/", 1)[-1] for o in w.workspace.list(target_root) if o.object_type == ObjectType.DIRECTORY]
except Exception:
    remote = []
for stale in sorted(r for r in remote if r.startswith("de-") and r not in de_names):
    print(f"{'DRY ' if DRY else ''}delete stale {target_root}/{stale}")
    if not DRY:
        w.workspace.delete(f"{target_root}/{stale}", recursive=True)

for label, root, names in SETS:
    for skill in names:
        if not DRY:
            try:
                w.workspace.delete(f"{target_root}/{skill}", recursive=True)   # clean copy of this skill only
            except Exception:
                pass
        for full, rel in source_files(root, skill):
            with open(full, "rb") as fh:
                upload(f"{target_root}/{rel}", fh.read())
        print(f"installed {label} {skill}")

# COMMAND ----------

# Genie Code ignores instruction text beyond 20,000 characters: check AGENTS.md and instructions/*.md.
CAP = 20000
inst_dir = f"{repo_root}/instructions"
for path in [f"{repo_root}/AGENTS.md"] + sorted(f"{inst_dir}/{f}" for f in os.listdir(inst_dir) if f.endswith(".md")):
    with open(path, encoding="utf-8") as fh:
        n = len(fh.read())
    print(f"{'ok  ' if n < CAP else 'WARN'} {n:>6} chars  {path[len(repo_root) + 1:]}{'' if n < CAP else '  (over the cap; shorten it)'}")

# Workspace scope only: workspace instructions file.
if SCOPE == "workspace":
    with open(f"{repo_root}/instructions/genie-code-user-instructions.md", encoding="utf-8") as fh:
        text = fh.read()
    body = text.split("\n----\n", 1)[1] if "\n----\n" in text else text      # paste-ready part after the ---- marker
    if len(body) >= CAP:
        raise RuntimeError("workspace instructions exceed Genie Code's 20,000 character cap")
    upload("/Workspace/.assistant_workspace_instructions.md", body.encode("utf-8"))

# Version stamp next to the installed skills (both scopes).
lines = [
    f"published_utc={datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
    f"published_by={me}",
    f"source={repo_root}",
]
for label, root, names in SETS:
    for s in names:
        with open(f"{root}/{s}/SKILL.md", encoding="utf-8") as fh:
            m = re.search(r'version:\s*"([^"]+)"', fh.read())
        lines.append(f"{s}={m.group(1) if m else '?'}")
if OFFICIAL:
    with open(f"{repo_root}/install/official/SOURCE.md", encoding="utf-8") as fh:
        m = re.search(r"commit\s+`([0-9a-f]{7,40})`", fh.read())
    lines.append(f"official_commit={m.group(1) if m else '?'}")
stamp = "\n".join(lines) + "\n"
upload(f"{target_root}/_VERSION", stamp.encode("utf-8"))
print(stamp)

# COMMAND ----------

# Verify: every repo file exists in the target with identical content.
ok, failed = 0, []
for label, root, names in SETS:
    for skill in names:
        bad = None
        for full, rel in source_files(root, skill):
            with open(full, "rb") as fh:
                want = fh.read()
            try:
                got = w.workspace.download(f"{target_root}/{rel}").read()
            except Exception as e:
                bad = f"{rel}: missing ({type(e).__name__})"
                break
            if got.replace(b"\r\n", b"\n") != want.replace(b"\r\n", b"\n"):
                bad = f"{rel}: content differs"
                break
        if bad:
            failed.append(bad)
        else:
            ok += 1
print(f"{ok} ok, {len(failed)} failed")
for f in failed:
    print("FAIL", f)
if DRY:
    print("(dry run: failures are expected because nothing was written)")
elif failed:
    raise RuntimeError("verification failed; see FAIL lines")
