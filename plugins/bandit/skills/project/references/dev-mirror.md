# 🪞 Dev mirror — Stop hook and script

> Read when onboarding or auditing a `dev: true` project. Holds the exact repo change that keeps
> `MyNotes/{Domain}/Claude/code-{slug}/` a current, Obsidian-visible mirror of the repo's
> `CLAUDE.md` + `.claude/`. Hook format checked against the Claude Code hooks docs
> (https://code.claude.com/docs/en/hooks) on 2026-09-28.

## 🧭 How it works

| Piece | Does |
|---|---|
| `Stop` command hook in `.claude/settings.json` | Runs the script each time Claude finishes a turn |
| `.claude/hooks/mirror-check.py` | Hashes `CLAUDE.md` + every file under `.claude/` (except `settings.local.json`, the stamp and `worktrees/`, where Claude Code keeps whole worktree checkouts), compares with the stamp, and **copies the changed files itself** into the Nextcloud-synced vault folder |
| `.claude/mirror-stamp.json` (gitignored) | Per-file sha256 from the last mirror |

- **The script copies, Claude doesn't.** No model call and no connector, so auto mode's check
  (which reads "repo files → outside service" as data exfiltration) never sees it, and it costs
  no tokens. Nextcloud desktop sync uploads the copies. This is the one exception to "vault writes
  go through WebDAV", approved by Leo 2026-09-30.
- **Vault root:** `$MYNOTES_DIR`, else `~/Documents/MyNotes`. Set `MYNOTES_DIR` in the user
  settings `env` block (`~/.claude/settings.json`) on a machine where the synced folder lives
  elsewhere. Never in the repo.
- **No change** → exit 0, silent. **Change** → copy (`.claude/` stored as `claude/`, since
  Obsidian hides dot-folders), stamp, one-line `systemMessage`. The copy gets a fresh date, which
  S11 reads as the mirror date.
- **Target missing** (no synced vault on this machine, or `code-{slug}/` not created) → a
  `systemMessage`, nothing copied, no stamp. It never creates the folder: that's bandit:notes'.
- A copy that fails → `systemMessage`, stamp left alone, retried next turn. Never blocks the turn.
- `domain` and `project` come from the `## 🧭 Project Context` in `CLAUDE.md`. Missing or
  `domain: none` → `systemMessage`, nothing copied.
- Removed repo files are reported, never deleted from the vault.

## 📦 The repo change (handed to Claude Code, never written by this skill)

**1. `.claude/settings.json`** — add to `hooks.Stop`; merge with any hooks already there
(`Stop` takes no matcher). The command runs `python3`, or `python` where `python3` isn't on the PATH:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "if command -v python3 >/dev/null 2>&1; then exec python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/mirror-check.py\"; else exec python \"${CLAUDE_PROJECT_DIR}/.claude/hooks/mirror-check.py\"; fi"
          }
        ]
      }
    ]
  }
}
```

**2. `.gitignore`** — add:

```
.claude/mirror-stamp.json
```

**3. `.claude/hooks/mirror-check.py`** — exactly this:

```python
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
```

**The sprint checker is not wired here.** It ships with the `bandit-dev` plugin as that plugin's
own `Stop` hook (`hooks/hooks.json`, `${CLAUDE_PLUGIN_ROOT}`): installing `bandit-dev` turns it on in
every repo, and a repo adds nothing. A machine that still registers the old checker by hand in the
user settings (`~/.claude/settings.json`) runs it twice: remove that user-level entry (Leo, by hand).

**4. First run:** no stamp yet, so the first Stop copies every file into `code-{slug}/`
(bandit:notes creates the folder at onboarding) and stamps. Upgrading from the old script (the one
that asked Claude to write through WebDAV): replace the file, delete `.claude/mirror-stamp.json` if
there is one, and end a turn: the whole mirror is recopied.

## ⚠️ Gotchas

- **2026-09-30 · Auto mode blocked the CS Notes mirror as data exfiltration.** The old script asked
  Claude to read the repo files and write them through the BanditCloud connector; 39 of 43 files
  were refused. → The script copies into the synced folder itself (**How it works**).
- **2026-09-30 · The script would have mirrored `.claude/worktrees/`.** Claude Code creates each
  worktree as a full checkout under `.claude/worktrees/`, and `rglob` walked into it. → `SKIP_DIRS`
  excludes it; any other non-settings folder Claude Code adds under `.claude/` goes there too.
