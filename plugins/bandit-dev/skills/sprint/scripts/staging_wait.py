#!/usr/bin/env python3
"""Checks, and waits for, the commit staging runs after a push of the trunk (references/execute.md → Pushing
`development`, Staging). It runs the recipe's `staging.commit` (prints the commit staging runs on its last line) and
compares it with the pushed hash; a short hash matches its full one.

Usage:
  staging_wait.py [--file PATH] --once HASH               one check, before any refresh
  staging_wait.py [--file PATH] --state FILE HASH         after the refresh: re-check every minute; returns after at
                                                          most 9 minutes (one shell call), so run it again while it
                                                          says still waiting; the first call writes its start time in
                                                          FILE (the session's scratch folder, never the repo)
  Test options: --every SECONDS (60) · --call MINUTES (9) · --limit MINUTES (30)

Prints `staging runs {commit}` on a match. Exit codes: 0 staging runs HASH · 1 it does not yet (still waiting) ·
2 usage · 3 recipe (named) · 4 the recipe has no `staging.commit`: nothing to compare · 5 the limit passed since the
first call (30 minutes): staging still runs another commit, both named.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe  # noqa: E402  (the one reader of bandit.yaml)


def served(root, cmd):
    """The last line `staging.commit` prints, or '' when it prints nothing or fails."""
    r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
    return lines[-1] if r.returncode == 0 and lines else ""


def same(a, b):
    a, b = a.lower(), b.lower()
    return len(min(a, b, key=len)) >= 7 and (a.startswith(b) or b.startswith(a))


def main(argv):
    path = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()) / "bandit.yaml"
    state, once, every, call, limit = None, False, 60.0, 9.0, 30.0
    rest = []
    while argv:
        a = argv.pop(0)
        if a == "--once":
            once = True
        elif a in ("--file", "--state", "--every", "--call", "--limit") and argv:
            v = argv.pop(0)
            if a == "--file":
                path = Path(v).resolve()
            elif a == "--state":
                state = v
            else:
                try:
                    num = float(v)
                except ValueError:
                    print(__doc__)
                    return 2
                every, call, limit = (num, call, limit) if a == "--every" else \
                    (every, num, limit) if a == "--call" else (every, call, num)
        else:
            rest.append(a)
    if len(rest) != 1 or once == bool(state):
        print(__doc__)
        return 2
    pushed = rest[0]
    data = recipe.load(path)
    cmd = None if recipe.absent(data, "staging.commit") else str(recipe.lookup(data, "staging.commit"))
    if cmd is None:
        print("staging wait: the recipe has no `staging.commit`: nothing to compare")
        return 4
    root = path.parent
    if once:
        got = served(root, cmd)
        if same(got, pushed):
            print(f"staging runs {got}")
            return 0
        print(f"staging runs {got or 'nothing readable'}, not {pushed}")
        return 1
    try:
        st = json.loads(Path(state).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        st = {"started": time.time(), "pushed": pushed}
        Path(state).write_text(json.dumps(st), encoding="utf-8")
    end_call = time.time() + call * 60
    deadline = st["started"] + limit * 60
    while True:
        got = served(root, cmd)
        if same(got, pushed):
            print(f"staging runs {got}")
            return 0
        now = time.time()
        if now >= deadline:
            print(f"staging wait: {limit:g} minutes since the refresh and staging runs {got or 'nothing readable'}, "
                  f"not {pushed}")
            return 5
        if now >= end_call:
            print(f"staging runs {got or 'nothing readable'}, not {pushed} yet: still waiting, run it again")
            return 1
        time.sleep(max(0.05, min(every, deadline - now, end_call - now)))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
