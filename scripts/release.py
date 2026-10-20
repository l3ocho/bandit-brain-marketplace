#!/usr/bin/env python3
"""Cut a marketplace release: one shared version for every plugin, Semantic Versioning, tag vX.Y.Z.

  release.py X.Y.Z            dry run: says what would change, changes nothing
  release.py X.Y.Z --write    bump every plugin.json and the marketplace, date the CHANGELOG's
                              `## Unreleased` entry, empty the done check's checked list, run the gate, commit on the trunk, fast-forward
                              the deploy branch, tag vX.Y.Z (all local)
  release.py X.Y.Z --push     push the trunk, the deploy branch and the tag (after --write)

Refuses: not on the trunk, a dirty tree, open rows in the done check, a version that isn't X.Y.Z or isn't above the current one,
no `## Unreleased` entry, an existing tag, or a red gate.
"""
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRUNK, DEPLOY = "development", "main"
CHANGELOG = ROOT / "CHANGELOG.md"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
DEPS = ROOT / "docs" / "dependencies.md"
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


def manifests():
    return sorted(ROOT.glob("plugins/*/.claude-plugin/plugin.json"))


def current_version():
    versions = {json.loads(p.read_text())["version"] for p in manifests()}
    if len(versions) != 1:
        sys.exit(f"plugins disagree on the version: {sorted(versions)}")
    return versions.pop()


def set_version(path, keys, version):
    data = json.loads(path.read_text())
    node = data
    for k in keys[:-1]:
        node = node.setdefault(k, {})
    node[keys[-1]] = version
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main(argv):
    if not argv or not SEMVER.match(argv[0]):
        sys.exit(__doc__)
    version, write, push = argv[0], "--write" in argv, "--push" in argv
    tag = f"v{version}"

    if push:
        if git("tag", "-l", tag) != tag:
            sys.exit(f"no local tag {tag}: run --write first")
        for ref in (TRUNK, DEPLOY, tag):
            git("push", "origin", ref)
        print(f"pushed {TRUNK}, {DEPLOY} and {tag}")
        return 0

    if git("branch", "--show-current") != TRUNK:
        sys.exit(f"release from {TRUNK} only")
    if git("status", "--porcelain"):
        sys.exit("the tree is not clean: commit or stash first")
    if git("tag", "-l", tag):
        sys.exit(f"tag {tag} already exists")
    old = current_version()
    if tuple(map(int, version.split("."))) <= tuple(map(int, old.split("."))):
        sys.exit(f"{version} is not above the current {old}")
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / "done_check.py")], cwd=ROOT,
                          capture_output=True, text=True)
    if done.returncode != 0:
        sys.exit(done.stdout + "\nthe done check has open rows (docs/dependencies.md): update them or list them as checked")
    text = CHANGELOG.read_text()
    if not re.search(r"^## Unreleased\b.*$", text, re.M):
        sys.exit("CHANGELOG.md has no `## Unreleased` entry to release")

    today = datetime.date.today().isoformat()
    plan = [f"{p.relative_to(ROOT)}: {old} → {version}" for p in manifests()]
    plan += [f".claude-plugin/marketplace.json metadata.version → {version}",
             f"CHANGELOG.md: `## Unreleased …` → `## {version} · {today} …`",
             f"gate, commit on {TRUNK}, fast-forward {DEPLOY}, tag {tag}"]
    print("\n".join(plan))
    if not write:
        print("dry run: nothing changed (add --write)")
        return 0

    for p in manifests():
        set_version(p, ["version"], version)
    set_version(MARKETPLACE, ["metadata", "version"], version)
    deps = DEPS.read_text()
    head = "## ☑️ Checked, nothing to change"
    before, rest = deps.split(head, 1)
    intro, after = rest.split("\n- ", 1)[0], "\n## " + rest.split("\n## ", 1)[1]
    DEPS.write_text(before + head + intro.rstrip("\n") + "\n\n- none yet\n" + after)
    CHANGELOG.write_text(re.sub(r"^## Unreleased(?: \([^)]*\))?", f"## {version} · {today}", text, count=1, flags=re.M))
    gate = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_repo.py")], cwd=ROOT)
    if gate.returncode != 0:
        git("checkout", "--", ".")
        sys.exit("the gate failed: changes reverted, nothing committed")
    git("commit", "-am", f"Release {version}")
    git("checkout", DEPLOY)
    git("merge", "--ff-only", TRUNK)
    git("tag", "-a", tag, "-m", f"{tag} · {today}")
    git("checkout", TRUNK)
    print(f"released {tag} locally; push with: scripts/release.py {version} --push")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
