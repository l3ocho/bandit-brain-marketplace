#!/usr/bin/env python3
"""Says whether a change needs the full check: only a change to code does.

Compares the working tree (commits and uncommitted edits) with a base and prints one first line:

  full check: needed — code changed since {base} in {n} files: {files}
  full check: not needed — since {base}, only docs, notes and comments changed ({files, each with why})

No code, file by file:
  docs      a .md, .markdown, .txt or .rst file outside the recipe's `stop.paths` (the implementation paths;
            a doc inside them ships with the app and counts as code); with no `stop` section, any such file
  comments  a file whose every changed line is blank or a comment in its own syntax (// /* * */ {/* */},
            #, --), the file not renamed and not binary
Anything else is code, and so is anything this script cannot read: it then says needed, never skips a check.

Usage:
  code_changed.py [--since REF]   default: on a branch other than the trunk, where it left the trunk
                                  (git merge-base); on the trunk, origin/{trunk} (what a push would send).
                                  The release passes the commit of the last green full check.
The trunk is the recipe's `branches.trunk` (bandit.yaml in $CLAUDE_PROJECT_DIR, else the current directory).
Exit 0 with the line; 2 on a usage error.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recipe  # noqa: E402  (the one reader of bandit.yaml)

DOCS = {".md", ".markdown", ".txt", ".rst"}
SLASH = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts", ".css", ".scss", ".less", ".java", ".kt",
         ".go", ".rs", ".swift", ".c", ".h", ".cpp", ".cs", ".php", ".dart"}
HASH = {".py", ".sh", ".bash", ".yaml", ".yml", ".toml", ".rb", ".r", ".pl", ".ps1", ".tf"}
DASH = {".sql", ".lua", ".hs"}


class Unreadable(Exception):
    pass


def git(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise Unreadable((r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else
                         f"git {' '.join(args)} failed")
    return r.stdout


def comment(line, ext):
    s = line.strip()
    if not s:
        return True
    if ext in SLASH:
        if s.startswith("{/*") and s.endswith("*/}"):
            return True
        if s.startswith(("//", "/*", "*")):
            rest = s.split("*/", 1)[1].strip() if "*/" in s else ""
            return not rest
        return False
    if ext in HASH:
        return s.startswith("#") and not s.startswith("#!")
    if ext in DASH:
        return s.startswith("--")
    return False


def inside(path, paths):
    p = PurePosixPath(path)
    return any(p == PurePosixPath(x) or PurePosixPath(x) in p.parents for x in paths)


def verdict(root, base, impl):
    """[(file, why)] for the files with no code, [file] for those with code."""
    quiet, code = [], []
    status = git(root, "diff", "-M", "--name-status", base).splitlines()
    status += [f"A\t{f}" for f in git(root, "ls-files", "--others", "--exclude-standard").splitlines() if f]
    for row in status:
        parts = row.split("\t")
        kind, path = parts[0], parts[-1]
        ext = PurePosixPath(path).suffix.lower()
        if ext in DOCS and not (impl and inside(path, impl)):
            quiet.append((path, "docs"))
            continue
        if kind.startswith(("R", "C")) or not (ext in SLASH or ext in HASH or ext in DASH):
            code.append(path)
            continue
        if kind == "A" and not git(root, "ls-files", path).strip():
            text = (root / path).read_text(encoding="utf-8", errors="replace").splitlines()
            lines = ["+" + t for t in text]
        else:
            numstat = git(root, "diff", "--numstat", base, "--", path).split("\t")
            if numstat and numstat[0] == "-":
                code.append(path)
                continue
            lines = [ln for ln in git(root, "diff", "-U0", base, "--", path).splitlines()
                     if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
        (quiet.append((path, "comments")) if all(comment(ln[1:], ext) for ln in lines) else code.append(path))
    return quiet, code


def default_base(root, trunk):
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    if branch == trunk:
        return f"origin/{trunk}"
    return git(root, "merge-base", trunk, "HEAD").strip()


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since")
    args = ap.parse_args(argv)
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    try:
        data = recipe.load_optional(root / "bandit.yaml") or {}
    except recipe.RecipeError as e:
        data = {}
        print(f"(bandit.yaml cannot be read: {e}; every doc counts as no code)", file=sys.stderr)
    stop = data.get("stop") if isinstance(data.get("stop"), dict) else {}
    impl = [p for p in stop.get("paths") or [] if isinstance(p, str)]
    trunk = (data.get("branches") or {}).get("trunk") if isinstance(data.get("branches"), dict) else None
    if not args.since and not trunk:
        print("full check: needed — no `branches.trunk` in bandit.yaml to compare with; pass --since REF")
        return 0
    try:
        base = args.since or default_base(root, trunk)
        short = git(root, "rev-parse", "--short", base).strip()
        quiet, code = verdict(root, base, impl)
    except (Unreadable, OSError) as e:
        print(f"full check: needed — cannot compare ({e})")
        return 0
    if code:
        shown = ", ".join(code[:10]) + (f" and {len(code) - 10} more" if len(code) > 10 else "")
        print(f"full check: needed — code changed since {short} in {len(code)} file{'s' if len(code) != 1 else ''}: {shown}")
    elif quiet:
        print(f"full check: not needed — since {short}, only docs, notes and comments changed ("
              + ", ".join(f"{f} ({why})" for f, why in quiet) + ")")
    else:
        print(f"full check: not needed — nothing changed since {short}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
