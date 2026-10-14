#!/usr/bin/env python3
"""House lint: check a skill folder against the house rulebook (references/rulebook.md).

Usage:
    python -m scripts.house_lint <skill-folder> [<skill-folder> ...] [--names FILE ...]

Exit 0 = ships (warnings allowed) · 1 = blocked: a must breaks, or R7 (the size gate).
package_skill.py runs this first and refuses to build a blocked skill.
Checks only what code can check. Judgment rules (R2 trigger quality, R4 one owner,
R6 obvious content, R8 railroading, R12 findings, R13 homes, R14 overwrites) stay with
review in bandit-maker:skill.

R15 (unique command names) compares the skill against every other skill in the marketplace
repo (`plugins/*/skills/*` with a SKILL.md, found from the skill's own path), or, outside the
repo, every sibling skill folder. Commands are written `/plugin:skill command` (or the bare
`/skill command`). --names adds files whose bare `/name` commands also count as taken
(e.g. the cheat sheet).
"""
import re
import sys
from pathlib import Path

import yaml

MAX_LINES = 500          # R7: a gate at build, not just a score
DESC_HARD = 1024         # R1: the save limit
DESC_WARN = 1000         # R1: the next edit will break it
UUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)
EMOJI_H2 = re.compile(r"^## [^\w\s`*]", re.M)
SKILL_CMD = re.compile(r"`/([a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)?) ([a-z][a-z0-9-]*)")  # `/plugin:skill command
BARE_CMD = re.compile(r"`/([a-z][a-z0-9-]*)`")                     # `/command` alone


def _texts(folder):
    for f in sorted(Path(folder).rglob("*.md")):
        if f.is_file():
            yield f, f.read_text(errors="ignore")


def _commands(folder):
    """(skill commands {word: skill}, bare commands {word: file}) named in a skill's .md files."""
    folder = Path(folder)
    skill_cmds, bare = {}, {}
    for f, text in _texts(folder):
        for skill, word in SKILL_CMD.findall(text):
            if skill.split(":")[-1] == folder.name:
                skill_cmds.setdefault(word, skill)
        for word in BARE_CMD.findall(text):
            bare.setdefault(word, f.relative_to(folder).as_posix())
    return skill_cmds, bare


def sibling_skills(folder):
    """Every other skill folder: the marketplace repo's plugins/*/skills/*, else the folder's siblings."""
    me = Path(folder).resolve()
    for up in me.parents:
        if up.name == "plugins" and up.is_dir():
            found = sorted(up.glob("*/skills/*/SKILL.md"))
            return [s.parent for s in found if s.parent.resolve() != me]
    return [p for p in sorted(me.parent.iterdir())
            if p.is_dir() and p.resolve() != me and (p / "SKILL.md").exists()]


def check_r15(folder, others=None, names=()):
    """R15 · no bare `/name` command reuses a skill's command word (e.g. `/triage` vs `/bandit:tasks triage`)."""
    folder = Path(folder)
    if others is None:
        others = sibling_skills(folder)
    skills = {folder.name} | {Path(o).name for o in others}
    own_cmds, own_bare = _commands(folder)
    taken = {}  # word -> "/skill word"
    for o in [folder, *others]:
        for word, skill in _commands(o)[0].items():
            taken.setdefault(word, f"/{skill} {word}")
    bare = {w: f"{folder.name}/{where}" for w, where in own_bare.items()}
    extra = {}  # bare commands named outside this skill: they clash only with this skill's words
    for o in others:
        for word, where in _commands(o)[1].items():
            extra.setdefault(word, f"{Path(o).name}/{where}")
    for n in names:
        for word in BARE_CMD.findall(Path(n).read_text(errors="ignore")):
            extra.setdefault(word, Path(n).name)
    clashes = [f"`/{w}` ({where}) reuses {taken[w]}"
               for w, where in bare.items() if w in taken and w not in skills]
    clashes += [f"`/{w}` ({where}) reuses /{folder.name} {w}"
                for w, where in extra.items() if w in own_cmds and w not in skills and w not in bare]
    if clashes:
        return [("R15", "fail", "; ".join(clashes[:5]))]
    return [("R15", "ok", f"command names unique against {len(others)} sibling skill(s)")]


def lint(folder, others=None, names=()):
    folder = Path(folder)
    out = []  # (rule, level, message)  level: fail | warn | ok
    md = folder / "SKILL.md"
    if not md.exists():
        return [("R1", "fail", "SKILL.md missing")]
    text = md.read_text()
    parts = text.split("---", 2)
    try:
        fm = yaml.safe_load(parts[1]) if len(parts) > 2 else None
    except yaml.YAMLError as e:
        return [("R1", "fail", f"frontmatter is not valid YAML: {e}")]
    if not isinstance(fm, dict):
        return [("R1", "fail", "no frontmatter")]

    # R1 · frontmatter
    name, desc = fm.get("name"), (fm.get("description") or "").strip()
    if name != folder.name:
        out.append(("R1", "fail", f"name `{name}` ≠ folder `{folder.name}`"))
    if len(desc) > DESC_HARD:
        out.append(("R1", "fail", f"description {len(desc)} chars > {DESC_HARD}"))
    elif len(desc) > DESC_WARN:
        out.append(("R1", "warn", f"description {len(desc)} chars > {DESC_WARN}: the next edit breaks the limit"))
    else:
        out.append(("R1", "ok", f"description {len(desc)} chars"))

    # R3 · gotchas: the section exists, every line has both halves
    m = re.search(r"^## ⚠️ Gotchas\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        out.append(("R3", "fail", "no `## ⚠️ Gotchas` section"))
    else:
        body = m.group(1)
        items = re.findall(r"^- .*?(?=^- |\Z)", body, re.M | re.S)
        halves = [i for i in items if "→" not in i and "None logged yet" not in i]
        pointer = "references/gotchas.md" in body
        if not items and "None logged yet" not in body and not pointer:
            out.append(("R3", "fail", "Gotchas section is empty (write `None logged yet.`)"))
        elif halves:
            out.append(("R3", "fail", f"{len(halves)} gotcha line(s) without `→ what to do instead`"))
        else:
            out.append(("R3", "ok", f"{len(items)} gotcha line(s)"))
        if len(items) > 15 and not pointer:
            out.append(("R3", "warn", f"{len(items)} gotchas: move them to references/gotchas.md"))

    # R7 · size gate
    lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    if lines > MAX_LINES:
        out.append(("R7", "fail", f"SKILL.md {lines} lines > {MAX_LINES}: move detail to references/"))
    else:
        out.append(("R7", "ok", f"SKILL.md {lines} lines"))

    # R10 · no hardcoded IDs anywhere in the skill's text files
    hits = []
    for f in sorted(folder.rglob("*")):
        if f.is_file() and f.suffix in (".md", ".py", ".json", ".yaml", ".yml"):
            for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
                if UUID.search(line):
                    hits.append(f"{f.relative_to(folder)}:{n}")
    out.append(("R10", "warn" if hits else "ok",
                f"possible hardcoded IDs: {', '.join(hits[:5])}" if hits else "no IDs"))

    # R11 · house format
    if not EMOJI_H2.search(text):
        out.append(("R11", "warn", "no emoji-anchored H2"))
    if not re.search(r"^## .*(Never|NOT|Outside|🚫)", text, re.M):
        out.append(("R11", "warn", "no Never / limits section"))
    if not any(r == "R11" for r, _, _ in out):
        out.append(("R11", "ok", "emoji H2s, Never section"))

    # R15 · unique command names
    out += check_r15(folder, others, names)
    return out


def main(argv):
    names = []
    while "--names" in argv:
        i = argv.index("--names")
        names.append(argv[i + 1])
        del argv[i:i + 2]
    if not argv:
        print(__doc__)
        return 2
    blocked = False
    for folder in argv:
        res = lint(folder, names=names)
        print(f"── {Path(folder).name}")
        for rule, level, msg in res:
            mark = {"ok": "✅", "warn": "⚠️", "fail": "❌"}[level]
            print(f"  {mark} {rule} {msg}")
        if any(level == "fail" for _, level, _ in res):
            blocked = True
    print("BLOCKED: fix the ❌ lines before shipping." if blocked else "OK to ship.")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
