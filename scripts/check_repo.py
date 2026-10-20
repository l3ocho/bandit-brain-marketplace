#!/usr/bin/env python3
"""Repo checker for bandit-brain-marketplace: rules as code (D19).

Usage:
    python3 scripts/check_repo.py            # every rule
    python3 scripts/check_repo.py --no-cli   # skip `claude plugin validate` (no Claude Code on PATH)

Exit 0 = green · 1 = a rule failed. Each rule prints one line; the last line is the verdict.
Rule homes and reasons: docs/decisions.md.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
SETTINGS = ROOT / ".claude" / "settings.json"
CHANGELOG = ROOT / "CHANGELOG.md"
# Plugins whose skills must be denied in the build session (G6). bandit-maker is the build tool.
G6_PLUGINS = ("bandit", "bandit-dev")

results = []  # (rule, ok, message)


def report(rule, ok, msg):
    results.append((rule, ok, msg))


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as e:
        return None, str(e)


def plugin_dirs():
    return sorted(p for p in PLUGINS.iterdir() if p.is_dir()) if PLUGINS.is_dir() else []


def skill_dirs(plugin):
    base = plugin / "skills"
    return sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []


# ── M1 · manifests are valid JSON and agree with each other ──────────────────────────────
def check_manifests():
    market, err = load_json(MARKETPLACE)
    if err:
        return report("M1", False, f"marketplace.json: {err}")
    bad = []
    listed = {p.get("name"): p.get("source") for p in market.get("plugins", [])}
    found = {p.name for p in plugin_dirs()}
    for name, source in listed.items():
        if source != f"./plugins/{name}":
            bad.append(f"{name}: source {source!r} ≠ ./plugins/{name}")
    if set(listed) != found:
        bad.append(f"listed {sorted(listed)} ≠ folders {sorted(found)}")
    for p in plugin_dirs():
        manifest, err = load_json(p / ".claude-plugin" / "plugin.json")
        if err:
            bad.append(f"{p.name}/plugin.json: {err}")
        elif manifest.get("name") != p.name:
            bad.append(f"{p.name}/plugin.json name {manifest.get('name')!r}")
        hooks = p / "hooks" / "hooks.json"
        if hooks.exists():
            data, err = load_json(hooks)
            if err or "hooks" not in (data or {}):
                bad.append(f"{p.name}/hooks/hooks.json: {err or 'no top-level hooks key'}")
    for extra in (SETTINGS,):
        if extra.exists() and load_json(extra)[1]:
            bad.append(f"{extra.relative_to(ROOT)}: {load_json(extra)[1]}")
    report("M1", not bad, "; ".join(bad) or f"manifests valid ({len(found)} plugins)")


# ── M2 · `claude plugin validate` passes for the marketplace and each plugin ─────────────
def check_validate(use_cli):
    if not use_cli:
        return report("M2", True, "skipped (--no-cli)")
    if not shutil.which("claude"):
        return report("M2", False, "claude CLI not on PATH (run with --no-cli to skip)")
    bad = []
    for target in [ROOT, *plugin_dirs()]:
        r = subprocess.run(["claude", "plugin", "validate", str(target)],
                           capture_output=True, text=True, timeout=180)
        out = (r.stdout + r.stderr).strip()
        if r.returncode != 0 or "Validation passed" not in out:
            bad.append(f"{target.name}: {out.splitlines()[-1] if out else r.returncode}")
    report("M2", not bad, "; ".join(bad) or f"claude plugin validate OK ×{len(plugin_dirs()) + 1}")


# ── L7 · no top-level bin/ in any plugin (it blocks the whole plugin on Claude.ai) ───────
def check_no_bin():
    hits = [p.name for p in plugin_dirs() if (p / "bin").exists()]
    report("L7", not hits, f"bin/ at plugin root: {', '.join(hits)}" if hits else "no bin/ at any plugin root")


# ── V1 · plugin versions match the top CHANGELOG entry (`Unreleased` allowed until release)
def check_versions():
    try:
        text = CHANGELOG.read_text(encoding="utf-8")
    except OSError:
        return report("V1", False, "CHANGELOG.md missing")
    m = re.search(r"^## (\S+)", text, re.M)
    if not m:
        return report("V1", False, "CHANGELOG.md has no `## ` entry")
    top = m.group(1)
    versions = {}
    for p in plugin_dirs():
        manifest, _ = load_json(p / ".claude-plugin" / "plugin.json")
        versions[p.name] = (manifest or {}).get("version")
    market, _ = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    versions["marketplace"] = ((market or {}).get("metadata") or {}).get("version")
    if top == "Unreleased":
        same = len(set(versions.values())) == 1
        return report("V1", same, f"top entry Unreleased; versions {versions}")
    bad = {k: v for k, v in versions.items() if v != top}
    report("V1", not bad, f"versions ≠ CHANGELOG {top}: {bad}" if bad else f"all plugins and the marketplace at {top} = CHANGELOG")


# ── V2 · every released CHANGELOG entry has its annotated tag vX.Y.Z, and the tag carries that version
def check_tags():
    released = re.findall(r"^## (\d+\.\d+\.\d+) ", CHANGELOG.read_text(encoding="utf-8"), re.M)
    if not shutil.which("git") or subprocess.run(["git", "rev-parse"], cwd=ROOT, capture_output=True).returncode:
        return report("V2", True, "skipped (not a git checkout)")
    tags = set(subprocess.run(["git", "tag", "-l", "v*"], cwd=ROOT, capture_output=True, text=True).stdout.split())
    current = (load_json(PLUGINS / "bandit" / ".claude-plugin" / "plugin.json")[0] or {}).get("version")
    bad = []
    for v in released:
        tag = f"v{v}"
        if tag not in tags:
            if v != current:  # the entry being released right now is tagged after this commit
                bad.append(f"{tag} missing")
            continue
        kind = subprocess.run(["git", "cat-file", "-t", tag], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        shown = subprocess.run(["git", "show", f"{tag}:plugins/bandit/.claude-plugin/plugin.json"],
                               cwd=ROOT, capture_output=True, text=True).stdout
        if kind != "tag":
            bad.append(f"{tag} is not annotated")
        if f'"version": "{v}"' not in shown:
            bad.append(f"{tag} does not carry version {v}")
    report("V2", not bad, "; ".join(bad) or f"{len(released)} released versions, each with its annotated tag")


# ── G6 · every skill in bandit and bandit-dev has a Skill() deny rule in .claude/settings.json
def check_g6():
    settings, err = load_json(SETTINGS)
    if err:
        return report("G6", False, f".claude/settings.json: {err}")
    deny = set(settings.get("permissions", {}).get("deny", []))
    missing = []
    count = 0
    for plugin in G6_PLUGINS:
        for s in skill_dirs(PLUGINS / plugin):
            count += 1
            if f"Skill({plugin}:{s.name})" not in deny:
                missing.append(f"Skill({plugin}:{s.name})")
    report("G6", not missing, f"no deny rule for {', '.join(missing)}" if missing
           else f"deny rules cover {count} skill(s) in {', '.join(G6_PLUGINS)}")


# ── D1 · no old skill name or retired string anywhere we ship or document ─────────────────
DENYLIST = ("bandit-tasks", "bandit-notes", "bandit-audit", "bandit-sprint", "project-settings",
            "text-rewriter", "project-planner", "wbs-generator", "meeting-minutes", "myskill-creator",
            "MyNotes/_skills", "Skill Manager", "mktpl-claude-datasaas", "projman")
# The one place allowed to name them: the history tables of docs/decisions.md, fenced by markers.
HISTORY_FILE = ROOT / "docs" / "decisions.md"
HISTORY_OFF, HISTORY_ON = "<!-- denylist:off -->", "<!-- denylist:on -->"
TEXT_SUFFIXES = (".md", ".py", ".json", ".yaml", ".yml", ".html", ".txt", ".sh")


def shipped_files():
    """plugins/, docs/, templates/, tests/ and the root files; never .work/, .git/ or scripts/."""
    files = [p for p in ROOT.iterdir() if p.is_file() and not p.name.startswith(".")]
    for sub in ("plugins", "docs", "templates", "tests"):
        base = ROOT / sub
        if base.is_dir():
            files += [p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    return sorted(f for f in files if f.suffix in TEXT_SUFFIXES or f.name in ("LICENSE",))


def strip_history(path, text):
    if HISTORY_OFF not in text:
        return text, None
    if path != HISTORY_FILE:
        return text, f"{path.relative_to(ROOT)}: denylist markers are allowed only in docs/decisions.md"
    return re.sub(re.escape(HISTORY_OFF) + r".*?" + re.escape(HISTORY_ON), "", text, flags=re.S), None


def check_denylist():
    hits = []
    for f in shipped_files():
        text, err = strip_history(f, f.read_text(encoding="utf-8", errors="ignore"))
        if err:
            hits.append(err)
        for n, line in enumerate(text.splitlines(), 1):
            for word in DENYLIST:
                if word in line:
                    hits.append(f"{f.relative_to(ROOT)}:{n} `{word}`")
    report("D1", not hits, f"old names: {'; '.join(hits[:8])}{' …' if len(hits) > 8 else ''} ({len(hits)})"
           if hits else f"no old name in {len(shipped_files())} shipped files")


# ── MT1 · no Bandit Brain assistant tool the app removed: a skill calling one answers NOT_FOUND ─
# The app's own list (its src/domains/tasks/removedTools.ts); the 18 tools that replace them are in
# its docs/handoff/mcp-tool-rename-for-skills.md. Whole words, so update_tasks never matches update_task.
REMOVED_TOOLS = (
    "list_projects list_folders list_tags list_household_members list_project_members get_lane_template "
    "list_sprints get_execution_board get_week_board get_inbox_board get_workload create_task "
    "create_recurring_task update_task complete_task complete_by_origin move_task set_task_execution_state "
    "set_task_due_date set_task_tags bulk_move_tasks bulk_set_due_date bulk_set_execution_state "
    "bulk_complete_tasks bulk_set_task_tags uncomplete_task delete_task delete_subtask remove_dependency "
    "delete_series delete_series_occurrence add_subtask rename_subtask set_subtask_completed reorder_subtasks "
    "promote_subtask attach_repeat_rule get_repeat_rule update_repeat_rule end_repeat_rule set_series_assignee "
    "skip_occurrence list_occurrences add_dependency create_project update_project archive_project "
    "restore_project add_project_column rename_project_column reorder_project_columns set_project_lanes "
    "create_tag update_tag promote_tag create_folder update_folder set_project_visibility delete_project "
    "delete_project_column delete_tag delete_folder").split()
REMOVED_TOOLS_RE = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(REMOVED_TOOLS) + r")(?![A-Za-z0-9_])")


def check_removed_tools():
    hits = []
    for f in shipped_files():
        text, _ = strip_history(f, f.read_text(encoding="utf-8", errors="ignore"))
        for n, line in enumerate(text.splitlines(), 1):
            line = line.replace('action: "list_occurrences"', "")  # manage_recurrence's own action
            for m in REMOVED_TOOLS_RE.finditer(line):
                hits.append(f"{f.relative_to(ROOT)}:{n} `{m.group(1)}`")
    report("MT1", not hits,
           f"removed tools: {'; '.join(hits[:8])}{' …' if len(hits) > 8 else ''} ({len(hits)})" if hits
           else f"no removed assistant tool in {len(shipped_files())} shipped files ({len(REMOVED_TOOLS)} names)")


# ── R15 · command words are unique across every skill (house_lint's rule, one source) ────
def house_lint():
    import importlib.util
    path = PLUGINS / "bandit-maker" / "skills" / "skill" / "scripts" / "house_lint.py"
    spec = importlib.util.spec_from_file_location("house_lint", path)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod


def all_skills():
    return [s for p in plugin_dirs() for s in skill_dirs(p) if (s / "SKILL.md").exists()]


def check_r15():
    lint = house_lint()
    bad = []
    for s in all_skills():
        for rule, level, msg in lint.check_r15(s):
            if level == "fail":
                bad.append(f"{s.name}: {msg}")
    report("R15", not bad, "; ".join(bad) or f"command words unique across {len(all_skills())} skills")


# ── X1 · the audit rules pin the exact working-folder guard the project skill hands out ───
def check_guard_pin():
    rules = PLUGINS / "bandit" / "skills" / "audit" / "references" / "structure-rules.yaml"
    guard = PLUGINS / "bandit" / "skills" / "project" / "scripts" / "workdir.py"
    if not rules.exists() or not guard.exists():
        return report("X1", True, "skipped (audit rules or guard not present)")
    import hashlib
    m = re.search(r"hook_sha12:\s*([0-9a-f]{12})", rules.read_text(encoding="utf-8"))
    actual = hashlib.sha256(guard.read_bytes()).hexdigest()[:12]
    ok = bool(m) and m.group(1) == actual
    report("X1", ok, f"s12.hook_sha12 = workdir.py sha12 ({actual})" if ok
           else f"s12.hook_sha12 {m.group(1) if m else 'missing'} ≠ workdir.py sha12 {actual}")


# ── L1 · description ≤ 300 characters, at most one "not for" clause ──────────────────────
DESC_MAX = 300
CORE_DESC_TOTAL = 2400


def frontmatter(skill):
    import yaml
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return (yaml.safe_load(parts[1]) or {}) if len(parts) > 2 else {}, text


def check_l1():
    bad, core = [], 0
    for s in all_skills():
        desc = str(frontmatter(s)[0].get("description") or "").strip()
        nots = len(re.findall(r"\b(do not|not for)\b", desc, re.I))
        if len(desc) > DESC_MAX:
            bad.append(f"{s.name} {len(desc)} chars")
        if nots > 1:
            bad.append(f"{s.name} {nots} not-for clauses")
        if s.parent.parent.name == "bandit":
            core += len(desc)
    if core > CORE_DESC_TOTAL:
        bad.append(f"core total {core} > {CORE_DESC_TOTAL}")
    report("L1", not bad, "; ".join(bad) or f"every description ≤ {DESC_MAX}; core total {core} ≤ {CORE_DESC_TOTAL}")


# ── L2 · SKILL.md ≤ 150 lines, with a router table pointing at references/ ───────────────
SKILL_MAX_LINES = 150


def check_l2():
    bad = []
    for s in all_skills():
        text = (s / "SKILL.md").read_text(encoding="utf-8")
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        if lines > SKILL_MAX_LINES:
            bad.append(f"{s.name} {lines} lines")
        known = {p.name for k in all_skills() for p in (k / "references").glob("*.md")}
        for ref in set(re.findall(r"`references/([\w.-]+\.md)`", text)):
            if ref not in known:  # a pointer may name another skill's reference file
                bad.append(f"{s.name} points to missing references/{ref}")
        if not re.search(r"^\|.*`references/[\w.-]+\.md`.*\|", text, re.M):
            bad.append(f"{s.name} has no router row pointing to references/")
    report("L2", not bad, "; ".join(bad) or f"every SKILL.md ≤ {SKILL_MAX_LINES} lines with a router")


# ── L8 · no person in shipped files: the plugins serve every member, so no owner's name and no he/his/him ──
L8_TERMS = re.compile(r"\b(Leo|Rachel|Matteo)\b|\b(he|his|him|himself)\b", re.I)


def check_l8():
    hits = []
    for f in sorted(PLUGINS.rglob("*")):
        if not f.is_file() or f.suffix not in TEXT_SUFFIXES or "__pycache__" in f.parts:
            continue
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            m = L8_TERMS.search(line)
            if m:
                hits.append(f"{f.relative_to(PLUGINS)}:{n} `{m.group(0)}`")
    report("L8", not hits, f"a person in shipped files (say \"the user\", they/them): {'; '.join(hits[:8])}"
           f"{' …' if len(hits) > 8 else ''} ({len(hits)})" if hits else "no person's name or he/his/him in any plugin file")


# ── T1 · talking to the user: no numbered rows or option codes where skills ask and decide ──
T1_FILES = ["bandit-dev/skills/sprint", "bandit/skills/clarify", "bandit/skills/tasks/references/dev-workflow.md"]
T1_TERMS = re.compile(r"numbered (fix )?rows?\b|numbered options|numbered lists so", re.I)


def check_t1():
    hits = []
    for root in T1_FILES:
        p = PLUGINS / root
        for f in sorted([p] if p.is_file() else p.rglob("*.md")):
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if T1_TERMS.search(line) and "no numbers" not in line and "numbered fix rows)" not in line:
                    hits.append(f"{f.relative_to(PLUGINS)}:{n}")
    report("T1", not hits, f"numbered rows where the user decides (use the decision table): {'; '.join(hits)}"
           if hits else "sprint, clarify and spec ask in the plain decision table, no numbered rows")


# ── L4 · no project details in skills: project names, stack tools, card ids, UUIDs ───────
L4_TERMS = re.compile(
    r"\b(BanditLabs|Summitt|cs-notes|CS Notes|bandit-labs|banditbrain|BanditBrains|drizzle|npm|npx)\b"
    r"|\b(?!WBS-|UTF-|SHA-)[A-Z]{2,4}-\d+\b"
    r"|\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
# The house standards are data the owner approves, not skill procedure: their examples stay.
L4_EXEMPT = {"structure-rulebook.md", "structure-rules.yaml", "rulebook.md"}


def check_l4():
    hits = []
    for s in all_skills():
        for f in sorted(s.rglob("*")):
            if not f.is_file() or f.suffix not in TEXT_SUFFIXES or f.name in L4_EXEMPT or "__pycache__" in f.parts:
                continue
            for n, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                m = L4_TERMS.search(line)
                if m:
                    hits.append(f"{f.relative_to(PLUGINS)}:{n} `{m.group(0)}`")
    report("L4", not hits, f"project details: {'; '.join(hits[:8])}{' …' if len(hits) > 8 else ''} ({len(hits)})"
           if hits else "no project names, stack tools, card ids or UUIDs in any skill")


# ── H1 · house lint passes on every skill (the rulebook's code gate) ──────────────────────
def check_house_lint():
    lint = house_lint()
    bad = []
    for s in all_skills():
        for rule, level, msg in lint.lint(s):
            if level == "fail":
                bad.append(f"{s.name} {rule}: {msg}")
    report("H1", not bad, "; ".join(bad) or f"house lint OK on {len(all_skills())} skills")


# ── A1 · the shipped audit rules pass the scorer's own contract (rules ↔ rulebook in step) ─
def check_audit_contract():
    import importlib.util
    base = PLUGINS / "bandit" / "skills" / "audit"
    script = base / "scripts" / "check_structure.py"
    if not script.exists():
        return report("A1", True, "skipped (no audit scorer)")
    spec = importlib.util.spec_from_file_location("check_structure", script)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    try:
        rules, sha = mod.load_rules(base / "references" / "structure-rules.yaml",
                                    base / "references" / "structure-rulebook.md")
    except Exception as e:  # ContractError or a YAML error: either way the scorer would refuse
        return report("A1", False, f"audit rules refused by check_structure.py: {e}")
    ok = bool(rules.get("paths", {}).get("stamps"))
    report("A1", ok, f"audit rules load (sha {sha}, rulebook {rules['rulebook_updated']}), paths.stamps set"
           if ok else "audit rules: paths.stamps missing")


# ── SP7 · the sprint checker refuses a committed sprint without its plan review (fixtures) ─
def run_script(script, *args, cwd=None):
    r = subprocess.run([sys.executable, "-B", str(script), *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr).strip()


def check_sp7():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "check_sprint.py"
    vault = ROOT / "tests" / "fixture-vault"
    good = run_script(script, "--vault", str(vault), "--domain", "Good")
    bad = run_script(script, "--vault", str(vault), "--domain", "Bad")
    ok = good[0] == 0 and bad[0] == 1 and "SP7" in bad[1] and bad[1].count("\n- ") == 1
    report("SP7", ok, "check_sprint passes the reviewed sprint and refuses the unreviewed one with SP7 only"
           if ok else f"fixtures: good → {good[0]} {good[1][-120:]!r}; bad → {bad[0]} {bad[1][-160:]!r}")


# ── SP8 · the Stop hook blocks only on the session's own projects (fixtures) ─────────────
def check_sp8():
    import tempfile
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "check_sprint.py"
    vault = ROOT / "tests" / "fixture-vault"
    got = {}
    with tempfile.TemporaryDirectory() as d:
        for name, body in (("own", "MyNotes/Bad/Projects/home-reno/sprint-one/x.md"),
                           ("other", "MyNotes/Bad/Projects/other-app/sprint-a/x.md")):
            t = Path(d) / f"{name}.jsonl"
            t.write_text(body + " bandit-dev:sprint\n", encoding="utf-8")
            r = subprocess.run([sys.executable, "-B", str(script), "--hook", "--vault", str(vault), "--domain", "Bad"],
                               input=json.dumps({"transcript_path": str(t)}), capture_output=True, text=True)
            got[name] = (r.returncode, r.stdout + r.stderr)
    ok = got["own"][0] == 2 and got["other"][0] == 0 and "systemMessage" in got["other"][1]
    report("SP8", ok, "hook blocks on the session's own project, warns (exit 0) on another's"
           if ok else f"own → {got['own'][0]}, other → {got['other'][0]} {got['other'][1][-120:]!r}")


# ── Y1 · the recipe reader refuses a missing key and a wrong migration tail (fixtures) ────
def check_recipe():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "recipe.py"
    app = ROOT / "tests" / "fixture-app"
    cases = [
        (("require", "verify", "branches.trunk", "branches.deploy", "release", "migrations.dir",
          "migrations.check", "staging.refresh"), 0, "present"),
        (("check-tail", "0002"), 0, "matches"),
        (("check-tail", "0003"), 4, "the plan names 0003"),
        (("--file", "bandit.missing-key.yaml", "check-tail", "0002"), 3, "missing key `migrations.check`"),
        (("--file", "bandit.no-migrations.yaml", "tail"), 0, "none"),
        (("--file", "bandit.no-migrations.yaml", "check-tail", "none"), 0, "matches"),
        (("--file", "bandit.no-migrations.yaml", "opt", "staging.refresh"), 0, "none"),
        (("opt", "staging.refresh"), 0, "echo staging refresh"),
    ]
    bad = []
    for args, code, text in cases:
        got, out = run_script(script, *args, cwd=app)
        if got != code or text not in out:
            bad.append(f"{' '.join(args)} → {got} {out[-100:]!r}")
    report("Y1", not bad, "; ".join(bad) or f"recipe.py: {len(cases)} fixture cases (keys, tail, refusal by name, optional sections)")


# ── TD1 · the testdata guard refuses every unsafe database and removes only what it created (fixtures) ─
def check_testdata():
    import shutil as sh
    import tempfile
    recipe_py = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "recipe.py"
    guard = PLUGINS / "bandit-dev" / "skills" / "testdata" / "scripts" / "dbguard.py"
    skill = PLUGINS / "bandit-dev" / "skills" / "testdata"
    missing = [n for n in ("SKILL.md", "references/map.md", "references/fill.md", "references/make.md",
                           "references/create.md", "references/safety.md") if not (skill / n).exists()]
    if missing or not guard.exists():
        return report("TD1", False, f"testdata skill files missing: {', '.join(missing) or 'scripts/dbguard.py'}")
    bad = []
    with tempfile.TemporaryDirectory() as d:
        app = Path(d) / "app"
        sh.copytree(ROOT / "tests" / "fixture-app", app)
        subprocess.run(["git", "init", "-q", str(app)], check=True)
        insert = ("INSERT INTO teams (name) VALUES ('Otter; made-up') RETURNING 'testdata', 'teams', 'id', id::text;\n"
                  "INSERT INTO members (team_id, username, role) SELECT id, 'td-otter', 'owner' FROM teams "
                  "RETURNING 'testdata', 'members', 'id', id::text;")
        env = {k: v for k, v in __import__("os").environ.items() if k != "FIXTURE_DB_URL"}

        def guarded(*args, stdin="", with_url=True):
            e = dict(env, FIXTURE_DB_URL="sentinel-address-td1") if with_url else env
            r = subprocess.run([sys.executable, "-B", str(guard), *args], input=stdin, capture_output=True,
                               text=True, cwd=app, env=e)
            return r.returncode, (r.stdout + r.stderr).strip()

        cases = [
            (lambda: run_script(recipe_py, "opt", "testdata.databases", cwd=app), 0, "staging\t"),
            (lambda: run_script(recipe_py, "--file", "bandit.no-migrations.yaml", "opt", "testdata.logic", cwd=app), 0, "none"),
            (lambda: guarded("--file", "bandit.testdata-missing-key.yaml", "check", "development"), 3, "missing key `testdata.logic`"),
            (lambda: guarded("check", "production"), 6, "not a test database"),
            (lambda: guarded("--file", "bandit.testdata-unsafe.yaml", "check", "test"), 6, "lists production"),
            (lambda: guarded("--file", "bandit.testdata-secret.yaml", "check", "development"), 6, "holds an address or password"),
            (lambda: guarded("check", "development", with_url=False), 6, "`FIXTURE_DB_URL` is not set"),
            (lambda: guarded("create", "development", "--kind", "card", "--label", "c1", stdin="UPDATE teams SET name = 'x';"), 6, "INSERTs only"),
            (lambda: guarded("create", "development", "--kind", "card", "--label", "c1", stdin="INSERT INTO teams (name) VALUES ('x');"), 6, "must end with RETURNING"),
            (lambda: guarded("read", "development", stdin="\\! echo hi"), 6, "meta-commands"),
            (lambda: guarded("create", "staging", "--kind", "card", "--label", "c1", stdin=insert), 6, "asks the user's yes"),
            (lambda: guarded("create", "development", "--kind", "card", "--label", "c1", stdin=insert), 0, "created 2 rows"),
            (lambda: guarded("clean", "development", "card", "c1", "--dry-run"), 0,
             "DELETE FROM members WHERE id::text IN ('fake-2');\nDELETE FROM teams WHERE id::text IN ('fake-1');"),
            (lambda: guarded("clean", "development", "card", "c1"), 0, "none left"),
            (lambda: guarded("records"), 0, "no open record"),
        ]
        for n, (call, code, text) in enumerate(cases, 1):
            got, out = call()
            if "sentinel-address-td1" in out:
                bad.append(f"case {n} printed the env var's value")
            if got != code or text not in out:
                bad.append(f"case {n} → {got} {out[-120:]!r}")
    report("TD1", not bad, "; ".join(bad) or f"testdata: {len(cases)} fixture cases (recipe section, refusals, "
           "INSERT-only create, staging yes, clean removes only the record's rows)")


# ── L5 · project instructions templates are one page, and the project skill ships them as-is ─
TEMPLATE_MAX_LINES, TEMPLATE_MAX_WORDS = 60, 450


def check_l5():
    canon = ROOT / "templates" / "instructions"
    shipped = PLUGINS / "bandit" / "skills" / "project" / "assets" / "instructions"
    names = sorted(p.name for p in canon.glob("*.md")) if canon.is_dir() else []
    bad = []
    if names != ["dev.md", "product_service.md", "workflow.md"]:
        bad.append(f"templates/instructions holds {names}, expected dev, product_service, workflow")
    for n in names:
        text = (canon / n).read_text(encoding="utf-8")
        body = text.split("\n", 1)[1] if text.startswith("<!--") else text
        lines, words = body.count("\n") + 1, len(body.split())
        if lines > TEMPLATE_MAX_LINES or words > TEMPLATE_MAX_WORDS:
            bad.append(f"{n} {lines} lines / {words} words > one page ({TEMPLATE_MAX_LINES} / {TEMPLATE_MAX_WORDS})")
        for need in ("## 🧭 Project Context", "Stage → command", "## 🧩 Modes"):
            if need not in text:
                bad.append(f"{n} lacks `{need}`")
        if not (shipped / n).exists() or (shipped / n).read_bytes() != (canon / n).read_bytes():
            bad.append(f"{n}: project/assets/instructions copy differs from templates/")
    extra = sorted(p.name for p in shipped.glob("*")) if shipped.is_dir() else []
    if extra != names:
        bad.append(f"project/assets/instructions holds {extra}")
    report("L5", not bad, "; ".join(bad) or f"{len(names)} templates ≤ one page, shipped byte for byte in bandit:project")


def main(argv):
    use_cli = "--no-cli" not in argv
    check_manifests()
    check_validate(use_cli)
    check_no_bin()
    check_versions()
    check_tags()
    check_g6()
    check_denylist()
    check_removed_tools()
    check_r15()
    check_guard_pin()
    check_l1()
    check_l2()
    check_l4()
    check_l8()
    check_t1()
    check_house_lint()
    check_audit_contract()
    check_sp7()
    check_sp8()
    check_recipe()
    check_testdata()
    check_l5()
    for rule, ok, msg in results:
        print(f"{'✅' if ok else '❌'} {rule} {msg}")
    failed = [r for r, ok, _ in results if not ok]
    print(f"check_repo: FAIL ({', '.join(failed)})" if failed
          else f"check_repo: OK ({len(results)} rules)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
