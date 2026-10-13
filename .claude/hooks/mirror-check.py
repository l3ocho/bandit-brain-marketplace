#!/usr/bin/env python3
"""Stop hook: mirror CLAUDE.md + .claude/ into the Nextcloud-synced MyNotes folder.

The script copies the files itself; Claude never moves them, so no model call and no
auto-mode check is involved. Nextcloud desktop sync uploads the copies to the vault.
No change -> exit 0, silent. Change -> copy, stamp, one-line systemMessage.
Vault root: $MYNOTES_DIR, else ~/Documents/MyNotes. Target folder must already exist
(bandit:notes creates it at onboarding): MyNotes/{domain}/Claude/code-{project}/.
"""
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
STAMP = ROOT / ".claude" / "mirror-stamp.json"
SKIP = {".claude/settings.local.json", ".claude/mirror-stamp.json"}
SKIP_DIRS = (".claude/worktrees/",)  # Claude Code worktrees: full repo checkouts, never settings


def current():
    files = {}
    candidates = [ROOT / "CLAUDE.md"]
    if (ROOT / ".claude").is_dir():
        candidates += sorted(p for p in (ROOT / ".claude").rglob("*") if p.is_file())
    for p in candidates:
        rel = p.relative_to(ROOT).as_posix()
        if rel in SKIP or rel.startswith(SKIP_DIRS) or "__pycache__" in p.parts or not p.is_file():
            continue
        files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return files


def context():
    try:
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    except OSError:
        return None, None
    block = text.split("## 🧭 Project Context", 1)
    if len(block) < 2:
        return None, None
    get = lambda k: (re.search(rf"^{k}:\s*(\S+)", block[1], re.M) or [None, None])[1]
    return get("domain"), get("project")


def vault_name(rel):
    return "claude/" + rel[len(".claude/"):] if rel.startswith(".claude/") else rel


def say(msg):
    print(json.dumps({"systemMessage": f"Dev mirror: {msg}"}))
    return 0


def main():
    try:
        hook = json.load(sys.stdin)
    except ValueError:
        hook = {}
    if hook.get("stop_hook_active"):
        return 0
    try:
        old = json.loads(STAMP.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    new = current()
    changed = sorted(k for k in new if old.get(k) != new[k])
    removed = sorted(k for k in old if k not in new)
    if not changed and not removed:
        return 0
    domain, slug = context()
    if not domain or not slug or domain == "none":
        return say("Project Context domain/project missing or none in CLAUDE.md; nothing mirrored.")
    vault = Path(os.environ.get("MYNOTES_DIR") or Path.home() / "Documents" / "MyNotes").expanduser()
    target = vault / domain / "Claude" / f"code-{slug}"
    if not target.is_dir():
        return say(f"{target} doesn't exist (no synced vault here, or the folder isn't created); "
                   "nothing mirrored. Set MYNOTES_DIR, or have bandit:notes create the folder.")
    done = []
    try:
        for rel in changed:
            dest = target / vault_name(rel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)  # fresh mtime: S11 reads it as the mirror date
            done.append(rel)
    except OSError as e:
        return say(f"copy failed at {rel} ({e}); {len(done)} copied, stamp left alone.")
    STAMP.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    msg = f"{len(done)} file(s) copied to {target}."
    if removed:
        msg += " Gone from the repo, left in the vault: " + ", ".join(vault_name(k) for k in removed) + "."
    return say(msg)


if __name__ == "__main__":
    sys.exit(main())
