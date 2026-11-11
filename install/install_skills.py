# Databricks notebook source
# MAGIC %md
# MAGIC # Install the de-* skills for Genie Code
# MAGIC
# MAGIC Run this notebook **from a Git folder of this repo** in the Databricks workspace.
# MAGIC
# MAGIC | Widget | Values | Effect |
# MAGIC |---|---|---|
# MAGIC | `scope` | `personal` | copies `skills/de-*` to `/Users/<you>/.assistant/skills` (any user) |
# MAGIC | | `workspace` | copies to `/Workspace/.assistant/skills` for everyone, writes `/Workspace/.assistant_workspace_instructions.md` and a `_VERSION` stamp (workspace admin only) |
# MAGIC | `dry_run` | `yes` / `no` | `yes` prints what would change and writes nothing |
# MAGIC
# MAGIC The last cell verifies every installed file against this repo and prints `13 ok, 0 failed`.
# MAGIC Official `databricks-*` skills are installed separately with the `install_genie_code_skills.py` notebook from
# MAGIC https://github.com/databricks-solutions/ai-dev-kit. Start a **new** Genie Code chat afterwards.

# COMMAND ----------

dbutils.widgets.dropdown("scope", "personal", ["personal", "workspace"])
dbutils.widgets.dropdown("dry_run", "no", ["no", "yes"])
SCOPE = dbutils.widgets.get("scope")
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
src_root = f"{repo_root}/skills"
if not os.path.isdir(src_root):
    raise RuntimeError(f"skills/ not found next to install/: {src_root}. Run this notebook from a Git folder of the repo.")

target_root = "/Workspace/.assistant/skills" if SCOPE == "workspace" else f"/Users/{me}/.assistant/skills"
skills = sorted(d for d in os.listdir(src_root) if d.startswith("de-") and os.path.isfile(f"{src_root}/{d}/SKILL.md"))
print(f"user={me} scope={SCOPE} dry_run={DRY}\nsource={src_root}\ntarget={target_root}\nskills ({len(skills)}): {', '.join(skills)}")

# COMMAND ----------

def upload(path: str, data: bytes):
    if DRY:
        print(f"DRY write {path} ({len(data)} bytes)")
        return
    w.workspace.mkdirs(path.rsplit("/", 1)[0])
    w.workspace.upload(path, io.BytesIO(data), format=ImportFormat.AUTO, overwrite=True)


def source_files(skill: str):
    base = f"{src_root}/{skill}"
    for dirpath, _, files in os.walk(base):
        for f in sorted(files):
            full = f"{dirpath}/{f}"
            yield full, full[len(src_root) + 1:]          # (filesystem path, relative path like de-x/SKILL.md)


# Remove de-* folders in the target that no longer exist in the repo (official databricks-* skills are untouched).
try:
    remote = [o.path.rsplit("/", 1)[-1] for o in w.workspace.list(target_root) if o.object_type == ObjectType.DIRECTORY]
except Exception:
    remote = []
for stale in sorted(r for r in remote if r.startswith("de-") and r not in skills):
    print(f"{'DRY ' if DRY else ''}delete stale {target_root}/{stale}")
    if not DRY:
        w.workspace.delete(f"{target_root}/{stale}", recursive=True)

for skill in skills:
    if not DRY:
        try:
            w.workspace.delete(f"{target_root}/{skill}", recursive=True)   # clean copy: removes files deleted in the repo
        except Exception:
            pass
    for full, rel in source_files(skill):
        with open(full, "rb") as fh:
            upload(f"{target_root}/{rel}", fh.read())
    print(f"installed {skill}")

# COMMAND ----------

# Workspace scope only: workspace instructions file and version stamp.
if SCOPE == "workspace":
    with open(f"{repo_root}/instructions/genie-code-user-instructions.md", encoding="utf-8") as fh:
        text = fh.read()
    body = text.split("\n----\n", 1)[1] if "\n----\n" in text else text      # paste-ready part after the ---- marker
    if len(body) >= 20000:
        raise RuntimeError("workspace instructions exceed Genie Code's 20,000 character cap")
    upload("/Workspace/.assistant_workspace_instructions.md", body.encode("utf-8"))

    versions = []
    for s in skills:
        with open(f"{src_root}/{s}/SKILL.md", encoding="utf-8") as fh:
            m = re.search(r'version:\s*"([^"]+)"', fh.read())
        versions.append(f"{s}={m.group(1) if m else '?'}")
    stamp = "\n".join([
        f"published_utc={datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"published_by={me}",
        f"source={repo_root}",
        *versions,
    ]) + "\n"
    upload(f"{target_root}/_VERSION", stamp.encode("utf-8"))
    print(stamp)

# COMMAND ----------

# Verify: every repo file exists in the target with identical content.
ok, failed = 0, []
for skill in skills:
    bad = None
    for full, rel in source_files(skill):
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
