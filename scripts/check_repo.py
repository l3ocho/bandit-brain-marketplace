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
    if top == "Unreleased":
        same = len(set(versions.values())) == 1
        return report("V1", same, f"top entry Unreleased; plugin versions {versions}")
    bad = {k: v for k, v in versions.items() if v != top}
    report("V1", not bad, f"versions ≠ CHANGELOG {top}: {bad}" if bad else f"all plugins at {top} = CHANGELOG")


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


def main(argv):
    use_cli = "--no-cli" not in argv
    check_manifests()
    check_validate(use_cli)
    check_no_bin()
    check_versions()
    check_g6()
    check_denylist()
    check_r15()
    check_guard_pin()
    for rule, ok, msg in results:
        print(f"{'✅' if ok else '❌'} {rule} {msg}")
    failed = [r for r, ok, _ in results if not ok]
    print(f"check_repo: FAIL ({', '.join(failed)})" if failed
          else f"check_repo: OK ({len(results)} rules)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
