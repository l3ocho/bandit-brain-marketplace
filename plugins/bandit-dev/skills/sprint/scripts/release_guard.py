#!/usr/bin/env python3
"""Guards a sprint release around the project's recipe steps (references/release.md). The recipe holds the
commands; this script holds the order: notes before the bump, nothing committed between the bump's tag and the
deploy branch's push, a green CI run before anything after that push, and the running version at the end.

The project names its own checks in the optional `release_checks` section of `bandit.yaml`:
  gate       a command run before the first step; non-zero stops the release (BanditBrain: its release-docs gate)
  ci         a command that waits for the deploy branch's CI run and exits non-zero on red
  version    a command that prints the version production runs
  whats_new  a command that prints the version the app's What's new shows

Usage:
  release_guard.py [--file PATH] lint                         refuse a `release` list whose notes step comes after the bump
  release_guard.py [--file PATH] gate                         run `release_checks.gate` (or say none is named)
  release_guard.py [--file PATH] --state FILE start           before step 1: record the tags and the deploy branch on origin
  release_guard.py [--file PATH] --state FILE before N        before step N: the trunk has not moved since the bump's tag;
                                                              after the deploy push, the CI run is green
  release_guard.py [--file PATH] --state FILE after N         after step N: note a new `v*` tag (the bump) and a moved
                                                              deploy branch on origin (the push)
  release_guard.py [--file PATH] --state FILE final VERSION   after the last step: `version` (and `whats_new`) print VERSION

The state file lives in the session's scratch folder, never in the repo.
Exit codes: 0 ok · 2 usage · 3 recipe (named) · 4 order refused (named) · 5 a check failed · 6 no CI watch named.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe  # noqa: E402  (the one reader of bandit.yaml)

# A step that runs the version bump, and a step that writes the release notes. Prose that only mentions a bump
# ("before the bump") or reads What's new ("What's new opens on it") is neither.
BUMP = re.compile(r"\bnpm version\b|\byarn version\b|\bpoetry version\b|\bcz bump\b|\bbump2version\b|"
                  r"release\.py\b[^\n]*--write|\bgit tag\b", re.I)
NOTES = re.compile(r"\b(add|write|update|rename|fill)\b[^.\n]{0,80}?(release notes|what'?s new|changelog|user manual)", re.I)


def refuse(code, msg):
    print(f"release guard: {msg}", file=sys.stderr)
    sys.exit(code)


def git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def short(step):
    step = " ".join(str(step).split())
    return step if len(step) <= 90 else step[:87] + "…"


def lint(data):
    steps = recipe.lookup(data, "release")
    bump = next((i for i, s in enumerate(steps) if BUMP.search(str(s))), None)
    if bump is None:
        return "release order: no step runs a version bump that the guard can see; nothing to check"
    late = [i for i, s in enumerate(steps) if i > bump and NOTES.search(str(s))]
    if late:
        refuse(4, f"step {late[0] + 1} writes the release notes after the bump (step {bump + 1}): "
                  f"\"{short(steps[late[0]])}\". Move it before \"{short(steps[bump])}\" in bandit.yaml")
    return f"release order: no notes step after the bump (step {bump + 1})"


def check(data, key):
    """The `release_checks` command for key, or None when the recipe names none."""
    sect = data.get("release_checks")
    if not isinstance(sect, dict) or sect.get(key) in (None, ""):
        return None
    return str(sect[key])


def run(root, cmd):
    r = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def deploy_on_origin(root, deploy):
    git(root, "fetch", "-q", "origin", deploy)
    return git(root, "rev-parse", f"origin/{deploy}")


def tags(root):
    return sorted(t for t in git(root, "tag", "--list", "v*").splitlines() if t)


def load_state(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        refuse(2, f"no release state at {path}: run `start` before the first step")


def main(argv):
    path = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()) / "bandit.yaml"
    state = None
    while argv and argv[0] in ("--file", "--state") and len(argv) >= 2:
        if argv[0] == "--file":
            path = Path(argv[1]).resolve()
        else:
            state = argv[1]
        argv = argv[2:]
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    data = recipe.load(path)
    root = path.parent
    if cmd == "lint" and not args:
        print(lint(data))
    elif cmd == "gate" and not args:
        gate = check(data, "gate")
        if gate is None:
            print("release guard: the recipe names no release gate (release_checks.gate)")
            return 0
        code, out = run(root, gate)
        if code != 0:
            refuse(5, f"the project's release gate refused ({code}): {out[-400:]}")
        print("release guard: the project's release gate passed")
    elif cmd in ("start", "before", "after", "final") and state:
        deploy = str(recipe.lookup(data, "branches.deploy"))
        if cmd == "start" and not args:
            st = {"tags": tags(root), "deploy": deploy_on_origin(root, deploy), "bump_tag": None, "pushed": False,
                  "ci_green": False}
            Path(state).write_text(json.dumps(st), encoding="utf-8")
            print(f"release guard: recorded {len(st['tags'])} tags and origin/{deploy}")
        elif cmd == "after" and len(args) == 1:
            st = load_state(state)
            new = [t for t in tags(root) if t not in st["tags"]]
            if new and not st["bump_tag"]:
                st["bump_tag"] = new[-1]
            if st["bump_tag"] and not st["pushed"] and deploy_on_origin(root, deploy) != st["deploy"]:
                st["pushed"] = True
            st["tags"] = tags(root)
            Path(state).write_text(json.dumps(st), encoding="utf-8")
            print(f"release guard: after step {args[0]}: bump {st['bump_tag'] or 'not yet'}, "
                  f"{deploy} {'pushed' if st['pushed'] else 'not pushed yet'}")
        elif cmd == "before" and len(args) == 1:
            st = load_state(state)
            if st["bump_tag"] and not st["pushed"]:
                at_tag = git(root, "rev-list", "-n", "1", st["bump_tag"])
                if git(root, "rev-parse", "HEAD") != at_tag:
                    moved = git(root, "log", "--oneline", f"{st['bump_tag']}..HEAD")
                    refuse(4, f"the trunk moved after {st['bump_tag']}: nothing may be committed between the bump and "
                              f"the push of {deploy}. Commits: {moved or 'HEAD is not the tag'}")
            if st["pushed"] and not st["ci_green"]:
                ci = check(data, "ci")
                if ci is None:
                    refuse(6, f"{deploy} is pushed and the recipe names no CI watch (release_checks.ci): the user "
                              "confirms the CI run is green before any later step")
                code, out = run(root, ci)
                if code != 0:
                    refuse(5, f"the CI run on {deploy} is not green ({code}): no later step runs. {out[-300:]}")
                st["ci_green"] = True
                Path(state).write_text(json.dumps(st), encoding="utf-8")
            print(f"release guard: step {args[0]} may run")
        elif cmd == "final" and len(args) == 1:
            want = args[0].lstrip("v")
            for key, what in (("version", "production runs"), ("whats_new", "What's new shows")):
                c = check(data, key)
                if c is None:
                    print(f"release guard: the recipe names no `release_checks.{key}`: not checked")
                    continue
                code, out = run(root, c)
                if code != 0 or want not in out:
                    refuse(5, f"{what} {out.splitlines()[-1] if out else 'nothing'}, not {want}")
                print(f"release guard: {what} {want}")
        else:
            print(__doc__)
            return 2
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
