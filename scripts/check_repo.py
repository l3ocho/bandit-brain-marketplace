#!/usr/bin/env python3
"""Repo checker for bandit-brain-marketplace: rules as code (D19).

Usage:
    python3 scripts/check_repo.py            # every rule
    python3 scripts/check_repo.py --no-cli   # skip `claude plugin validate` (no Claude Code on PATH)

Exit 0 = green · 1 = a rule failed. Each rule prints one line; the last line is the verdict.
Rule homes and reasons: docs/decisions.md.
"""
import json
import os
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
# The app's own list (its src/domains/tasks/removedTools.ts); the 20 tools that replace them are in
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
    "delete_project_column delete_tag delete_folder manage_projects").split()
REMOVED_TOOLS_RE = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(REMOVED_TOOLS) + r")(?![A-Za-z0-9_])")


def check_removed_tools():
    hits = []
    # The CHANGELOG (its history, and its entries that name what changed) and the BR1 row name manage_projects.
    for f in [f for f in shipped_files() if f not in BRIDGE_SKIP]:
        text, _ = strip_history(f, f.read_text(encoding="utf-8", errors="ignore"))
        for n, line in enumerate(text.splitlines(), 1):
            if f == HISTORY_FILE and line.startswith("| BR1 |"):
                continue
            line = line.replace('action: "list_occurrences"', "")  # manage_recurrence's own action
            for m in REMOVED_TOOLS_RE.finditer(line):
                hits.append(f"{f.relative_to(ROOT)}:{n} `{m.group(1)}`")
    report("MT1", not hits,
           f"removed tools: {'; '.join(hits[:8])}{' …' if len(hits) > 8 else ''} ({len(hits)})" if hits
           else f"no removed assistant tool in {len(shipped_files())} shipped files ({len(REMOVED_TOOLS)} names)")


# ── BR1 · no project-named assistant name the app renamed for Boards (its docs/handoff/boards-rename-for-skills.md) ─
# The old names answer through a bridge for one release only, then NOT_FOUND or an unknown argument.
# Tool, argument and answer key names, refusal codes, and the argument and answer values.
BRIDGE_NAMES = (
    "manage_projects projectId projectColumnId projectName projectColor projectPosition projectFolderId projectIds "
    "projectMembers PROJECT_ARCHIVED PROJECT_HAS_OTHERS_CARDS RESTRICTED_PROJECT_NEEDS_MEMBER SYSTEM_OWNED_PROJECT "
    "TAG_WRONG_PROJECT TASK_HAS_NO_PROJECT task.project").split()
_WORDS = r"(?:tags|members|columns|lanes|sprints|boards)"  # not folders: vault folders too
BRIDGE_RE = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(n) for n in BRIDGE_NAMES) + r")(?![A-Za-z0-9_])"
                       r"|(?<![A-Za-z0-9_])(?:kind|scope)\s*(?::|={1,3})?\s*[`\"']project[`\"']"  # kind: "project", scope === 'project'
                       r"|(?<![A-Za-z0-9_])(?:kind|scope):\s*project\b|`project` (?:kind|scope)\b"   # scope: project
                       r"|delete_board_items`? \(project\)|get_context`?\s*(?:→|->)?\s*`?projects\b"
                       r"|(?:get_context|`folders`)[^\n]*`projects`"                         # its `projects`: get_context's key
                       r"|\((?=[^)\n]*\b" + _WORDS + r"\b)(?:[\w ]{1,20}, )*projects(?:, [\w ]{1,20})*\)")  # (tags, projects)
# Every shipped file but the CHANGELOG (release history keeps the names it shipped with); the BR1 row itself names them.
BRIDGE_SKIP = (ROOT / "CHANGELOG.md",)
# Old lines the rule must catch (from the skills before the move) and kept meanings it must leave alone.
BRIDGE_CATCH = ("`get_context` once. Its `projects` carry each folder", "Its `folders` and `projects` give", "(`folders`, `projects`)",
                "Read `get_context` once (tags, projects)", "first (projects, tags, members, sprints)",
                "`delete_board_items` (project)", "kind: 'project'", 'scope === "project"', "kind `project`",
                "get_context → projects", "`manage_projects`", "list_tasks { projectId }", "TASK_HAS_NO_PROJECT",
                "`get_context` projects check", "get_context -> projects", "scope: project", "the `project` scope",
                "(boards, projects)", "the hook body's task.project")
BRIDGE_KEEP = ("the domain's workflow project", 'board: project "Home Reno"', "a WBS-backed project",
               "Project-management cards", "projection", "the stamp ledger: its `projects` object",
               'elif board_kind == "project"', 'f"board.projects[{i}].lanes[{j}]"', "(dev projects, §1 Sprint folders)",
               "(Claude folders, projects)", "(vault folders, projects, inbox)", "a project's task.projection")


def check_bridge_names():
    missed = [s for s in BRIDGE_CATCH if not BRIDGE_RE.search(s)]
    missed += [f"false hit: {s}" for s in BRIDGE_KEEP if BRIDGE_RE.search(s)]
    if missed:
        return report("BR1", False, f"rule self-test failed: {'; '.join(missed)}")
    hits, files = [], [f for f in shipped_files() if f not in BRIDGE_SKIP]
    for f in files:
        text, _ = strip_history(f, f.read_text(encoding="utf-8", errors="ignore"))
        for n, line in enumerate(text.splitlines(), 1):
            if f == HISTORY_FILE and line.startswith("| BR1 |"):
                continue
            for m in BRIDGE_RE.finditer(line):
                hits.append(f"{f.relative_to(ROOT)}:{n} `{m.group(0)}`")
    report("BR1", not hits,
           f"old project names: {'; '.join(hits[:8])}{' …' if len(hits) > 8 else ''} ({len(hits)})" if hits
           else f"no old project-named assistant name in {len(files)} files")


# ── BP1 · no board type: the app replaced it with the board profile (sprint 2026-w44-d) ─
# manage_boards refuses `type`, and the values deliverable and hybrid no longer exist. A skill may say
# "type" for the Project Context key (`type: workflow`) or a vault note's frontmatter; not for a board.
BOARD_TYPE_RE = re.compile(r"manage_boards[^\n]*\btype\b"                        # a type argument on manage_boards
                           r"|\btype:\s*[`\"']?(?:deliverable|hybrid)\b"           # type: "deliverable"
                           r"|\"type\"\s*:\s*\"(?:deliverable|hybrid)\""               # JSON "type": "hybrid"
                           r"|`(?:deliverable|hybrid)`\s*·|·\s*(?:deliverable|hybrid)\s*·"  # a choice list or a row value
                           r"|`type` must be `(?:deliverable|hybrid)`"                 # a type check
                           r"|(?i:\b(?:deliverable|hybrid) board\b)"               # a Deliverable board
                           r"|(?i:\bboard(?:'s)? type\b)")                          # Board type, the board's type
BOARD_TYPE_CATCH = ('manage_boards { action: "create", name, folderId, type: "deliverable" }',
                    "type (`deliverable` · `workflow` · `hybrid`)", "WBS → a new Deliverable board",
                    "| Board type for a new board |", "`get_context` → `boards` gives each board's type", '"type": "hybrid", "folder"',
                    '"Home Reno" · deliverable · folder', "Its `type` must be `deliverable`")
BOARD_TYPE_KEEP = ("type: workflow", "`type:` (`product_service`, `workflow` or `claude_marketplace`)",
                   "type: brief", "L2 deliverable", "Plan the project or a deliverable",
                   'manage_boards { action: "create", name, profile, folderId }', "`hook.type`")


def check_board_type():
    missed = [s for s in BOARD_TYPE_CATCH if not BOARD_TYPE_RE.search(s)]
    missed += [f"false hit: {s}" for s in BOARD_TYPE_KEEP if BOARD_TYPE_RE.search(s)]
    if missed:
        return report("BP1", False, f"rule self-test failed: {'; '.join(missed)}")
    hits, files = [], [f for f in shipped_files() if f not in BRIDGE_SKIP]
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if f == HISTORY_FILE and line.startswith("| BP1 |"):
                continue
            for m in BOARD_TYPE_RE.finditer(line):
                hits.append(f"{f.relative_to(ROOT)}:{n} `{m.group(0)}`")
    report("BP1", not hits,
           f"board type: {'; '.join(hits[:8])}{' …' if len(hits) > 8 else ''} ({len(hits)}) — use the profile"
           if hits else f"no board type in {len(files)} files (profile only)")


# ── AT1 · the tool lists above are the app's: the app clone's tools and its removed list ──
# The 21 board tools the app serves today. The project audit's list must match it with FINANCE_TOOLS (AT2).
CURRENT_TOOLS = (
    "get_context list_tasks get_task add_comment list_events create_tasks update_tasks reopen_tasks "
    "delete_tasks manage_subtasks manage_recurrence link_tasks manage_boards manage_columns_lanes "
    "manage_tags manage_folders set_visibility delete_board_items manage_sprints get_sprints manage_inbox_groups").split()
# The 17 Finance tools (bandit:finance), from the app's finance descriptors.
FINANCE_TOOLS = (
    "finance_get_context finance_list_transactions finance_get_budget finance_list_schedules finance_get_report "
    "finance_list_rules finance_get_account_history finance_manage_accounts finance_manage_transactions "
    "finance_manage_budget finance_manage_categories finance_manage_payees finance_manage_schedules "
    "finance_import_transactions finance_manage_reconciliation finance_manage_rules finance_delete_items").split()
# The app clone on this host (read-only) and the branch the skills are built against.
APP_REPO = Path(os.environ.get("BANDIT_APP_REPO") or ROOT.parent / "bandit_brain")
# Held on the app commit before finance_manage_settlements (Leo, 2026-11-08, sprint mktplce-refining);
# the new Finance tool gets its own card, which moves this back to origin/development.
APP_REF = os.environ.get("BANDIT_APP_REF") or "639bdc44"


def app_file(path):
    r = subprocess.run(["git", "-C", str(APP_REPO), "show", f"{APP_REF}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def check_app_tools():
    desc = app_file("src/domains/tasks/descriptors.ts") if (APP_REPO / ".git").exists() else None
    if desc is None:
        return report("AT1", True, f"skipped (no app clone at {APP_REPO} with {APP_REF})")
    raw = desc.split("RAW_TASK_OPERATIONS", 1)[-1]
    app_tools = set(re.findall(r"^\s{4}name: '([a-z_]+)'", raw, re.M))
    fin = app_file("src/domains/finance/descriptors.ts") or ""
    fin_tools = set(re.findall(r"^\s{4}name: '(finance_[a-z_]+)'", fin.split("RAW_FINANCE_OPERATIONS", 1)[-1], re.M))
    removed_src = app_file("src/domains/tasks/removedTools.ts") or ""
    app_removed = set(re.findall(r"^\s{2}([a-z_]+): \{ tool:", removed_src, re.M))
    bad = []
    if app_tools != set(CURRENT_TOOLS):
        bad.append(f"app tools ≠ CURRENT_TOOLS: new {sorted(app_tools - set(CURRENT_TOOLS))}, "
                   f"gone {sorted(set(CURRENT_TOOLS) - app_tools)}")
    if fin_tools != set(FINANCE_TOOLS):
        bad.append(f"app finance tools ≠ FINANCE_TOOLS: new {sorted(fin_tools - set(FINANCE_TOOLS))}, "
                   f"gone {sorted(set(FINANCE_TOOLS) - fin_tools)}")
    if removed_src and app_removed != set(REMOVED_TOOLS):
        bad.append(f"app removed list ≠ REMOVED_TOOLS: {sorted(app_removed ^ set(REMOVED_TOOLS))}")
    report("AT1", not bad, "; ".join(bad) + " — update the skills, then both lists (docs/dependencies.md)" if bad
           else f"skills' tool lists = the app's at {APP_REF} ({len(app_tools)} board, {len(fin_tools)} finance, "
                f"{len(app_removed)} removed)")


# ── AT2 · copies that must match: the project audit's tool list, the Project Context lines ──
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
CONTEXT_BLOCK = PLUGINS / "bandit" / "skills" / "project" / "references" / "project-context.md"
PROJECT_AUDIT = PLUGINS / "bandit" / "skills" / "project" / "references" / "audit.md"


def context_lines(text):
    """The three lines under the Project Context keys: who reads it, the scope line, the names-only line."""
    return [l for l in text.splitlines() if l.startswith(("Read by ", "**Home board first", "Names only:"))][:3]


def check_copies():
    bad = []
    audit = PROJECT_AUDIT.read_text(encoding="utf-8")
    sec = audit.split("**Legacy tool names**", 1)[-1].split("- **Legacy lifecycle**", 1)[0]
    listed = re.findall(r"`([a-z_]+)`", sec.split("Any other", 1)[0])
    if sorted(listed) != sorted(CURRENT_TOOLS + FINANCE_TOOLS):
        bad.append(f"project audit's tool list ≠ CURRENT_TOOLS + FINANCE_TOOLS: "
                   f"{sorted(set(listed) ^ set(CURRENT_TOOLS + FINANCE_TOOLS))}")
    canon = context_lines(CONTEXT_BLOCK.read_text(encoding="utf-8"))
    if len(canon) != 3:
        bad.append("project-context.md: the block's three lines not found")
    for f in [ROOT / "CLAUDE.md", *sorted((ROOT / "templates" / "instructions").glob("*.md"))]:
        if context_lines(f.read_text(encoding="utf-8")) != canon:
            bad.append(f"{f.relative_to(ROOT)}: Project Context lines ≠ project-context.md")
    report("AT2", not bad, "; ".join(bad) or "project audit lists the current tools; Project Context lines match "
           "in CLAUDE.md and the templates")


# ── CL1 · a plugin change since the last release has an Unreleased CHANGELOG entry ──────
def last_tag():
    r = subprocess.run(["git", "describe", "--tags", "--abbrev=0", "--match", "v*"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def changed_since(tag):
    """Files changed since the tag: commits, staged and working tree, plus new untracked files."""
    out = subprocess.run(["git", "diff", "--name-only", tag], cwd=ROOT, capture_output=True, text=True).stdout.split()
    out += subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split()
    return sorted(set(out))


def check_changelog_entry():
    tag = last_tag()
    if not tag:
        return report("CL1", True, "skipped (no release tag)")
    plug = [f for f in changed_since(tag) if f.startswith("plugins/") and "__pycache__" not in f]
    if not plug:
        return report("CL1", True, f"no plugin change since {tag}")
    text = CHANGELOG.read_text(encoding="utf-8")
    top = text.split("\n## ", 1)[-1] if "\n## " in text else ""
    entry = top.split("\n## ", 1)[0]
    head = (entry.split() or [""])[0]
    # Unreleased with a line, or the entry release.py just dated for a version not yet tagged.
    ok = (head == "Unreleased" or (SEMVER_RE.match(head) and f"v{head}" != tag)) and re.search(r"^- ", entry, re.M)
    report("CL1", bool(ok), f"{len(plug)} plugin files changed since {tag}, CHANGELOG entry present" if ok
           else f"{len(plug)} plugin files changed since {tag} but CHANGELOG has no `## Unreleased` entry with a line")


# ── CS1 · every skill command is on the cheat sheet ──────────────────────────────────────
def check_cheat_sheet():
    sys.path.insert(0, str(PLUGINS / "bandit-maker" / "skills" / "skill" / "scripts"))
    import house_lint
    sheet = (ROOT / "docs" / "cheat-sheet.md").read_text(encoding="utf-8")
    missing = []
    for s in all_skills():
        for word, skill in house_lint._commands(s)[0].items():
            if f"/{skill} {word}" not in sheet:
                missing.append(f"/{skill} {word}")
    report("CS1", not missing, f"commands missing from docs/cheat-sheet.md: {', '.join(missing)}" if missing
           else "every skill command is on the cheat sheet")

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
CORE_DESC_TOTAL = 2700


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


# ── EX1 · the sprint commit proves the Execution board by due date, not by column ─
def check_execution_by_date():
    plan = (PLUGINS / "bandit-dev" / "skills" / "sprint" / "references" / "plan.md").read_text(encoding="utf-8")
    step = plan.split("## 12 · Commit the sprint", 1)[-1].split("\n## ", 1)[0]
    flat = " ".join(step.split())
    missing = [w for w in ("A card with no due date gets the sprint date", "this week's Sunday",
                           "Verify by date, not by column") if w not in flat]
    old = [w for w in ("No tag and no due date", "keeps its own (the sprint's date is the sprint's)")
           if w in flat]
    sunday = "No date given: the sprint date is this week's Sunday" in " ".join(plan.split())
    ok = not missing and not old and sunday
    report("EX1", ok, "plan step 12 dates undated cards and checks each due date against this week's Sunday"
           if ok else f"plan step 12 lost the Execution board check: missing {missing}, old wording {old}, "
           f"Sunday default {'present' if sunday else 'missing'} (BB-282, decision RS9)")


# ── DB1 · a debug fix runs its targeted tests; the full check runs once before each push ─
def check_debug_push():
    debug = (PLUGINS / "bandit-dev" / "skills" / "sprint" / "references" / "debug.md").read_text(encoding="utf-8")
    loop = debug.split("## Fix loop", 1)[-1].split("\n## ", 1)[0]
    push = debug.split("## Pushing", 1)[-1].split("\n## ", 1)[0] if "## Pushing" in debug else ""
    fix_full = bool(re.search(r"\(code review, verify", loop)) or "No full check per fix" not in " ".join(loop.split())
    push_ok = "`verify`" in push and "Red stops the push" in push
    ok = not fix_full and push_ok
    report("DB1", ok, "debug: a fix runs its targeted tests, the full check runs once before each push"
           if ok else f"debug.md: fix loop asks for a full check per fix: {fix_full}; push step with verify: {push_ok} (BB-299)")


# ── DC1 · the design card rule has one home, and sprint planning points to it ─
def check_design_card():
    tasks = PLUGINS / "bandit" / "skills" / "tasks" / "references"
    homes = [p.name for p in tasks.glob("*.md") if "**Design card**" in p.read_text(encoding="utf-8")]
    plan = (PLUGINS / "bandit-dev" / "skills" / "sprint" / "references" / "plan.md").read_text(encoding="utf-8")
    context = (PLUGINS / "bandit" / "skills" / "project" / "references" / "project-context.md").read_text(encoding="utf-8")
    bad = []
    if homes != ["dev-workflow.md"]:
        bad.append(f"design card rule homes: {homes or 'none'} (one: dev-workflow.md)")
    if "Design card" not in plan.split("## 2 · Spec completeness check", 1)[-1].split("\n## ", 1)[0]:
        bad.append("plan step 2 does not flag an open design card")
    if "| `design` *(optional)*" not in context:
        bad.append("project-context.md lacks the optional design line")
    if re.search(r"\bdesign\.(board|column)\b", " ".join(p.read_text(encoding="utf-8") for p in tasks.glob("*.md"))):
        bad.append("bandit:tasks reads a bandit.yaml design key (core never reads bandit.yaml)")
    report("DC1", not bad, "; ".join(bad) or "design card: one home (dev-workflow.md), planning flags an open one, "
           "the Project Context lists the optional line")


# ── SP11 · a done wave has its section, Flow and Tokens blocks in the wave report ─
def check_sp11():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "check_sprint.py"
    vault = ROOT / "tests" / "fixture-vault"
    good = run_script(script, "--vault", str(vault), "--domain", "Record")
    bad = run_script(script, "--vault", str(vault), "--domain", "WaveBad")
    ok = (good[0] == 0 and "SP1-SP13" in good[1] and bad[0] == 1 and bad[1].count("\n- ") == 1
          and "SP11" in bad[1] and "Tokens" in bad[1])
    report("SP11", ok, "check_sprint passes a done wave with its report section and refuses one without its Tokens block"
           if ok else f"SP11: Record → {good[0]} {good[1][-120:]!r}; WaveBad → {bad[0]} {bad[1][-160:]!r}")


# ── DH1 · a screen card's UI check compares the build with its design handover, once ─
def check_design_handover():
    s = PLUGINS / "bandit-dev" / "skills" / "sprint" / "references"
    prompt = (s / "templates.md").read_text(encoding="utf-8").split("## Execution prompt", 1)[-1].split("\n## ", 1)[0]
    flat = " ".join(prompt.split())
    bad = [w for w in ("names the design handover", "one comparison inside the same UI-check launch",
                       "matches the design handover", "no `Design:` line gets no comparison") if w not in flat]
    if "design handover" not in (s / "run.md").read_text(encoding="utf-8"):
        bad.append("run.md's UI-check brief")
    if "matches the design handover" not in (s / "plan.md").read_text(encoding="utf-8"):
        bad.append("plan.md step 7's Verification row")
    report("DH1", not bad, "design comparison: the execution prompt, run's brief and the plan's Verification row "
           "name the design handover" if not bad else f"design comparison missing: {bad} (BB-317)")


# ── GO1 · each card goes through its gates once: review, one UI check, one full check, merge ─
GATE_ORDER = ("Per card, in this order: code review and every fix first; then one browser check (when UI changed); "
              "then one full check, last, after the card's notes and status are committed; then merge. "
              "A browser check never starts while code review is still open.")
TRUNK_DONE = 'the trunk check counts as done when the project\'s full check prints "already passed"'


def check_gate_order():
    s = PLUGINS / "bandit-dev" / "skills" / "sprint" / "references"
    prompt = " ".join((s / "templates.md").read_text(encoding="utf-8")
                      .split("## Execution prompt", 1)[-1].split("\n## ", 1)[0].split())
    run = " ".join((s / "run.md").read_text(encoding="utf-8")
                   .split("## Gates the wave agent cannot run", 1)[-1].split("\n## ", 1)[0].split())
    push = " ".join((s / "execute.md").read_text(encoding="utf-8").split("## Pushing", 1)[-1].split("\n## ", 1)[0].split())
    bad = [w for w, ok in (("execution prompt: the gate order word for word", GATE_ORDER in prompt),
                           ("execution prompt: the trunk check's \"already passed\"", TRUNK_DONE in prompt),
                           ("execute.md Pushing: \"already passed\"", "already passed" in push),
                           ("run.md fallback: UI check only once review is closed", "Only once review is closed" in run),
                           ("run.md fallback: verify once, last", "runs `verify` (`bandit.yaml`) once, last" in run)) if not ok]
    report("GO1", not bad, "; ".join(bad) + " (BB-373)" if bad else
           "gate order: review and fixes, one UI check, one full check last, then merge; \"already passed\" ends the trunk check")


# ── DM1 · the dev mirror prunes .claude/worktrees/, and this repo runs the reference copy ─
def check_dev_mirror():
    ref = (PLUGINS / "bandit" / "skills" / "project" / "references" / "dev-mirror.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*3\. `\.claude/hooks/mirror-check\.py`\*\*[^\n]*\n\n```python\n(.*?)\n```", ref, re.S)
    code = m.group(1) if m else ""
    bad = []
    if not code:
        bad.append("dev-mirror.md has no mirror-check.py block")
    elif "rglob(" in code or "dirnames[:]" not in code or '".claude/worktrees"' not in code:
        bad.append("the reference script walks .claude/ without pruning .claude/worktrees")
    own = ROOT / ".claude" / "hooks" / "mirror-check.py"
    if code and own.is_file() and own.read_text(encoding="utf-8").rstrip("\n") != code.rstrip("\n"):
        bad.append(".claude/hooks/mirror-check.py differs from the dev-mirror.md copy")
    report("DM1", not bad, "; ".join(bad) + " (BB-373)" if bad else
           "dev mirror: the reference prunes .claude/worktrees, this repo runs the same copy")


# ── SP12 · a done wave is drawn done in the sprint map (temporary, decisions RS16) ─
def check_sp12():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "check_sprint.py"
    vault = ROOT / "tests" / "fixture-vault"
    good = run_script(script, "--vault", str(vault), "--domain", "Record")
    bad = run_script(script, "--vault", str(vault), "--domain", "MapBad")
    ok = good[0] == 0 and bad[0] == 1 and bad[1].count("\n- ") == 1 and "SP12" in bad[1]
    report("SP12", ok, "check_sprint passes a map that lists the done waves and refuses one not redrawn after a wave"
           if ok else f"SP12: Record → {good[0]} {good[1][-120:]!r}; MapBad → {bad[0]} {bad[1][-160:]!r}")


# ── SP13 · a sprint committed after 2026-11-08 gives every batch card its build-step count in step 9 (fixtures) ─
def check_sp13():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "check_sprint.py"
    vault = ROOT / "tests" / "fixture-vault"
    good = run_script(script, "--vault", str(vault), "--domain", "StepsGood")
    bad = run_script(script, "--vault", str(vault), "--domain", "StepsBad")
    earlier = run_script(script, "--vault", str(vault), "--domain", "Record")   # committed before the cut-off: exempt
    plan = (PLUGINS / "bandit-dev" / "skills" / "sprint" / "references" / "plan.md").read_text(encoding="utf-8")
    plan = " ".join(plan.split())
    words = [w for w in ("write the card's **build steps** from its plan section as ordered sub-tasks",
                         "A card with no build sub-tasks fails readiness", "`{card id}: {n} steps`") if w not in plan]
    ok = (good[0] == 0 and "SP1-SP13" in good[1] and bad[0] == 1 and bad[1].count("\n- ") == 1 and "SP13" in bad[1]
          and "GA-2" in bad[1] and earlier[0] == 0 and not words)
    report("SP13", ok, "check_sprint passes a sprint whose step 9 counts every batch card's build steps, refuses one with a "
           "card at 0 steps, leaves earlier sprints alone; plan.md steps 7 and 9 name the sub-tasks and the count"
           if ok else f"SP13: StepsGood → {good[0]} {good[1][-120:]!r}; StepsBad → {bad[0]} {bad[1][-160:]!r}; "
           f"Record → {earlier[0]}; plan.md lost {words} (BB-374)")


# ── WO1 · a card waits for its own blockers, not for the wave before it; the cap counts the sprint's cards ─
OLD_ORDER = re.compile(r"refused\s+while\s+wave\s+N-1|strictly\s+in\s+sequence|Waves\s+run\s+in\s+order|Last\s+wave\s+only"
                       r"|move\s+the\s+next\s+wave['’]s\s+cards|list_tasks\(\{\s*executionState:\s*'next'", re.I)


def old_order_hits(text):
    return [m.group(0) for m in OLD_ORDER.finditer(" ".join(text.split()))]


def check_wave_order():
    s = PLUGINS / "bandit-dev" / "skills" / "sprint"
    files = [s / "SKILL.md", *sorted((s / "references").glob("*.md"))]
    files = [f for f in files if f.name not in ("gotchas.md", "old-way.md")]   # history lines quote the old wording
    hits = [f"{f.relative_to(ROOT)}: {h!r}" for f in files for h in old_order_hits(f.read_text(encoding="utf-8"))]
    cases = [("Wave N is refused while wave N-1 is not done", 1), ("Strictly\nin sequence.", 1), ("Waves run in order.", 1),
             ("**Last wave only:** when", 1), ("move the next wave's cards to `next`", 1),
             ("`list_tasks({ executionState: 'next' })`", 1),
             ("`list_tasks({ sprintId, executionState: 'next' })`: this sprint's cards only", 0),
             ("A wave waits for what it depends on, not for the wave before it.", 0)]
    bad_cases = [c for c, n in cases if len(old_order_hits(c)) != n]
    execute = " ".join((s / "references" / "execute.md").read_text(encoding="utf-8").split())
    run = " ".join((s / "references" / "run.md").read_text(encoding="utf-8").split())
    words = [w for w, src in (("A wave waits for what it depends on, not for the wave before it", execute),
                              ("`list_tasks({ sprintId, executionState: 'next' })`", execute),
                              ("counted over this sprint's own cards", execute),
                              ("a wave whose dependencies are delivered runs even while an earlier wave holds a paused "
                               "or blocked card", run)) if w not in src]
    script = s / "scripts" / "check_sprint.py"
    vault = ROOT / "tests" / "fixture-vault"
    free = run_script(script, "--vault", str(vault), "--domain", "WavesFree")   # a later independent wave done early
    dep = run_script(script, "--vault", str(vault), "--domain", "WavesDep")     # dependent waves done early
    fx = free[0] == 0 and dep[0] == 1 and dep[1].count("\n- ") == 2 and "which it depends on" in dep[1]
    ok = not hits and not bad_cases and not words and fx
    report("WO1", ok, f"wave order: no strict-order wording in {len(files)} sprint files ({len(cases)} self-test cases); the cap "
           "counts the sprint's cards; SP10 passes a later independent wave done early and refuses a dependent one"
           if ok else f"old wave-order wording {hits + bad_cases}; lost {words}; fixtures: WavesFree → {free[0]} "
           f"{free[1][-100:]!r}, WavesDep → {dep[0]} {dep[1][-160:]!r} (BB-397)")


# ── AC1 · README and install guide say which Bandit Brain app version the marketplace version needs ─
def compat_has_row(text, version):
    """True when the `### Works with Bandit Brain` table has a row for `version`."""
    table = text.split("### Works with Bandit Brain", 1)[-1].split("\n### ", 1)[0].split("\n## ", 1)[0] \
        if "### Works with Bandit Brain" in text else ""
    return re.search(rf"^\|\s*{re.escape(version)}\s*\|\s*\S[^|]*\|\s*\S[^|]*\|\s*$", table, re.M) is not None


def check_app_compat():
    market, _ = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    version = ((market or {}).get("metadata") or {}).get("version") or ""
    docs = {name: (ROOT / name).read_text(encoding="utf-8") for name in ("README.md", "docs/install.md")}
    bad = [f"{name} has no `Works with Bandit Brain` row for {version}" for name, text in docs.items()
           if not compat_has_row(text, version)]
    # The rule must fail on a table without the current row and pass on one with it.
    sample = "### Works with Bandit Brain\n\n| Marketplace | App | Finance |\n|---|---|---|\n| 9.9.9 | v1.0.0 | same |\n"
    if compat_has_row(sample, "9.9.8") or not compat_has_row(sample, "9.9.9"):
        bad.append("the rule does not fail on a missing row and pass on a present one")
    report("AC1", not bad, "; ".join(bad) + " (BB-401)" if bad else
           f"app compatibility: README and install guide each have a row for {version}; a version with no row fails")


# ── DK1 · the debug card: one home for its three line shapes and its moves, and every step that uses it points there ─
PROCESS_SHAPE = "Process: {step} —"
DEBUG_NEEDLES = (("plan.md", "Create the debug card"), ("execute.md", "`Expected:` line"),
                 ("debug.md", "The debug card first"), ("close.md", "The debug card"), ("run.md", "debug card"))
DEBUG_OLD = ("stays where `plan` seeded it until `close`", "and never the debug card", "is not one and stays put",
             "two line shapes", "The debug card is never moved by a wave.")


def debug_card_problems(files):
    """`files` maps a sprint reference name to its text."""
    flat = {n: " ".join(x.split()) for n, x in files.items()}
    bad = []
    for shape in ("Expected: {screen} › {part} —", PROCESS_SHAPE):
        homes = sorted(n for n, x in files.items() if shape in x)
        if homes != ["templates.md"]:
            bad.append(f"line shape '{shape}' lives in {homes or 'nowhere'} (one home: templates.md)")
    for name, words in DEBUG_NEEDLES:
        if words not in files.get(name, ""):
            bad.append(f"{name} lost '{words}'")
    t = flat.get("templates.md", "")
    if "three line shapes" not in t or "| Card | Expected | Found | Process | Fixed |" not in t:
        bad.append("templates.md must name three line shapes and a Process column in the Debug table")
    if "Process lines** (the one home" not in t or "**Moves.**" not in t or "ticked once it is fixed or its lesson" not in t:
        bad.append("templates.md lost the Process lines rule, the Moves rule or the Process outcome")
    if "`doing` when `debug` starts" not in t or "`standby` when `release` starts" not in t:
        bad.append("templates.md must say the debug card goes to doing at debug and standby at release")
    if not re.search(r"Move the sprint's debug card .{0,80}to `doing`", flat.get("debug.md", "")):
        bad.append("debug.md Intake 1 must move the debug card to doing")
    if not re.search(r"move the sprint's debug card .{0,80}to `standby`", flat.get("release.md", "")):
        bad.append("release.md step 1 must move the debug card to standby before the recipe")
    for name, words in (("execute.md", "writes its Process line on the debug card"), ("run.md", "gets a Process line on the debug card"),
                        ("debug.md", "writes its Process line on the debug card"), ("release.md", "writes a Process line on it")):
        if words not in flat.get(name, ""):
            bad.append(f"{name} does not say a stalled step writes a Process line ('{words}')")
    if "Process lines" not in flat.get("close.md", ""):
        bad.append("close.md's report must name the Process lines")
    for name, x in flat.items():
        for old in DEBUG_OLD:
            if old in x:
                bad.append(f"{name} still says '{old}'")
    return bad


def check_debug_card():
    s = PLUGINS / "bandit-dev" / "skills" / "sprint" / "references"
    files = {p.name: p.read_text(encoding="utf-8") for p in s.glob("*.md")}
    bad = debug_card_problems(files)

    def without(name, old, new=""):
        copy = dict(files)
        assert old in copy[name], (name, old)
        copy[name] = copy[name].replace(old, new)
        return copy
    mutants = [without("templates.md", "Process lines** (the one home", "Other lines** (the one home"),
               without("templates.md", "`doing` when `debug` starts", "`doing` when it starts"),
               without("templates.md", "| Found | Process | Fixed |", "| Found | Fixed |"),
               without("templates.md", "three line shapes", "two line shapes"),
               without("debug.md", "to `doing` (`update_tasks`", "to `assigned` (`update_tasks`"),
               without("release.md", "to `standby` with `update_tasks`", "to `done` with `update_tasks`"),
               without("execute.md", "writes its Process line", "writes its note"),
               without("run.md", "gets a Process line", "gets a note"),
               without("debug.md", "writes its Process line", "writes its note"),
               without("release.md", "writes a Process line", "writes a note"),
               without("close.md", "Process lines", "notes"),
               without("close.md", "The debug card", "The bug card"),
               {**files, "execute.md": files["execute.md"] + "\nthe debug card stays where `plan` seeded it until `close`\n"},
               {**files, "debug.md": files["debug.md"] + f"\n`{PROCESS_SHAPE}` again\n"}]
    missed = [i for i, m in enumerate(mutants) if not debug_card_problems(m)]
    if missed:
        bad.append(f"the rule does not fail on every broken copy (missed {missed})")
    report("DK1", not bad, "; ".join(bad) + " (BB-381)" if bad else
           "debug card: three line shapes in templates.md only; plan creates it, debug moves it to doing, release to "
           "standby, close completes it; every step points to the Process line rule; the wave adds Expected lines, "
           "debug reads it first, close refuses an unticked line, run names it")


# ── DL1 · the design page link and the handover files' place ride on the card, and every reader finds the files through `Handover:` ─
DESIGN_LINK_FILES = {"dev-workflow.md": ("plugins", "bandit", "skills", "tasks", "references", "dev-workflow.md"),
                     "dev.md": ("plugins", "bandit", "skills", "tasks", "references", "dev.md"),
                     "plan.md": ("plugins", "bandit-dev", "skills", "sprint", "references", "plan.md"),
                     "templates.md": ("plugins", "bandit-dev", "skills", "sprint", "references", "templates.md"),
                     "run.md": ("plugins", "bandit-dev", "skills", "sprint", "references", "run.md"),
                     "debug.md": ("plugins", "bandit-dev", "skills", "sprint", "references", "debug.md"),
                     "pipeline.md": ("docs", "pipeline.md")}


def design_link_problems(files):
    """`files` maps a short file name (DESIGN_LINK_FILES) to its text."""
    flat = {n: " ".join(x.split()) for n, x in files.items()}
    bad = []
    dw = flat.get("dev-workflow.md", "")
    design_step = dw.split("### Design step", 1)[-1].split("**Design card**", 1)[0]
    design_card = dw.split("**Design card**", 1)[-1].split("### ", 1)[0]
    for where, text, words in (
            ("Design step", design_step, ("<p>Design: {page link}</p>", "full `https://` address",
                                          "<p>Handover: {where the handover files live}</p>",
                                          "The agent that lands the handover and writes the card's Spec adds both")),
            ("Design card", design_card, ("<p>Design page: {page link}</p>", "<p>Handover: {where the handover files live}</p>",
                                          "It is not completed without the page link", "<p>Design: {page link}</p>",
                                          "found through the design card's `Handover:` line, reached through the build card's `blockedBy`",
                                          "carries both `Design: {page link}` and `Handover: {where the handover files live}`"))):
        for w in words:
            if w not in text:
                bad.append(f"dev-workflow.md {where} lost '{w}'")
    if "{handover link}" in dw:
        bad.append("dev-workflow.md still puts the handover link on the build card's Design line")
    if "<p>Design: {page link}</p>" not in flat.get("dev.md", ""):
        bad.append("dev.md's Source row does not name the page link")
    if "is not a full web address" not in flat.get("plan.md", ""):
        bad.append("plan.md step 2 has no fix row for a Design line that is missing or not a full web address")
    for name in ("templates.md", "run.md", "debug.md"):
        if "`Handover:` line" not in flat.get(name, ""):
            bad.append(f"{name} does not send the reader to the `Handover:` line for the handover files")
    if "`Handover:`" not in flat.get("pipeline.md", "") or "full web address" not in flat.get("pipeline.md", ""):
        bad.append("pipeline.md stage 4 does not match (page link, Handover line)")
    homes = sorted(n for n, x in files.items() if "<p>Design page: {page link}</p>" in x)
    if homes != ["dev-workflow.md"]:
        bad.append(f"the design card's page line lives in {homes or 'nowhere'} (one home: dev-workflow.md)")
    return bad


def check_design_link():
    root = ROOT
    files = {n: root.joinpath(*parts).read_text(encoding="utf-8") for n, parts in DESIGN_LINK_FILES.items()}
    bad = design_link_problems(files)

    def without(name, old, new=""):
        copy = dict(files)
        assert old in copy[name], (name, old)
        copy[name] = copy[name].replace(old, new)
        return copy
    mutants = [without("dev-workflow.md", "<p>Design page: {page link}</p>", "<p>Design page: {link}</p>"),
               without("dev-workflow.md", "It is not completed\n   without the page link.", "It is completed."),
               without("dev-workflow.md", "full\n   `https://` address", "link"),
               without("dev-workflow.md", "The agent that lands the handover and writes the card's Spec adds both", "Someone adds both"),
               without("dev-workflow.md", "reached through the build card's `blockedBy`", "reached some way"),
               without("dev-workflow.md", "carries both `Design: {page link}` and `Handover:", "carries `Design: {page link}` and `Files:"),
               {**files, "dev-workflow.md": files["dev-workflow.md"] + "\nthe build card's `<p>Design: {handover link}</p>`\n"},
               without("dev.md", "{page link}", "{link}"),
               without("plan.md", "is not a full web address", "is odd"),
               without("templates.md", "`Handover:` line", "`Design:` line"),
               without("run.md", "`Handover:` line", "`Design:` line"),
               without("debug.md", "`Handover:` line", "`Design:` line"),
               without("pipeline.md", "(`Handover:`)", "(handover)"),
               {**files, "run.md": files["run.md"] + "\n<p>Design page: {page link}</p>\n"}]
    missed = [i for i, m in enumerate(mutants) if not design_link_problems(m)]
    if missed:
        bad.append(f"the rule does not fail on every broken copy (missed {missed})")
    report("DL1", not bad, "; ".join(bad) + " (BB-377)" if bad else
           f"design links: the page link and the Handover line live in dev-workflow.md only (design card and build card, "
           f"with and without a design card); planning flags a missing or non-web Design line; the UI check, run and "
           f"debug find the files through the Handover line; {len(mutants)} broken copies all fail")


# ── DS1 · a design that changed the shared look ends by asking for design sync, and the design card records it ─
def design_sync_problems(files):
    """`files` maps a short file name to its text; dev-workflow.md is the one home."""
    flat = {n: " ".join(x.split()) for n, x in files.items()}
    dw = flat.get("dev-workflow.md", "")
    step = dw.split("### Design step", 1)[-1].split("**Design card**", 1)[0]
    card = dw.split("**Design card**", 1)[-1].split("### ", 1)[0]
    bad = []
    for w in ("**Closing step.**", "changed the shared look (colours, fonts, spacing, shared components)",
              "asking the user to run `/design-sync`", "the helpers cannot run",
              "<p>Design sync run {date}</p>", "<p>Design sync not needed: {reason}</p>"):
        if w not in step:
            bad.append(f"dev-workflow.md Design step lost '{w}'")
    if "without one of the two design sync lines" not in card:
        bad.append("dev-workflow.md Design card is completed without a design sync line")
    homes = sorted(n for n, x in files.items() if "**Closing step.**" in x and "design-sync" in x)
    if homes != ["dev-workflow.md"]:
        bad.append(f"the design sync closing step lives in {homes or 'nowhere'} (one home: dev-workflow.md)")
    for n in ("pipeline.md", "decisions.md"):
        if "Design sync run {date}" not in flat.get(n, "") and "design-sync" not in flat.get(n, ""):
            bad.append(f"{n} does not mention design sync")
    if "Design sync not needed: {reason}" not in flat.get("pipeline.md", ""):
        bad.append("pipeline.md stage 4 does not name the design sync lines")
    if "RS25" not in flat.get("decisions.md", ""):
        bad.append("decisions.md has no RS25 row")
    return bad


def check_design_sync():
    names = {"dev-workflow.md": ("plugins", "bandit", "skills", "tasks", "references", "dev-workflow.md"),
             "pipeline.md": ("docs", "pipeline.md"), "decisions.md": ("docs", "decisions.md"),
             "plan.md": ("plugins", "bandit-dev", "skills", "sprint", "references", "plan.md")}
    files = {n: ROOT.joinpath(*parts).read_text(encoding="utf-8") for n, parts in names.items()}
    bad = design_sync_problems(files)

    def without(name, old, new=""):
        copy = dict(files)
        assert old in copy[name], (name, old)
        copy[name] = copy[name].replace(old, new)
        return copy
    mutants = [without("dev-workflow.md", "**Closing step.**", "**Last step.**"),
               without("dev-workflow.md", "asking the user to run `/design-sync`", "asking the user"),
               without("dev-workflow.md", "<p>Design sync run {date}</p>", "<p>Synced</p>"),
               without("dev-workflow.md", "<p>Design sync not needed: {reason}</p>", "<p>No sync</p>"),
               without("dev-workflow.md", "(colours, fonts, spacing, shared", "(colours"),
               without("dev-workflow.md", "without one of the two design sync lines", "without the page link again"),
               without("pipeline.md", "Design sync not needed: {reason}", "no sync line"),
               without("decisions.md", "| RS25 |", "| RS99 |"),
               {**files, "plan.md": files["plan.md"] + "\n**Closing step.** ask for `/design-sync`\n"}]
    missed = [i for i, m in enumerate(mutants) if not design_sync_problems(m)]
    if missed:
        bad.append(f"the rule does not fail on every broken copy (missed {missed})")
    report("DS1", not bad, "; ".join(bad) + " (BB-398)" if bad else
           f"design sync: the closing step and the design card's sync line live in dev-workflow.md only; the design card is "
           f"not completed without one; pipeline and decisions match; {len(mutants)} broken copies all fail")


# ── TG1 · no helper forbids creating a tag or asks before creating one: the app's roles are the gate ─
TAG_BANS = (re.compile(r"\b(?:create|add)\s+columns[^.\n]*\btags?\b", re.I),   # a Never line that lists tags with columns
            re.compile(r"Creating a tag[^\n]*ask first", re.I),
            re.compile(r"TAG_NAME_TAKEN[^\n]*the user picks"))


def tag_ban_hits(text):
    return [m.group(0)[:60] for rx in TAG_BANS for m in rx.finditer(text)]


def check_tag_creation():
    hits = []
    for p in sorted(PLUGINS.rglob("*.md")):
        hits += [f"{p.relative_to(ROOT)}: {h}" for h in tag_ban_hits(p.read_text(encoding="utf-8"))]
    board = (PLUGINS / "bandit" / "skills" / "tasks" / "references" / "board.md").read_text(encoding="utf-8")
    if "REQUIRES_ADMIN" not in board.split("**Creating a tag**", 1)[-1].split("\n\n", 1)[0]:
        hits.append("board.md Creating a tag does not name the app's roles and refusals")
    # The rule must fail on the old lines and pass on the new ones.
    old = ("create columns, boards or tags", "- Add columns, lanes, tasks or tags.",
           "**Creating a tag** (a write needs one that doesn't exist; ask first)",
           "`TAG_NAME_TAKEN` · `TAG_NAME_RESERVED` | x | Offer another name; the user picks")
    new = ("create columns or boards", "- Add columns, lanes or tasks.", "**Creating a tag** (a write needs one that doesn't exist)")
    proof = all(tag_ban_hits(o) for o in old) and not any(tag_ban_hits(n) for n in new)
    if not proof:
        hits.append("the rule does not fail on the old ban lines and pass on the new ones")
    report("TG1", not hits, "; ".join(hits[:6]) + " (BB-396)" if hits else
           "tags: no helper forbids creating one or asks first; board.md names the app's roles as the gate")


# ── AP1 · the approval line: one home, no wave, run or debug step ticks it, close ticks it only on the user's yes ─
APPROVAL_LINE = "Tested and approved by you"
NEVER_TICKED = "the approval line is never ticked here"
TICKS_IT = re.compile(r"\btick(?:s)?\s+(?:the|its|their)\s+approval\s+line", re.I)


def approval_problems(files, claude):
    """`files` maps a sprint reference name to its text (plus 'templates.md', 'close.md'); `claude` is the repo CLAUDE.md."""
    flat = {n: " ".join(x.split()) for n, x in files.items()}
    bad = []
    homes = sorted(n for n, x in flat.items() if APPROVAL_LINE in x)
    if homes != ["templates.md"]:
        bad.append(f"the line's text lives in {homes or 'nowhere'} (one home: templates.md)")
    if "## Approval line" not in files.get("templates.md", ""):
        bad.append("templates.md lost its Approval line section")
    for name, n in (("execute.md", 1), ("run.md", 2), ("debug.md", 1)):
        if flat.get(name, "").count(NEVER_TICKED) < n:
            bad.append(f"{name} lost '{NEVER_TICKED}' (needs {n})")
    for name in ("plan.md", "execute.md", "run.md", "debug.md", "release.md"):
        if TICKS_IT.search(flat.get(name, "")):
            bad.append(f"{name} has a step that ticks the approval line")
    if "templates.md` → Approval line" not in flat.get("plan.md", ""):
        bad.append("plan.md does not add the approval line (step 7) or check it (step 9)")
    close = flat.get("close.md", "")
    if "Tick the approval line" not in close or "approval line is open" not in close or \
            close.find("Tick the approval line") > close.find("`update_tasks { items: [{ taskId, complete: true }"):
        bad.append("close.md must tick the approval line on the quoted approval before it completes, and refuse an open one")
    c = " ".join(claude.split())
    if "stay in Stand By" not in c or "approval line" not in c or "Only then close the card" in c:
        bad.append("CLAUDE.md 'Done means released' must leave the cards in Stand By until Leo's yes")
    return bad


def check_approval_line():
    s = PLUGINS / "bandit-dev" / "skills" / "sprint" / "references"
    files = {n: (s / n).read_text(encoding="utf-8") for n in ("plan.md", "execute.md", "run.md", "debug.md", "close.md",
                                                               "release.md", "templates.md")}
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    bad = approval_problems(files, claude)
    # The rule must fail on a copy without each part, and pass on the real text.
    def without(name, old, new=""):
        copy = dict(files)
        copy[name] = copy[name].replace(old, new)
        return copy
    mutants = [without("execute.md", NEVER_TICKED), without("run.md", NEVER_TICKED),
               without("debug.md", NEVER_TICKED),
               without("execute.md", NEVER_TICKED, "so tick the approval line"),
               without("plan.md", "templates.md` → Approval line"),
               without("close.md", "Tick the approval line"),
               without("templates.md", "## Approval line", "## Other"),
               {**files, "plan.md": files["plan.md"] + f"\n{APPROVAL_LINE}\n"}]
    missed = [i for i, m in enumerate(mutants) if not approval_problems(m, claude)]
    if missed or not approval_problems(files, claude.replace("stay in Stand By", "close the card")):
        bad.append(f"the rule does not fail on every broken copy (missed {missed})")
    report("AP1", not bad, "; ".join(bad) + " (BB-378)" if bad else
           "approval line: one home in templates.md; execute, run and debug never tick it; plan adds and checks it; close "
           "ticks it on the quoted approval and refuses an open one; the repo CLAUDE.md leaves cards in Stand By until Leo's yes")


# ── SM1 · the sprint map draws every card and link, routes no arrow through a card, follows the recipe ─
def crosses(seg, box):
    (x1, y1), (x2, y2) = seg
    bx, by, bw, bh = box
    lo_x, hi_x, lo_y, hi_y = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
    return lo_x < bx + bw - 0.5 and hi_x > bx + 0.5 and lo_y < by + bh - 0.5 and hi_y > by + 0.5


def check_sprint_map():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "sprint_map.py"
    data = ROOT / "tests" / "fixture-map" / "cosmetic-1.json"
    app = ROOT / "tests" / "fixture-app"
    spec = json.loads(data.read_text(encoding="utf-8"))
    bad = []
    got, out = run_script(script, str(data), "--geometry", cwd=ROOT)
    geo = json.loads(out) if got == 0 else {"boxes": {}, "paths": []}
    drawn = {c["id"] for c in spec["cards"] if c.get("wave")}
    if set(geo["boxes"]) != drawn:
        bad.append(f"cards drawn {sorted(geo['boxes'])} ≠ the cards with a wave")
    if len(geo["paths"]) != len(spec["links"]) + len(spec["after"]):
        bad.append(f"{len(geo['paths'])} arrows for {len(spec['links']) + len(spec['after'])} links")
    for p in geo["paths"]:
        pts = p["points"]
        if any(a[0] != b[0] and a[1] != b[1] for a, b in zip(pts, pts[1:])):
            bad.append(f"{p['from']}→{p['to']} has a slanted segment")
        for cid, box in geo["boxes"].items():
            if any(crosses(s, box) for s in zip(pts, pts[1:])):
                bad.append(f"{p['from']}→{p['to']} crosses {cid}")
    for recipe, want, not_want in (("bandit.yaml", "production card for you to fire", "release runs the deploy"),
                                   ("bandit.no-production.yaml", "release runs the deploy", "production card")):
        got, page = run_script(script, str(data), "--recipe", str(app / recipe), cwd=ROOT)
        if got != 0 or want not in page or not_want in page or 'name="sprint-map-waves-done" content="1,2"' not in page:
            bad.append(f"page with {recipe}: road or waves-done marker wrong")
    report("SM1", not bad, "; ".join(bad[:4]) or f"sprint_map.py: {len(drawn)} cards, {len(geo['paths'])} arrows at right "
           "angles, none through a card; the road follows the recipe; the waves-done marker is set")


# ── WF1 · the wave report's Flow and Tokens blocks match a hand count of the fixture logs ─
def check_wave_flow():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "wave_flow.py"
    logs = ROOT / "tests" / "fixture-logs"
    got, out = run_script(script, "--logs", str(logs), "--since", "2026-11-04T09:00:00Z", "--verify", "make verify",
                          "--test", "^run-tests", cwd=ROOT)
    want = ["- Time: 0:50 · per card: XY-1 0:35, XY-2 0:15",
            "- Full checks: 4 runs, 30 min total (1 in the background: not measured), 1 failed (FAILED: 1 test)",
            "- Test runs: 1 whole suite, 1 targeted", "- Gates: code review 1 rounds, UI check 0 rounds",
            "- Repeat runs: 2 (make verify)", "- Total: 1.2 M re-read from cache · 30 K new · 2 K written",
            "- Split: main chat 1.1 M (90%) · code-reviewer 121 K (10%)", "- Per card: XY-1 580 K, XY-2 642 K",
            "- Main chat: 9 steps · start context 100 K · peak context 140 K",
            # by source: hand count of the labelled fixture steps (marketplace 2 steps, connectors 3, everything else
            # 2 main steps and the 2 agent steps, 2 unlabelled), hooks (5 runs, 1000 ms, 1000 chars) and the priced cost
            "- By source: marketplace 220 K (18%) · Bandit Brain connectors 360 K (29%) · everything else 391 K (32%) "
            "· unlabelled 250 K (20%)",
            "- Top in marketplace: 1. bandit-dev:sprint 220 K (2 steps)",
            "- Top in Bandit Brain connectors: 1. claude.ai BanditBrain › get_task 120 K (1 step) · "
            "2. claude.ai BanditBrain › update_tasks 120 K (1 step) · 3. claude.ai BanditCloud › nc_webdav_read_file 120 K (1 step)",
            "- Top in everything else: 1. other-server › ping 140 K (1 step) · 2. other-plugin:lint 130 K (1 step) · "
            "3. agent code-reviewer 121 K (2 steps)",
            "- Unlabelled steps (no label recorded): 2 steps, 250 K",
            "- Helper agents by type: code-reviewer 121 K (10%), 2 steps",
            "- Hooks: 5 runs, 1000 ms total · added to the chat: 1000 chars (no tokens recorded) · by event: "
            "Stop 2× 500 ms · PreToolUse 2× 400 ms · SessionStart 1× 100 ms",
            "- Estimated cost: $0.33 (estimate, not billing; prices checked 2026-11-08) · claude-haiku-4-5 $0.03 · "
            "claude-opus-5-5 $0.28 · claude-sonnet-5-5 $0.03 · no price for claude-future-1: 140 K, not counted"]
    missing = [w for w in want if w not in out]
    gone, quiet = run_script(script, "--logs", str(logs), "--since", "2027-01-01T00:00:00Z", "--verify", "x", cwd=ROOT)
    # the groups follow the names given on the command line: one connector and one plugin renamed move the totals
    moved, regrouped = run_script(script, "--logs", str(logs), "--since", "2026-11-04T09:00:00Z", "--verify", "x",
                                  "--connectors", "claude.ai BanditBrain", "--marketplace-plugins", "other-plugin", cwd=ROOT)
    regroup = "- By source: marketplace 130 K (11%) · Bandit Brain connectors 240 K (20%) · everything else 602 K (49%)"
    ok = got == 0 and not missing and gone == 3 and moved == 0 and regroup in regrouped
    report("WF1", ok, f"wave_flow.py: {len(want)} Flow and Tokens lines match the hand count (steps deduped by "
           "message id, background run not measured, repeats after no edit, per card from CARD-START; tokens by source "
           "in three groups with the unlabelled line, helper agents, hooks by time and size, the estimated cost with its "
           "price date; the group names follow the arguments)"
           if ok else f"wave_flow.py → {got}, missing {missing}; empty window → {gone} (want 3); regrouped run → {moved}"
                      f"{'' if regroup in regrouped else ', group names not taken from the arguments'}")


# ── NA1 · the sprint helper never tells an executor to decide and continue without asking ─
NO_ASK_RE = re.compile(r"conservative\s+reading|cautious\s+reading|do(?:n['’]t|\s+not)\s+ask(?:\s+any)?\s+questions"
                       r"|never\s+ask\s+the\s+user|decide\s+(?:and\s+(?:continue|proceed)|alone)", re.I)
HISTORY_RE = re.compile(r"^- Sprint \d{4}-w\d+", re.M)  # a gotcha's dated history line quotes the old wording


def no_ask_hits(text):
    """Matches across hard line wraps; a dated gotcha history paragraph is skipped."""
    paras = [p for p in re.split(r"\n(?=- |\n)", text) if not HISTORY_RE.match(p.strip())]
    return [m.group(0) for p in paras for m in NO_ASK_RE.finditer(" ".join(p.split()))]


def check_no_decide_and_continue():
    roots = [PLUGINS / "bandit-dev" / "skills" / "sprint", PLUGINS / "bandit-dev" / "agents"]
    files = [f for r in roots for f in sorted(r.rglob("*.md"))]
    hits = [f"{f.relative_to(ROOT)}: {h!r}" for f in files for h in no_ask_hits(f.read_text(encoding="utf-8"))]
    cases = [("Do not ask questions; take the\nconservative reading.", 2), ("Don’t ask questions.", 1),
             ("Then decide and proceed.", 1), ("You may decide alone.", 1),
             ("autonomy (no questions about what the Spec, the plan or the project's rules already answer)", 0),
             ("- Sprint 2026-w44-e: the prompt said \"do not ask questions\" → fixed.", 0)]
    bad_cases = [c for c, n in cases if len(no_ask_hits(c)) != n]
    ok = not hits and not bad_cases
    report("NA1", ok, f"no 'decide and continue' wording in {len(files)} sprint and agent files ({len(cases)} self-test cases)"
           if ok else f"tells the executor to decide alone: {'; '.join(hits + bad_cases)} — a gap with no "
           "convention stops that card and asks (execute.md → Needs a decision)")


# ── SP9 · the sprint checker holds a sprint kept in the app to its plan steps and waves (fixtures) ─
def check_sp9():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "check_sprint.py"
    vault = ROOT / "tests" / "fixture-vault"
    good = run_script(script, "--vault", str(vault), "--domain", "Record")
    bad = run_script(script, "--vault", str(vault), "--domain", "RecordBad")
    want = ("step 3 (Close the open questions) is marked done with no evidence",
            "Wave 2 is done while Wave 1, which it depends on, is not", "Wave 2 names GA-3",
            "missing garden-sprint-summer-plan.md")
    # Record also holds a sprint still in planning (no plan or prompt yet), which must pass;
    # RecordBad's planning sprint has step 7 done with no plan, which must fail SP1.
    ok = good[0] == 0 and bad[0] == 1 and all(w in bad[1] for w in want) and bad[1].count("\n- ") == 4
    report("SP9", ok, "check_sprint passes a record sprint's steps and waves, refuses a step with no evidence, "
           "a wave done before a wave it depends on, a card outside the table, and a plan missing after step 7; a sprint still in planning passes (SP1, SP9, SP10)"
           if ok else f"fixtures: good → {good[0]} {good[1][-120:]!r}; bad → {bad[0]} {bad[1][-200:]!r}")


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
        (("opt", "handover.board"), 0, "Fixture Ops"),
        (("--file", "bandit.no-migrations.yaml", "opt", "handover.board"), 0, "none"),
        (("get", "handover.staging.runbook"), 0, "docs/staging-runbook.md#Deploy to staging"),
        (("--file", "bandit.missing-key.yaml", "require", "handover.production.runbook"), 3, "missing key `handover.production.runbook`"),
        (("--file", "bandit.no-production.yaml", "require", "release", "branches.trunk", "branches.deploy"), 0, "present"),
        (("--file", "bandit.no-production.yaml", "get", "handover.staging.column"), 0, "Fixture Lab"),
        (("--file", "bandit.no-production.yaml", "get", "handover.production.column"), 3, "missing key `handover.production.column`"),
        (("--file", "bandit.no-production.yaml", "opt", "handover.production.column"), 0, "none"),
        (("opt", "handover.production.column"), 0, "Fixture Host"),
        (("opt", "guard.credentials.block"), 0, "set-password"),
        (("--file", "bandit.no-migrations.yaml", "opt", "guard.credentials.block"), 0, "none"),
        (("opt", "stop.close"), 0, "the fixture's close step"),
        (("--file", "bandit.no-migrations.yaml", "opt", "stop.paths"), 0, "none"),
    ]
    bad = []
    for args, code, text in cases:
        got, out = run_script(script, *args, cwd=app)
        if got != code or text not in out:
            bad.append(f"{' '.join(args)} → {got} {out[-100:]!r}")
    report("Y1", not bad, "; ".join(bad) or f"recipe.py: {len(cases)} fixture cases (keys, tail, refusal by name, optional sections)")


# ── Y2 · the shipped contract lists every key the plugin reads, once ─────────
def y2_errors(keys, contract, readers):
    """keys: recipe.py KEYS · contract: the contract file's text · readers: {name: text} of plugin files."""
    section = contract.split("## 🗝️ Keys", 1)[-1].split("\n## ", 1)[0]
    listed = [m.group(1) for m in re.finditer(r"^\| `([a-z]+(?:\.[a-z]+)*)` \|", section, re.M)]
    errors = [f"`{k}` listed {listed.count(k)}×" for k in sorted(set(listed)) if listed.count(k) > 1]
    errors += [f"`{k}` in KEYS, not in the contract" for k in sorted(set(keys) - set(listed))]
    errors += [f"`{k}` in the contract, not in KEYS" for k in sorted(set(listed) - set(keys))]
    tops = {k.split(".")[0] for k in keys}
    read = set()
    for name, text in readers.items():
        if name.endswith(".md"):
            for m in re.finditer(r"recipe\.py (?:--file \S+ )?(?:get|opt|require) ([a-z. ]+)", text):
                read |= {(name, k) for k in m.group(1).split() if "." in k or k in tops}
        else:
            read |= {(name, m.group(1)) for m in re.finditer(r"[\"']([a-z]+(?:\.[a-z]+)+)[\"']", text)
                     if m.group(1).split(".")[0] in tops}
    errors += [f"{n} reads `{k}`, not in KEYS" for n, k in sorted(read) if k not in keys]
    return errors


def check_contract():
    import importlib.util
    sprint = PLUGINS / "bandit-dev" / "skills" / "sprint"
    contract = sprint / "references" / "bandit-yaml.md"
    if not contract.exists():
        return report("Y2", False, "plugins/bandit-dev/skills/sprint/references/bandit-yaml.md missing")
    spec = importlib.util.spec_from_file_location("recipe", sprint / "scripts" / "recipe.py")
    recipe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recipe)
    keys, text = recipe.KEYS, contract.read_text(encoding="utf-8")
    readers = {str(f.relative_to(PLUGINS)): f.read_text(encoding="utf-8")
               for f in sorted((PLUGINS / "bandit-dev").rglob("*"))
               if f.is_file() and f.suffix in (".md", ".py") and f.name != "recipe.py" and "__pycache__" not in f.parts}
    errors = y2_errors(keys, text, readers)
    # The rule must fail on a row dropped from the table, and on a reader of an unlisted key.
    dropped = text.replace("| `verify` |", "| verify |", 1)
    if not y2_errors(keys, dropped, readers) or not y2_errors(keys, text, {"x.md": "`recipe.py get branches.nope`"}):
        errors.append("self-test: Y2 did not fail on a dropped row or an unlisted reader key")
    # The app's proposed recipe in docs/bandit-yaml.md must itself be a recipe the reader can load.
    example = re.search(r"```yaml\n(.*?)```", (ROOT / "docs" / "bandit-yaml.md").read_text(encoding="utf-8"), re.S)
    try:
        if not example or not isinstance(recipe.parse_text(example.group(1)), dict):
            errors.append("docs/bandit-yaml.md has no yaml example")
    except recipe.RecipeError as e:
        errors.append(f"docs/bandit-yaml.md example: {e}")
    report("Y2", not errors, "; ".join(errors) or f"contract lists the {len(keys)} keys once; every key "
           f"read in {len(readers)} plugin files is listed; the app's example parses")


def clean_env(**extra):
    """os.environ without git's own variables: under the pre-commit hook GIT_INDEX_FILE and GIT_DIR point
    at this repo, and a fixture's git command would write into its index."""
    return {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, **extra}


def run_hook(script, payload, project, env_extra=None):
    env = clean_env(CLAUDE_PROJECT_DIR=str(project), **(env_extra or {}))
    r = subprocess.run([sys.executable, "-B", str(script)], input=json.dumps(payload),
                       capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


# ── CG1 · the credential guard refuses a credential write and lets the allowed dev login run ───────
def check_credential_guard():
    import shutil as sh
    import tempfile
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "credential_guard.py"
    fixture = ROOT / "tests" / "fixture-app" / "bandit.yaml"
    bash = lambda c: {"tool_name": "Bash", "tool_input": {"command": c}}  # noqa: E731
    bad = []
    with tempfile.TemporaryDirectory() as d:
        on, off, none, broken, broad = (Path(d) / n for n in ("on", "off", "none", "broken", "broad"))
        for p in (on, off, none, broken, broad):
            p.mkdir()
        sh.copy(fixture, on / "bandit.yaml")
        (off / "bandit.yaml").write_text("verify: 'true'\nbranches: { trunk: a, deploy: b }\nrelease: [x]\n")
        (broken / "bandit.yaml").write_text("guard:\n  credentials: [unclosed\n")
        (broad / "bandit.yaml").write_text("guard:\n  credentials:\n    block: ['(?i)password_hash\\s*=']\n"
                                           "    allow: ['python3 .*']\n")
        cases = [
            (on, "psql -c \"UPDATE users SET password_hash = 'x'\"", 2, "guard.credentials.block"),
            (on, "python3 scripts/set-password.py someone", 2, "set-password"),
            (on, "python3 scripts/set-dev-passwords.py", 0, ""),
            (on, "python3 scripts/set-dev-passwords.py; psql -c 'update u set password_hash = 1'", 2, "Blocked"),
            (broad, "python3 x.py && psql -c 'update u set password_hash = 1'", 2, "Blocked"),
            (on, "git status", 0, ""),
            (off, "psql -c 'update u set password_hash = 1'", 0, ""),
            (none, "psql -c 'update u set password_hash = 1'", 0, ""),
            (broken, "git status", 2, "cannot read bandit.yaml"),
        ]
        for project, command, code, text in cases:
            got, out = run_hook(script, bash(command), project)
            if got != code or text not in out:
                bad.append(f"{project.name}: {command[:40]!r} → {got} {out[-90:]!r}")
    report("CG1", not bad, "; ".join(bad) or f"credential guard: {len(cases)} fixture cases (refused with the "
           "reason, allowed dev login runs, chained and broad-allow writes refused, off without a section, "
           "fails closed on a broken recipe)")


# ── SG1 · the stop gate holds a chat with uncommitted implementation changes, not a clean or docs-only one ─
def check_stop_gate():
    import tempfile
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "stop_gate.py"
    bad = []
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d) / "repo"
        (repo / "src").mkdir(parents=True)
        (repo / "docs").mkdir()
        recipe_text = "verify: 'true'\nstop:\n  paths: [src]\n  close: /close-round\n"
        (repo / "bandit.yaml").write_text(recipe_text)
        (repo / "src" / "a.py").write_text("a = 1\n")
        (repo / "docs" / "x.md").write_text("x\n")
        git = lambda *a: subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *a],  # noqa: E731
                                        capture_output=True, text=True, check=True, env=clean_env())
        git("init", "-q")
        git("add", "-A")
        git("commit", "-qm", "start")

        def transcript(name, *tools):
            t = Path(d) / f"{name}.jsonl"
            t.write_text("".join(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": n, "input": i}]}}) + "\n" for n, i in tools))
            return str(t)

        def case(label, code, text="", **payload):
            got, out = run_hook(script, payload, repo)
            if got != code or text not in out:
                bad.append(f"{label} → {got} {out[-90:]!r}")

        case("clean tree", 0)
        (repo / "docs" / "x.md").write_text("y\n")
        case("docs-only change", 0)
        (repo / "src" / "a.py").write_text("a = 2\n")
        case("src change", 2, "/close-round")
        case("src change, stop_hook_active", 0, stop_hook_active=True)
        agent = ("Agent", {"prompt": "wave"})
        case("src change by a background agent", 0, transcript_path=transcript("t1", agent))
        case("own edit, absolute path", 2, "src/a.py",
             transcript_path=transcript("t2", ("Task", {}), ("Edit", {"file_path": str(repo / "src" / "a.py")})))
        git("add", "-A")
        git("commit", "-qm", "two")
        git("mv", "src/a.py", "src/b.py")
        case("own rename, relative path", 2, "src/b.py",
             transcript_path=transcript("t3", agent, ("Write", {"file_path": "src/b.py"})))
        (repo / "bandit.yaml").write_text("verify: 'true'\n")
        case("no stop section", 0)
        (repo / "bandit.yaml").write_text("stop:\n  paths: [unclosed\n")
        case("broken recipe", 0, "not checked")
        (repo / "bandit.yaml").write_text(recipe_text)
        case("no transcript, rename staged", 2, "src/b.py")
    report("SG1", not bad, "; ".join(bad) or "stop gate: 10 fixture cases (src change held with the close step, "
           "clean and docs-only pass, a background agent's files pass, own edits by absolute path and rename "
           "held, stop_hook_active, no section and a broken recipe pass)")


# ── DG1 · a card made to block another tells the session which gate sub-task it owes ─────────────
def check_dependency_gate():
    script = PLUGINS / "bandit-dev" / "skills" / "sprint" / "scripts" / "dependency_gate.py"
    ok_text = [{"type": "text", "text": json.dumps({"ok": True, "applied": 1, "results": [{"ok": True, "shortId": "XY-9"}]})}]
    link = {"tool_name": "mcp__board__link_tasks", "tool_input": {"blockerTaskId": "AB-1", "blockedTaskId": "AB-2"},
            "tool_response": {"ok": True}}
    create = lambda item, resp=ok_text: {"tool_name": "mcp__other_board__create_tasks",  # noqa: E731
                                         "tool_input": {"items": [item]}, "tool_response": resp}
    cases = [
        ("link", link, ["AB-1 now blocks AB-2", "Skip if a gate for this blocker already exists", "sprint card blocked by its"]),
        ("refused link", {**link, "tool_response": {"ok": False, "code": "CYCLE"}}, None),
        ("create blockedBy", create({"title": "New", "dependencies": {"blockedBy": ["AB-1"]}}), ["AB-1 now blocks XY-9"]),
        ("create blocks", create({"title": "New", "dependencies": {"blocks": ["AB-3"]}}), ["XY-9 now blocks AB-3"]),
        ("create a design card", create({"title": "Design: New screen", "dependencies": {"blocks": ["AB-4"]}}),
         ["XY-9 (a design card) now blocks AB-4", "the design handover is linked and approved", "before AB-4 gets stage/spec"]),
        ("create with its gate", create({"title": "New", "dependencies": {"blockedBy": ["AB-1"]},
                                         "subtasks": ["Build it", "Gate: AB-1 delivered (the API) before deploy"]}), None),
        ("sprint card", create({"title": "Sprint 2026-w01", "dependencies": {"blockedBy": ["AB-1", "AB-2"]}}), None),
        ("refused create", create({"title": "New", "dependencies": {"blockedBy": ["AB-1"]}},
                                  {"ok": True, "results": [{"ok": False, "code": "CYCLE"}]}), None),
        ("no link", create({"title": "New"}), None),
        ("another tool", {**link, "tool_name": "mcp__board__update_tasks"}, None),
        ("link to a sprint", {**link, "tool_input": {"blockerTaskId": "AB-1", "blockedSprintId": "sp-2"}},
         ["AB-1 now blocks sprint sp-2", "ledger, section Gates"]),
        ("create blocked by a sprint", create({"title": "New", "dependencies": {"blockedBySprints": ["sp-1"]}}),
         ["sprint sp-1 now blocks XY-9: add to XY-9 a sub-task"]),
    ]
    bad = []
    for label, payload, want in cases:
        r = subprocess.run([sys.executable, "-B", str(script)], input=json.dumps(payload), capture_output=True, text=True)
        if r.returncode != 0:
            bad.append(f"{label} → exit {r.returncode}")
            continue
        if want is None:
            if r.stdout.strip():
                bad.append(f"{label} → notice {r.stdout[:80]!r}, expected silence")
            continue
        try:
            out = json.loads(r.stdout)["hookSpecificOutput"]
        except (ValueError, KeyError, TypeError):
            bad.append(f"{label} → no hookSpecificOutput: {r.stdout[:80]!r}")
            continue
        missing = [w for w in want if w not in out.get("additionalContext", "")]
        if out.get("hookEventName") != "PostToolUse" or missing:
            bad.append(f"{label} → missing {missing or out.get('hookEventName')}")
    report("DG1", not bad, "; ".join(bad) or f"dependency gate: {len(cases)} fixture payloads (notice in the "
           "session's context naming the blocked card or sprint and the skip line; silent on refusals, a created card "
           "with its gate, sprint cards and other tools)")


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
    check_bridge_names()
    check_board_type()
    check_app_tools()
    check_copies()
    check_changelog_entry()
    check_cheat_sheet()
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
    check_sp9()
    check_no_decide_and_continue()
    check_execution_by_date()
    check_debug_push()
    check_design_card()
    check_wave_flow()
    check_sp11()
    check_design_handover()
    check_gate_order()
    check_dev_mirror()
    check_sprint_map()
    check_sp12()
    check_sp13()
    check_app_compat()
    check_wave_order()
    check_debug_card()
    check_design_link()
    check_design_sync()
    check_tag_creation()
    check_approval_line()
    check_recipe()
    check_contract()
    check_credential_guard()
    check_stop_gate()
    check_dependency_gate()
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
