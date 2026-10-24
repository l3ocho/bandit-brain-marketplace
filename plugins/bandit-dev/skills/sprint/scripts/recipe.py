#!/usr/bin/env python3
"""Reads the project's recipe, `bandit.yaml` at the repo root. The skill holds the gate; the
project holds the recipe. A missing file or key refuses and names it (contract: references/bandit-yaml.md
in this skill).

Usage:
  recipe.py [--file PATH] get KEY            print one value (a list prints one item per line,
                                             a mapping one `key<TAB>value` line per entry)
  recipe.py [--file PATH] require KEY [KEY…] exit 0 only when every key is present
  recipe.py [--file PATH] opt KEY            print an optional key's value, or `none` when absent
  recipe.py [--file PATH] tail               run migrations.check, print the current tail
                                             (`none` when the recipe has no `migrations` section)
  recipe.py [--file PATH] check-tail EXPECT  exit 0 only when the tail equals EXPECT

Exit codes: 0 ok · 2 usage · 3 missing file or key (named) · 4 migration tail differs · 5 command failed.
The default file is bandit.yaml in $CLAUDE_PROJECT_DIR, else the current directory.
"""
import os
import subprocess
import sys
from pathlib import Path

# Every key the bandit-dev skills read, and the command that reads it (references/bandit-yaml.md).
KEYS = {
    "verify": "execute, run, debug: the check a wave, a fix and a push must pass",
    "branches.trunk": "execute, run, debug, testdata: the branch waves merge into and push",
    "branches.deploy": "release: the branch a release fast-forwards",
    "release": "release: the ordered release steps",
    "migrations.dir": "plan: where migrations live",
    "migrations.check": "execute, run, release: prints the current migration tail",
    "staging.refresh": "release: the instruction the user runs to test the release on staging",
    "testdata.schema": "testdata: where the tables are defined",
    "testdata.logic": "testdata: where the app enforces its rules",
    "testdata.databases": "testdata: one command per database that runs SQL from stdin",
    "handover.board": "plan, execute, release: the board the deployment handover cards go on",
    "handover.production.column": "plan, release: the column of the production handover card",
    "handover.production.runbook": "release: the production deploy steps (path#section)",
    "handover.staging.column": "plan, execute: the column of the staging handover card",
    "handover.staging.runbook": "execute: the staging deploy steps (path#section)",
    "guard.credentials.block": "credential guard hook: regexes of commands no agent runs",
    "guard.credentials.allow": "credential guard hook: regexes of the project's allowed dev-login commands",
    "stop.paths": "stop gate hook: the paths that count as implementation (git pathspecs)",
    "stop.close": "stop gate hook: the close step its message names",
}
# A repo without an optional section leaves it out; a section present is complete.
OPTIONAL = ("migrations", "staging", "testdata", "handover", "guard", "stop")


class RecipeError(Exception):
    """A recipe a hook cannot read: broken YAML, not a mapping, or PyYAML missing."""


def refuse(code, msg):
    print(f"bandit.yaml: {msg}", file=sys.stderr)
    sys.exit(code)


def parse_text(text, name="bandit.yaml"):
    """The recipe as a mapping; RecipeError when it cannot be read. yaml is imported only here."""
    try:
        import yaml
    except ImportError:
        raise RecipeError("PyYAML is not installed (pip install pyyaml)")
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        raise RecipeError(f"{name} is not valid YAML ({str(e).splitlines()[0]})")
    if not isinstance(data, dict):
        raise RecipeError(f"{name} is not a mapping of keys")
    return data


def parse(path):
    return parse_text(path.read_text(encoding="utf-8"), str(path))


def load(path):
    if not path.exists():
        refuse(3, f"no recipe file at {path}: the project must provide bandit.yaml")
    try:
        return parse(path)
    except RecipeError as e:
        refuse(3, str(e))


def load_optional(path):
    """For hooks: None when there is no file; RecipeError when it cannot be read."""
    return parse(path) if path.exists() else None


def lookup(data, key):
    node = data
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node or node[part] in (None, "", []):
            refuse(3, f"missing key `{key}`" + (f" (used by {KEYS[key]})" if key in KEYS else ""))
        node = node[part]
    return node


def show(value):
    """A list prints one item per line, a mapping one `key<TAB>value` line per entry."""
    if isinstance(value, list):
        return "\n".join(map(str, value))
    if isinstance(value, dict):
        return "\n".join(f"{k}\t{v}" for k, v in value.items())
    return str(value)


def tail(data, root):
    if data.get("migrations") in (None, "", {}):
        return "none"
    cmd = lookup(data, "migrations.check")
    r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
    out = r.stdout.strip().splitlines()
    if r.returncode != 0 or not out:
        refuse(5, f"`migrations.check` failed ({r.returncode}): {(r.stderr or r.stdout).strip()[:200]}")
    return out[-1].strip()


def main(argv):
    path = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()) / "bandit.yaml"
    if len(argv) >= 2 and argv[0] == "--file":
        path, argv = Path(argv[1]), argv[2:]
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    data = load(path)
    if cmd == "get" and len(args) == 1:
        print(show(lookup(data, args[0])))
    elif cmd == "opt" and len(args) == 1:
        if args[0].split(".")[0] not in OPTIONAL:
            refuse(2, f"`{args[0]}` is not optional: use get")
        if data.get(args[0].split(".")[0]) in (None, "", {}):
            print("none")
        else:
            print(show(lookup(data, args[0])))
    elif cmd == "require" and args:
        for key in args:
            lookup(data, key)
        print(f"bandit.yaml: {len(args)} key(s) present")
    elif cmd == "tail" and not args:
        print(tail(data, path.parent))
    elif cmd == "check-tail" and len(args) == 1:
        now = tail(data, path.parent)
        if now != args[0]:
            refuse(4, f"migration tail is {now}, the plan names {args[0]}: stop the wave and report it")
        print(f"bandit.yaml: migration tail {now} matches the plan")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
