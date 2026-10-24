#!/usr/bin/env python3
"""Stop hook: refuses to end a chat that leaves implementation changes uncommitted.

The project names what counts as implementation and its close step in `bandit.yaml`:

  stop:
    paths: [src, migrations, package.json]   # git pathspecs
    close: the step that commits the work      # shown in the message

No `bandit.yaml`, or no `stop` section: the hook does nothing. Already continuing because of a Stop
hook (`stop_hook_active`): it lets the chat end rather than loop.

Wave agents share the working directory, so a main chat can stop while a background agent is still
editing. Once the chat's own transcript shows it launched an agent (`Agent` or `Task`), only dirty
files this chat edited itself (Edit, Write, NotebookEdit) count. A chat that launched no agent is
held to every dirty implementation file. A recipe it cannot read prints one line and lets the chat
end: this gate reminds, the credential guard is the one that fails closed.

Contract: references/bandit-yaml.md in this skill.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe  # noqa: E402  (the one reader of bandit.yaml)

AGENTS = {"Agent", "Task"}
EDITS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def section(root):
    """(paths, close), or None when the project has no `stop` section."""
    path = root / "bandit.yaml"
    if not path.exists() or "stop" not in path.read_text(encoding="utf-8"):
        return None
    stop = (recipe.load_optional(path) or {}).get("stop")
    if stop in (None, "", {}):
        return None
    paths, close = (stop.get("paths"), stop.get("close")) if isinstance(stop, dict) else (None, None)
    if not paths or not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
        raise recipe.RecipeError("`stop.paths` must be a list of paths")
    if not isinstance(close, str) or not close.strip():
        raise recipe.RecipeError("`stop.close` is missing")
    return paths, close


def dirty(root, paths):
    out = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all", "--", *paths],
                         capture_output=True, text=True, timeout=8, check=True).stdout
    files = []
    for line in out.splitlines():
        name = line[3:]
        files.append(name.split(" -> ", 1)[-1].strip('"'))  # a rename counts as its new path
    return files


def own_work(transcript, root):
    """(launched an agent, the repo-relative files this chat edited itself)."""
    launched, edited = False, set()
    if not transcript or not os.path.exists(transcript):
        return launched, edited
    base = root.resolve()
    with open(transcript, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                content = json.loads(line).get("message", {}).get("content")
            except (ValueError, AttributeError):
                continue
            for item in content if isinstance(content, list) else []:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                if item.get("name") in AGENTS:
                    launched = True
                elif item.get("name") in EDITS:
                    target = (item.get("input") or {}).get("file_path") or (item.get("input") or {}).get("notebook_path")
                    if isinstance(target, str):
                        p = Path(target)
                        p = (p if p.is_absolute() else base / p).resolve()
                        if p.is_relative_to(base):
                            edited.add(p.relative_to(base).as_posix())
    return launched, edited


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("stop_hook_active"):
        return 0
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd())
    try:
        found = section(root)
    except (recipe.RecipeError, OSError) as e:
        print(f"bandit-dev stop gate: bandit.yaml `stop` cannot be read ({e}); not checked.", file=sys.stderr)
        return 0
    if not found:
        return 0
    paths, close = found
    try:
        files = dirty(root, paths)
    except (OSError, subprocess.SubprocessError):
        return 0  # not a git repo, or git unavailable: nothing to hold the chat to
    launched, edited = own_work(payload.get("transcript_path"), root)
    if launched:
        files = [f for f in files if f in edited]
    if not files:
        return 0
    print("Implementation changes are uncommitted:\n" + "\n".join(f"  {f}" for f in files)
          + f"\n\nClose the loop before stopping: {close}.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
