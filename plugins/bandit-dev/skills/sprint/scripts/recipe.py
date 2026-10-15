#!/usr/bin/env python3
"""Reads the project's recipe, `bandit.yaml` at the repo root. The skill holds the gate; the
project holds the recipe. A missing file or key refuses and names it (contract: the marketplace
repo's docs/bandit-yaml.md).

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

import yaml

# Every key the sprint skill reads, and the command that reads it (docs/bandit-yaml.md).
KEYS = {
    "verify": "execute, run, debug: the check a wave, a fix and a push must pass",
    "branches.trunk": "execute, run, debug: the branch waves merge into and push",
    "branches.deploy": "release: the branch a release fast-forwards",
    "release": "release: the ordered release steps",
    "migrations.dir": "plan: where migrations live",
    "migrations.check": "execute, run, release: prints the current migration tail",
    "staging.refresh": "release: the instruction the user runs to test the release on staging",
    "testdata.schema": "testdata: where the tables are defined",
    "testdata.logic": "testdata: where the app enforces its rules",
    "testdata.databases": "testdata: one command per database that runs SQL from stdin",
}
# A repo without migrations, staging or testdata leaves the whole section out; a section present is complete.
OPTIONAL = ("migrations", "staging", "testdata")


def refuse(code, msg):
    print(f"bandit.yaml: {msg}", file=sys.stderr)
    sys.exit(code)


def load(path):
    if not path.exists():
        refuse(3, f"no recipe file at {path}: the project must provide bandit.yaml")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        refuse(3, f"{path} is not valid YAML ({str(e).splitlines()[0]})")
    if not isinstance(data, dict):
        refuse(3, f"{path} is not a mapping of keys")
    return data


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
