#!/usr/bin/env python3
"""Working-folder guard for a Claude Code twin (structure rule S12).

Installed as `.claude/hooks/workdir.py` in the twin's working folder
(vault copy: `code-{slug}/claude/hooks/workdir.py`). Two modes:

  workdir.py guard     PreToolUse on Write|Edit|NotebookEdit. Exit 2 blocks a write
                       outside the layout, with the reason on stderr.
  workdir.py manifest  SessionStart. Writes `.claude/workdir-manifest.json` (paths,
                       dates, counts; never file contents, never file names under
                       data/) and, once a day, asks Claude to upload it to the vault.

Layout (root = $CLAUDE_PROJECT_DIR):
  CLAUDE.md  .claude/   settings, owned by bandit:project
  repos/                read-only clones
  work/{prefix}-{task}/ one folder per board task
  data/{prefix}-{task}/ data files for that task, purged on close
  scratch/              throwaway
  _closed/              closed work, written only by `/bandit:tasks done`
  _backup/              rollback copies of settings only: CLAUDE.md.*, settings.json.*, workdir.py.*
Superseded work stays in its task folder (work/{prefix}-{task}/superseded/), never _backup/.
A folder with its own CLAUDE.md is a hosted project: its own settings apply.

The constants below mirror `s12` in bandit:audit references/structure-rules.yaml.
Change one, change the other: bandit:audit checks this file's hash.
"""
import datetime, json, os, re, sys
from pathlib import Path

ROOT_ALLOWED = {"CLAUDE.md", ".claude", "repos", "work", "data", "scratch", "_closed", "_backup"}
BACKUP_NAME = re.compile(r"^(CLAUDE\.md|settings\.json|workdir\.py)\..+$")
TASK_DIRS = ("work", "data", "_closed")
DATA_EXT = {".csv", ".tsv", ".xls", ".xlsx", ".xlsm", ".parquet", ".feather", ".jsonl",
            ".ndjson", ".db", ".sqlite", ".sqlite3", ".duckdb"}
SKIP = {".git", "node_modules", "__pycache__", ".venv"}
LIST_CAP = 200


def root_dir():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def context(root):
    """Project Context values from the twin's CLAUDE.md, e.g. {'prefix': 'sw', ...}."""
    try:
        text = (root / "CLAUDE.md").read_text(encoding="utf-8")
    except OSError:
        return {}
    m = re.search(r"^## [^\n]*Project Context[ \t]*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return dict(re.findall(r"^(domain|project|prefix):\s*(\S+)\s*$", m.group(1), re.M)) if m else {}


def task_pattern(prefix):
    p = re.escape(prefix) if prefix and prefix != "none" else "[a-z]{2,3}"
    return re.compile(rf"^{p}-[a-z0-9]+(-[a-z0-9]+)*$")


def hosted(root, rel_parts):
    """True when a folder between root and the file has its own CLAUDE.md."""
    d = root
    for part in rel_parts[:-1]:
        d = d / part
        if (d / "CLAUDE.md").is_file():
            return True
    return False


# ───────────────────────── guard ─────────────────────────
def block(msg):
    sys.stderr.write(f"Working folder (S12): {msg}\n")
    return 2


def guard():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return block("hook input unreadable, write refused")
    ti = data.get("tool_input") or {}
    raw = ti.get("file_path") or ti.get("notebook_path")
    if not raw:
        return 0
    root = root_dir()
    p = Path(raw)
    if not p.is_absolute():
        p = Path(data.get("cwd") or os.getcwd()) / p
    p = Path(os.path.realpath(p))
    try:
        rel = p.relative_to(root).parts
    except ValueError:
        return 0  # outside this project: its own rules apply
    if not rel:
        return 0
    if rel == ("CLAUDE.md",) or rel[0] == ".claude":
        return 0  # settings, handed over by bandit:project
    if hosted(root, rel):
        return 0
    top, ext = rel[0], p.suffix.lower()
    pat = task_pattern(context(root).get("prefix"))
    if top in ("work", "data"):
        if len(rel) < 3:
            return block(f"no loose files in {top}/: use {top}/{{prefix}}-{{task}}/ (task = the board task's title, kebab-case)")
        if not pat.match(rel[1]):
            return block(f"`{top}/{rel[1]}/` isn't {{prefix}}-{{task}} (pattern {pat.pattern})")
        if top == "work" and ext in DATA_EXT:
            return block(f"{ext} is a data file: write it to data/{rel[1]}/")
        return 0
    if top == "scratch":
        if len(rel) < 2:
            return 0
        if ext in DATA_EXT:
            return block(f"{ext} is a data file: write it to data/{{prefix}}-{{task}}/, never scratch/")
        return 0
    if top == "_closed":
        return block("_closed/ is filled only by `/bandit:tasks done` (a move), never written")
    if top == "_backup":
        if len(rel) != 2 or not BACKUP_NAME.match(rel[1]) or ext in DATA_EXT:
            return block("_backup/ holds settings rollback copies only, flat: CLAUDE.md.{version}, "
                         "settings.json.{version}, workdir.py.{version}. Superseded work goes in "
                         "work/{prefix}-{task}/superseded/")
        return 0
    if top == "repos":
        return block("repos/ holds read-only clones")
    return block(f"`{rel[0]}` is outside the layout: work/{{prefix}}-{{task}}/, data/{{prefix}}-{{task}}/ or scratch/")


# ───────────────────────── manifest ─────────────────────────
def day(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).date().isoformat()


def walk_files(d):
    for dirpath, dirnames, filenames in os.walk(d):
        dirnames[:] = sorted(x for x in dirnames if x not in SKIP)
        for f in sorted(filenames):
            yield Path(dirpath) / f


def manifest():
    root = root_dir()
    ctx = context(root)
    m = {"schema": 1, "generated_at": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
         "domain": ctx.get("domain"), "project": ctx.get("project"), "prefix": ctx.get("prefix"),
         "root": [], "hosted": [], "task_folders": {k: [] for k in TASK_DIRS},
         "loose": [], "scratch": [], "misplaced_data": [], "backup": [], "truncated": False}

    def add(lst, item):
        if len(lst) >= LIST_CAP:
            m["truncated"] = True
        else:
            lst.append(item)

    for e in sorted(root.iterdir(), key=lambda x: x.name):
        if e.is_dir() and (e / "CLAUDE.md").is_file() and e.name not in ROOT_ALLOWED:
            m["hosted"].append(e.name)
            continue
        m["root"].append({"name": e.name, "dir": e.is_dir()})
        if e.is_file() and e.name not in ROOT_ALLOWED:
            if e.suffix.lower() in DATA_EXT:
                add(m["misplaced_data"], {"dir": ".", "ext": e.suffix.lower(), "modified": day(e.stat().st_mtime)})
            continue
        if not e.is_dir() or e.name in ROOT_ALLOWED:
            continue
        for f in walk_files(e):  # a folder outside the layout: report data files in it
            if f.suffix.lower() in DATA_EXT:
                add(m["misplaced_data"], {"dir": str(f.parent.relative_to(root)), "ext": f.suffix.lower(),
                                          "modified": day(f.stat().st_mtime)})

    for top in TASK_DIRS:
        d = root / top
        if not d.is_dir():
            continue
        for e in sorted(d.iterdir(), key=lambda x: x.name):
            if e.is_file():
                item = {"path": f"{top}/{e.name}", "modified": day(e.stat().st_mtime)}
                if top == "data":  # never a file name from data/
                    item = {"path": "data/", "ext": e.suffix.lower(), "modified": item["modified"]}
                add(m["loose"], item)
                continue
            files = list(walk_files(e))
            if top == "_closed":  # closing touches the folder: its own date is the close date
                mod = day(e.stat().st_mtime)
            else:
                mod = max((day(f.stat().st_mtime) for f in files), default=day(e.stat().st_mtime))
            m["task_folders"][top].append({"name": e.name, "modified": mod, "files": len(files)})
            if top == "work":
                for f in files:
                    if f.suffix.lower() in DATA_EXT:
                        add(m["misplaced_data"], {"dir": str(f.parent.relative_to(root)), "ext": f.suffix.lower(),
                                                  "modified": day(f.stat().st_mtime)})
    bd = root / "_backup"
    if bd.is_dir():
        for e in sorted(bd.iterdir(), key=lambda x: x.name):
            ok = e.is_file() and bool(BACKUP_NAME.match(e.name)) and e.suffix.lower() not in DATA_EXT
            data = e.is_file() and e.suffix.lower() in DATA_EXT  # never a data file's name
            add(m["backup"], {"name": f"(a {e.suffix.lower()} file)" if data else e.name,
                              "dir": e.is_dir(), "ok": ok, "modified": day(e.stat().st_mtime)})
    sd = root / "scratch"
    if sd.is_dir():
        for f in walk_files(sd):
            add(m["scratch"], {"path": str(f.relative_to(root)), "modified": day(f.stat().st_mtime)})
            if f.suffix.lower() in DATA_EXT:
                add(m["misplaced_data"], {"dir": str(f.parent.relative_to(root)), "ext": f.suffix.lower(),
                                          "modified": day(f.stat().st_mtime)})

    cdir = root / ".claude"
    cdir.mkdir(exist_ok=True)
    (cdir / "workdir-manifest.json").write_text(json.dumps(m, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    stray = [r["name"] for r in m["root"] if r["name"] not in ROOT_ALLOWED]
    print(f"Working folder (S12): {len(stray)} outside the layout, {len(m['loose'])} loose, "
          f"{len(m['misplaced_data'])} data file(s) outside data/. Details: .claude/workdir-manifest.json")
    stamp = cdir / "workdir-manifest.requested"
    today = m["generated_at"]
    try:
        last = stamp.read_text().strip()
    except OSError:
        last = ""
    if last != today and m["domain"] and m["project"]:
        stamp.write_text(today + "\n")
        print(f"Upload .claude/workdir-manifest.json, as-is, to MyNotes/{m['domain']}/Projects/{m['project']}/"
              f"workdir-manifest.json through BanditCloud (new file: omit if_match; existing: its bare-hex etag). "
              f"It feeds /bandit:audit S12. One line to the user when done, nothing else.")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        sys.exit(guard() if mode == "guard" else manifest() if mode == "manifest" else block(f"unknown mode `{mode}`"))
    except Exception as e:  # fail closed on the guard, never crash the session start
        if mode == "guard":
            sys.exit(block(f"guard failed ({e.__class__.__name__}: {e}), write refused"))
        print(f"Working folder (S12): manifest failed ({e.__class__.__name__}: {e})")
        sys.exit(0)
