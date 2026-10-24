#!/usr/bin/env python3
"""PreToolUse hook (Bash): refuses a command that writes, resets or mints a real login credential.

A sentence in an agent's instructions does not hold in the middle of a task (a testing agent reset a
real login to get past a sign-in screen); exit 2 stops the call before it runs, for the main session
and every subagent alike. The project lists what to refuse in its `bandit.yaml`:

  guard:
    credentials:
      block: [regex, …]   # commands no agent runs (credential scripts, a raw write to the column)
      allow: [regex, …]   # optional: the project's dev-only login commands, matched whole

No `bandit.yaml`, or no `guard` section: the hook does nothing. The command is split on `;`, `&&`,
`||`, `|` and newlines; a part an allow pattern matches whole is skipped, every other part is tested
against the block list, so an allowed command cannot carry a blocked one. A recipe that names a
`guard` but cannot be read refuses every command until it is fixed: the guard fails closed.

Contract: references/bandit-yaml.md in this skill.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe  # noqa: E402  (the one reader of bandit.yaml)

PARTS = re.compile(r"\|\||&&|[;|\n]")
ADVICE = ("No agent, main session or subagent, writes, resets or mints a real login credential. Ask the "
          "user to run it themselves, in their own terminal, never through this session.")


def patterns(section, key):
    value = (section or {}).get(key)
    if value in (None, "", []):
        return []
    if not isinstance(value, list) or not all(isinstance(p, str) for p in value):
        raise recipe.RecipeError(f"`guard.credentials.{key}` must be a list of regexes")
    try:
        return [re.compile(p) for p in value]
    except re.error as e:
        raise recipe.RecipeError(f"`guard.credentials.{key}` holds a bad regex ({e})")


def blocked(command, block, allow):
    """The block pattern a part of the command hits, or None."""
    for part in (p.strip() for p in PARTS.split(command)):
        if not part or any(a.fullmatch(part) for a in allow):
            continue
        for b in block:
            if b.search(part):
                return b.pattern
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str):
        return 0
    path = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()) / "bandit.yaml"
    try:
        if not path.exists() or "guard" not in path.read_text(encoding="utf-8"):
            return 0  # cheap exit on every Bash call of a project without the guard
        data = recipe.load_optional(path) or {}
        guard = data.get("guard")
        if guard in (None, "", {}):
            return 0
        section = guard.get("credentials") if isinstance(guard, dict) else None
        block = patterns(section, "block")
        if not block:
            raise recipe.RecipeError("`guard.credentials.block` is missing or empty")
        hit = blocked(command, block, patterns(section, "allow"))
    except (recipe.RecipeError, OSError) as e:
        print(f"Blocked: the credential guard cannot read bandit.yaml ({e}). Every command is refused "
              "until it is fixed: edit the file, then retry.", file=sys.stderr)
        return 2
    if hit:
        print(f"Blocked: this command sets a real login credential (it matches `{hit}` in bandit.yaml "
              f"`guard.credentials.block`). {ADVICE} A dev-only login command the project allows is "
              "listed under `guard.credentials.allow`.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
