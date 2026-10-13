#!/usr/bin/env python3
"""Score Leo's domains against the structure rules (S1–S16).

Usage:
  check_structure.py --rules structure-rules.yaml --rulebook structure-rulebook.md \
      --snapshot snapshot.json [--domain D ...] [--project D/slug] [--out DIR]
  check_structure.py --replay report.md --rules ... --rulebook ... --snapshot ...
  check_structure.py --project Personal/ai-fran --rules ... --rulebook ... --snapshot ...
      (one project only, for /bandit:audit check: its rows, no domain block, nothing written)

Same inputs → same bytes. Exit 0 = scored, 2 = an input broke its contract
(nothing scored), 3 = replay mismatch (the report is not what these inputs produce).
The model never scores by hand: it builds the snapshot, runs this, and shows the output.
"""
import argparse, datetime, hashlib, json, re, sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML missing: pip install pyyaml")

SCRIPT_VERSION = "5"
S5_ORDER = ["no_stamp", "stamp_matches_newest", "stamp_matches_older",
            "stamp_newer_than_all", "stamp_before_newest_file_date", "otherwise"]
MARK = {"ok": "✅", "warn": "⚠️", "fail": "❌", "na": "—", "unchecked": "unchecked"}


class ContractError(Exception):
    pass


# ───────────────────────── inputs and contracts ─────────────────────────
def sha12(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def load_rules(path, rulebook_path):
    raw = Path(path).read_bytes()
    rules = yaml.safe_load(raw)
    for key in ("schema", "rulebook_updated", "levels", "names", "workflow",
                "project_context", "settings_files", "owners", "row_order", "s9",
                "surfaces", "s10", "s11", "s12", "vault_content"):
        if key not in rules:
            raise ContractError(f"rules: missing key `{key}`")
    # Parts of the rules that are logic, not settings: the script implements them in code,
    # so a change in the YAML without a script update is refused rather than ignored.
    if [c.get("when") for c in rules.get("s5", [])] != S5_ORDER:
        raise ContractError("rules.s5 order differs from what this script implements: update the script too")
    pc = rules["project_context"]
    if pc.get("optional_keys", []) != ["dev"] or pc.get("dev_values") != ["true"]:
        raise ContractError("rules.project_context optional_keys/dev_values changed: update the script too")
    for k in ("lane_tags", "stage_tags", "first_lane_tag"):
        if k not in rules["s9"]:
            raise ContractError(f"rules.s9: missing `{k}`")
    if not rules["s9"]["lane_tags"] or rules["s9"]["first_lane_tag"] != rules["s9"]["lane_tags"][0]:
        raise ContractError("rules.s9.first_lane_tag must be the first of lane_tags")
    for blk, keys in (("surfaces", ("twin_files", "mirror_files", "mirror_dir", "forbidden")),
                      ("s10", ("file", "environment_heading")),
                      ("s11", ("required_files", "settings_file", "hook_event", "hook_script")),
                      ("s12", ("hook_file", "hook_sha12", "settings_file", "hook_events", "hook_script",
                               "manifest", "manifest_max_age_days", "root_allowed", "task_dirs",
                               "task_folder_pattern", "data_extensions", "retention_days",
                               "backup_dir", "backup_name_pattern")),
                      ("vault_content", ("sprint_folder_pattern", "sprint_tag_prefix", "planning_dir",
                                         "brief_type", "unique_exempt", "unique_scope"))):
        for k in keys:
            if k not in rules[blk]:
                raise ContractError(f"rules.{blk}: missing `{k}`")
    for k in ("twin_update", "dev_mirror", "surface_folder", "workdir_guard", "workdir_fix",
              "brief_move", "duplicate_name", "frontmatter_fix", "root_move"):
        if k not in rules["owners"]:
            raise ContractError(f"rules.owners: missing `{k}`")
    for r in ("S13", "S14", "S15", "S16"):
        if r not in rules["levels"]:
            raise ContractError(f"rules.levels: missing `{r}`")
    if rules["vault_content"]["unique_scope"] != ["_inbox", "Projects"]:
        raise ContractError("rules.vault_content.unique_scope changed: update the script and the snapshot too")
    if rules.get("s7", {}).get("prompt_reference_keep") != "highest":
        raise ContractError("rules.s7.prompt_reference_keep changed: update the script too")
    m = re.search(r"^updated:\s*(\S+)", Path(rulebook_path).read_text(), re.M)
    if not m:
        raise ContractError("rulebook: no `updated:` in frontmatter")
    if str(rules["rulebook_updated"]) != m.group(1):
        raise ContractError(f"rules say rulebook_updated {rules['rulebook_updated']}, "
                            f"rulebook says {m.group(1)}: update both in one proposal")
    return rules, sha12(raw)


def load_snapshot(path):
    raw = Path(path).read_bytes()
    s = json.loads(raw)
    errs = []
    need = lambda cond, msg: None if cond else errs.append(msg)
    need(s.get("schema") in (1, 2, 3, 4, 5), "snapshot.schema must be 1, 2, 3, 4 or 5")
    need(isinstance(s.get("taken_at"), str), "snapshot.taken_at missing")
    b, v = s.get("board", {}), s.get("vault", {})
    need(isinstance(b.get("folders"), list), "board.folders must be a list")
    need(isinstance(b.get("projects"), list), "board.projects must be a list")
    for i, p in enumerate(b.get("projects", [])):
        for k in ("name", "type", "folder", "visibility", "system_owner"):
            need(k in p, f"board.projects[{i}] missing `{k}`")
    if s.get("schema", 0) >= 2:
        need(isinstance(s.get("tags"), list) and all(isinstance(x, str) for x in s.get("tags", [])),
             "tags must be a list of tag names (schema 2)")
        for i, p in enumerate(b.get("projects", [])):
            need(isinstance(p.get("lanes"), list), f"board.projects[{i}].lanes must be a list (schema 2)")
            for j, ln in enumerate(p.get("lanes") or []):
                for k in ("name", "position", "matcher"):
                    need(k in ln, f"board.projects[{i}].lanes[{j}] missing `{k}`")
                m = ln.get("matcher") or {}
                need("field" in m and isinstance(m.get("values"), list),
                     f"board.projects[{i}].lanes[{j}].matcher needs `field` and `values`")
    for i, f in enumerate(b.get("folders", [])):
        for k in ("name", "parent"):
            need(k in f, f"board.folders[{i}] missing `{k}`")
    need(isinstance(v.get("domains"), list), "vault.domains must be a list")
    need(isinstance(v.get("settings"), dict), "vault.settings must be an object")
    for dom, folders in v.get("settings", {}).items():
        for fname, fd in folders.items():
            need(isinstance(fd.get("entries"), list), f"vault.settings.{dom}.{fname}.entries missing")
            need(isinstance(fd.get("instructions"), dict), f"vault.settings.{dom}.{fname}.instructions missing")
            listed = {e["name"] for e in fd.get("entries", [])}
            for file in fd.get("instructions", {}):
                need(file in listed, f"vault.settings.{dom}.{fname}: {file} read but not in the listing")
    if s.get("schema", 0) >= 3:
        for dom, folders in v.get("settings", {}).items():
            for fname, fd in folders.items():
                for file, meta in (fd.get("instructions") or {}).items():
                    need(isinstance(meta.get("text"), str),
                         f"vault.settings.{dom}.{fname}.instructions[{file}].text missing (schema 3)")
        need(isinstance(v.get("surfaces"), dict), "vault.surfaces must be an object (schema 3)")
        for dom, folders in (v.get("surfaces") or {}).items():
            for fname, fd in folders.items():
                need(fname.startswith(("code-", "design-")), f"vault.surfaces.{dom}.{fname}: not a code-/design- folder")
                need(isinstance(fd.get("entries"), list), f"vault.surfaces.{dom}.{fname}.entries missing")
                need(isinstance(fd.get("files"), dict) and all(isinstance(t, str) for t in (fd.get("files") or {}).values()),
                     f"vault.surfaces.{dom}.{fname}.files must map names to text")
                listed = {e["name"] for e in fd.get("entries", [])}
                for file in fd.get("files") or {}:
                    need(file in listed, f"vault.surfaces.{dom}.{fname}: {file} read but not in the listing")
                repo = fd.get("repo")
                need(repo is None or (isinstance(repo, dict) and isinstance(repo.get("pushed_at"), str)
                                      and isinstance(repo.get("name"), str)),
                     f"vault.surfaces.{dom}.{fname}.repo must be null or {{name, pushed_at}}")
                if s.get("schema") >= 4:
                    need("workdir" in fd, f"vault.surfaces.{dom}.{fname}.workdir missing (schema 4: null when no manifest)")
                    wd = fd.get("workdir")
                    if wd is not None:
                        ok = (isinstance(wd, dict) and wd.get("schema") == 1 and isinstance(wd.get("generated_at"), str)
                              and all(isinstance(wd.get(k), list) for k in ("root", "hosted", "loose", "scratch", "misplaced_data", "backup"))
                              and isinstance(wd.get("task_folders"), dict)
                              and all(isinstance(v, list) for v in wd["task_folders"].values())
                              and isinstance(wd.get("truncated"), bool))
                        need(ok, f"vault.surfaces.{dom}.{fname}.workdir isn't a schema-1 manifest")
    if s.get("schema", 0) >= 5:
        sc = b.get("sprint_cards")
        need(isinstance(sc, list) and all(isinstance(c, dict) and isinstance(c.get("id"), str)
                                          and (c.get("short_id") is None or isinstance(c.get("short_id"), str))
                                          and isinstance(c.get("sprints"), list) for c in (sc or [])),
             "board.sprint_cards must be a list of {id, short_id, sprints} (schema 5)")
        need(isinstance(v.get("projects"), dict), "vault.projects must be an object (schema 5)")
        need(isinstance(v.get("inbox"), dict), "vault.inbox must be an object (schema 5)")
        for dom, names in (v.get("inbox") or {}).items():
            need(isinstance(names, list) and all(isinstance(n, str) for n in names),
                 f"vault.inbox.{dom} must be a list of filenames")
        for dom, projs in (v.get("projects") or {}).items():
            for slug_, pd in projs.items():
                ev_ = f"vault.projects.{dom}.{slug_}"
                need(isinstance(pd.get("entries"), list), f"{ev_}.entries missing")
                need(isinstance(pd.get("frontmatter"), dict), f"{ev_}.frontmatter missing (an empty object when none was read)")
                listed = {e.get("name"): e.get("dir") for e in pd.get("entries") or []}
                for f, raw_ in (pd.get("frontmatter") or {}).items():
                    need(listed.get(f) is False, f"{ev_}: frontmatter of `{f}` read but `{f}` not listed as a file")
                    need(raw_ is None or isinstance(raw_, str), f"{ev_}.frontmatter[{f}] must be text or null")
                sprinty = any(e.get("dir") and "/" not in e.get("name", "") and e["name"].startswith("sprint-")
                              for e in pd.get("entries") or [])
                if sprinty:
                    for f, is_dir in listed.items():
                        if not is_dir and f.endswith(".md"):
                            need(f in (pd.get("frontmatter") or {}),
                                 f"{ev_}: sprint project, but the frontmatter of `{f}` wasn't read (schema 5 reads every note)")
    need(isinstance(s.get("stamps"), dict), "stamps must be an object (empty if the ledger is missing)")
    folder_names = {f.get("name") for f in b.get("folders", [])}
    for i, p in enumerate(b.get("projects", [])):
        need(p.get("folder") in folder_names or p.get("folder") is None,
             f"board.projects[{i}] folder `{p.get('folder')}` not in board.folders")
    if errs:
        raise ContractError("snapshot: " + "; ".join(errs))
    return s, sha12(raw)


# ───────────────────────── helpers ─────────────────────────
def slug(name):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


def vtoken(line):
    return line.split()[0] if line and line.split() else None


def vkey(tok):
    parts = re.findall(r"\d+", tok or "")
    return tuple(int(p) for p in parts) if parts else (-1,)


def parse_board(value):
    """`project "X"` → ("project", "X"); `none` → ("none", None)."""
    if value is None:
        return (None, None)
    m = re.fullmatch(r'(project|folder)\s+"(.+)"', value.strip())
    if m:
        return (m.group(1), m.group(2))
    return (value.strip(), None)


def vnum(filename):
    m = re.search(r"-v(\d+)\.md$", filename)
    return int(m.group(1)) if m else None


def version_of(text):
    m = re.search(r"^\*\*Version:\*\*\s*(.*)$", text, re.M)
    return vtoken(m.group(1)) if m else None


def core_sha(text, heading):
    """sha12 of the text with the `heading` section (up to the next `## ` heading) removed."""
    out, skip = [], False
    for line in text.split("\n"):
        if line.rstrip() == heading:
            skip = True
            continue
        if skip and line.startswith("## "):
            skip = False
        if not skip:
            out.append(line)
    return sha12("\n".join(out).encode("utf-8"))


class Row:
    def __init__(self, action, target, owner, rule, pair=None):
        self.action, self.target, self.owner, self.rule, self.pair = action, target, owner, rule, pair


# ───────────────────────── scoring ─────────────────────────
class Domain:
    def __init__(self, name, snap, rules):
        self.name, self.snap, self.rules = name, snap, rules
        self.L = name[0]
        self.levels = rules["levels"]
        folders = snap["board"]["folders"]
        self.top = next((f for f in folders if f["name"] == name and f["parent"] is None), None)
        sub = {f["name"] for f in folders if f["parent"] == name}
        allp = snap["board"]["projects"]
        self.system = sorted(p["name"] for p in allp
                             if p["system_owner"] and (p["folder"] == name or p["folder"] in sub))
        self.boards = sorted([p for p in allp if not p["system_owner"]
                              and (p["folder"] == name or p["folder"] in sub)], key=lambda p: p["name"])
        self.all_board_names = {p["name"]: p for p in allp}
        self.projects = []
        self.domain_results = []
        self.rows = []
        self.unchecked = []
        self.claimed = set()
        self.surfaces = snap["vault"].get("surfaces", {}).get(name, {}) if snap["schema"] >= 3 else {}
        self.vprojects = snap["vault"].get("projects", {}).get(name, {}) if snap["schema"] >= 5 else {}
        self.sprint_of = {}
        for c in (snap["board"].get("sprint_cards") or []) if snap["schema"] >= 5 else []:
            for key in (c["id"], (c.get("short_id") or "").upper()):
                if key:
                    self.sprint_of[key] = sorted(c["sprints"])

    def res(self, rule, status, note, evidence):
        if status == "bad":
            status = "fail" if self.levels[rule] == "must" else "warn"
        return {"rule": rule, "status": status, "note": note, "evidence": evidence}

    def score(self):
        s = self.snap
        settings = s["vault"]["settings"].get(self.name, {})
        stamps = s["stamps"]
        for folder in sorted(settings):
            self.projects.append(self.score_project(folder, settings[folder], stamps))
        # stamped projects with no vault folder
        known = {f"MyNotes/{self.name}/Claude/{f}" for f in settings}
        for key in sorted(stamps):
            st = stamps[key]
            if key.split("/")[0] == self.name and st.get("folder") not in known:
                self.unchecked.append(f"{key}: stamped ({st.get('claude_name')}) but `{st.get('folder')}` "
                                      f"is not in the vault → S6 finding")
                self.domain_results.append(self.res("S6", "bad",
                    f"Stamp `{key}` points to `{st.get('folder')}`, which doesn't exist",
                    f"stamps.{key}.folder"))
                self.rows.append(Row(f"Decide: create the settings folder for `{key}` or drop its stamp",
                                     st.get("folder"), self.rules["owners"]["decide"], "S6"))
        slugs = {f[3:] for f in settings if f.startswith("ai-")}
        for ps in sorted(self.vprojects):
            if ps not in slugs and self.is_sprint_project(self.vprojects[ps]):
                self.unchecked.append(f"Projects/{ps}/: sprint folders but no `ai-{ps}/` project → S13, S15, S16 not scored")
        for sf in sorted(self.surfaces):
            if sf.split("-", 1)[1] not in slugs:
                self.unchecked.append(f"{sf}: no `ai-{sf.split('-', 1)[1]}/` project → surface not scored")
        self.score_domain()
        return self

    # ---------- per project ----------
    def score_project(self, folder, fd, stamps):
        prod = self._project(folder, fd, stamps, use_newest=False)
        if prod["newest_pending"]:
            alt = self._project(folder, fd, stamps, use_newest=True)
            alt_status = {r["rule"]: r["status"] for r in alt["results"]}
            fixed = set()
            for r in prod["results"]:
                if r["rule"] in ("S1", "S2", "S3", "S4", "S6", "S8", "S9") and r["status"] in ("fail", "warn") \
                        and alt_status.get(r["rule"]) in ("ok", "na"):
                    r["status"] = "warn"
                    r["note"] += f" — fixed in `{prod['newest_pending']}`, paste pending"
                    fixed.add(r["rule"])
            prod["rows"] = [row for row in prod["rows"] if row.rule not in fixed]
            prod["wf_after_paste"] = alt["is_wf"]
        self.rows += prod["rows"]
        self.unchecked += prod["unchecked"]
        if prod["mine"]:
            self.claimed.add(prod["mine"])
        return prod

    def _project(self, folder, fd, stamps, use_newest):
        R, rows, unchecked = [], [], []
        ev = f"vault.settings.{self.name}.{folder}"
        files = {}
        for name, meta in fd["instructions"].items():
            files[name] = {"n": vnum(name), "tok": vtoken(meta["version_line"]), "ctx": meta["context"]}
        dates = {e["name"]: e["modified"] for e in fd["entries"]}
        path = f"MyNotes/{self.name}/Claude/{folder}"
        stamp_key, stamp = None, None
        for k in sorted(stamps):
            if stamps[k].get("folder") == path:
                stamp_key, stamp = k, stamps[k]
        if stamp is None:
            projs = {f["ctx"]["project"] for f in files.values() if f["ctx"]}
            for p in sorted(projs):
                k = f"{self.name}/{p}"
                if k in stamps:
                    stamp_key, stamp = k, stamps[k]
        by_n = sorted(files.items(), key=lambda kv: (kv[1]["n"] if kv[1]["n"] is not None else -1))
        newest = by_n[-1] if by_n else None
        prod = None
        if stamp:
            matches = [kv for kv in by_n if kv[1]["tok"] == str(stamp["version"])]
            prod = matches[-1] if matches else None
        chosen = newest if use_newest else (prod or newest)
        pending = newest[0] if (stamp and prod and newest and prod[0] != newest[0]) else None
        ctx = chosen[1]["ctx"] if chosen else None
        title = (stamp or {}).get("claude_name") or folder

        # ── S5 ──
        s5 = None
        if not stamp:
            s5 = self.res("S5", "unchecked", "No stamp", "stamps")
            unchecked.append(f"{folder}: no stamp → run `/bandit:audit check` inside it")
        elif prod and prod[0] == newest[0]:
            s5 = self.res("S5", "ok", f"Runs {stamp['version']} = `{prod[0]}`", f"stamps.{stamp_key}")
        elif prod:
            s5 = self.res("S5", "warn", f"Vault `{newest[0]}` ({newest[1]['tok']}) not pasted yet; "
                          f"Claude.ai runs {stamp['version']}", f"stamps.{stamp_key}")
            rows.append(Row(f"Paste `{newest[0]}` into {title}, then run `/bandit:audit check` there",
                                 f"{path}/{newest[0]}", self.rules["owners"]["self_check"], "S5"))
        elif newest and vkey(str(stamp["version"])) > max(vkey(f["tok"]) for f in files.values()):
            s5 = self.res("S5", "bad", f"Critical: Claude.ai runs {stamp['version']}, newer than every vault file",
                          f"stamps.{stamp_key}")
            rows.append(Row("Recover the vault copy of the running instructions", path,
                                 self.rules["owners"]["decide"], "S5"))
        elif newest and stamp.get("checked", "") < max(dates.get(n, "") for n in files):
            s5 = self.res("S5", "unchecked", f"Stamp {stamp['version']} ({stamp.get('checked')}) is older than "
                          f"the newest file and matches none", f"stamps.{stamp_key}")
            unchecked.append(f"{folder}: stamp {stamp['version']} matches no file → run `/bandit:audit check` inside it")
        else:
            s5 = self.res("S5", "warn", f"Drift: stamp {stamp['version']}, vault newest {newest[1]['tok'] if newest else '—'}",
                          f"stamps.{stamp_key}")
        s5_known = s5["status"] in ("ok", "warn") and prod is not None

        # ── S4 ──
        pc = self.rules["project_context"]
        board_kind, board_name = parse_board(ctx.get("board")) if ctx else (None, None)
        s4_board_problems = []
        if ctx is None:
            R.append(self.res("S4", "bad", f"No Project Context in `{chosen[0] if chosen else '—'}`", ev))
            rows.append(Row("Add the Project Context block", path, self.rules["owners"]["context_update"], "S4"))
        else:
            problems = [f"missing `{k}`" for k in pc["required_keys"] if not ctx.get(k)]
            if ctx.get("domain") and ctx["domain"] != self.name:
                problems.append(f"domain `{ctx['domain']}` ≠ `{self.name}`")
            if ctx.get("type") and ctx["type"] not in pc["types"]:
                problems.append(f"type `{ctx['type']}` unknown")
            if "dev" in ctx and ctx["dev"] not in pc["dev_values"]:
                problems.append(f"dev `{ctx['dev']}` must be `true` or absent")
            if board_kind not in pc["board_forms"]:
                problems.append(f"board form `{board_kind}` not allowed ({', '.join(pc['board_forms'])})")
            elif board_kind == "project" and board_name not in self.all_board_names:
                problems.append(f"board `{board_name}` doesn't resolve")
            R.append(self.res("S4", "bad" if problems else "ok",
                              "; ".join(problems) or f"5 required keys (+ optional `dev`), board `{ctx['board']}` resolves",
                              f"{ev}.instructions[{chosen[0]}].context"))
            s4_board_problems = [p for p in problems if p.startswith("board")]
            for p in problems:
                if not p.startswith("board"):
                    rows.append(Row(f"Project Context: {p}", path, self.rules["owners"]["context_update"], "S4"))
        if not s5_known and stamp is None:
            R[-1]["note"] += " (read from the highest v{N}: no stamp)"

        # which board is this project's?
        is_wf = bool(ctx and ctx.get("type") == self.rules["workflow"]["project_type"])
        mine = None
        if board_kind == "project" and board_name in {b["name"] for b in self.boards}:
            mine = board_name
        else:
            fslug = folder[3:] if folder.startswith("ai-") else folder
            for b in self.boards:
                bn = b["name"][:-len(self.rules["names"]["workflow_suffix"])] if b["name"].endswith(self.rules["names"]["workflow_suffix"]) else b["name"]
                if slug(bn) == fslug:
                    mine = b["name"]

        wf_rule = is_wf and self.rules["workflow"]["context_board_is_wkflw"]
        if ctx is not None and s4_board_problems and not wf_rule:
            if mine:
                rows.append(Row(f'`board:` → `project "{mine}"` ({s4_board_problems[0]})', path,
                                self.rules["owners"]["context_update"], "S4"))
            else:
                rows.append(Row(f"Decide `{folder}`'s board: an existing board or `none` ({s4_board_problems[0]})",
                                path, self.rules["owners"]["decide"], "S4"))

        # ── S1 (project part) ──
        cname = (stamp or {}).get("claude_name")
        if cname is None:
            R.append(self.res("S1", "unchecked", "Claude.ai name unknown (no stamp)", "stamps"))
        else:
            R.append(self.res("S1", "ok" if cname.startswith(self.L) else "bad",
                              f"Claude.ai `{cname}`" + ("" if cname.startswith(self.L) else f" doesn't start with {self.L}"),
                              f"stamps.{stamp_key}.claude_name"))
            if not cname.startswith(self.L):
                rows.append(Row(f"Rename Claude.ai project `{cname}` to start with `{self.L}`", cname,
                                     self.rules["owners"]["claude_rename"], "S1"))

        # ── S2 ──
        suf = self.rules["names"]["workflow_suffix"]
        if cname is None:
            R.append(self.res("S2", "unchecked", "Claude.ai name unknown (no stamp)", "stamps"))
        else:
            pre = self.rules["names"]["claude_prefix"].replace("{L}", self.L)
            name = cname[len(pre):] if cname.startswith(pre) else cname
            fslug = folder[3:] if folder.startswith("ai-") else folder
            bname = mine[:-len(suf)] if (mine and mine.endswith(suf)) else mine
            votes = {"claude": slug(name), "vault": fslug, "board": slug(bname) if bname else None}
            want_board = name + (suf if is_wf else "")
            issues = []
            if mine is None:
                issues.append("no board found")
            elif mine != want_board:
                issues.append(f"board `{mine}` ≠ `{want_board}`")
            if fslug != slug(name):
                issues.append(f"vault `{folder}` ≠ `ai-{slug(name)}`")
            R.append(self.res("S2", "bad" if issues else "ok",
                              "; ".join(issues) or f"`{name}` everywhere", f"stamps.{stamp_key}.claude_name + board + {ev}"))
            if issues:
                vals = [x for x in votes.values() if x]
                majority = max(set(vals), key=vals.count) if vals else None
                if majority and vals.count(majority) >= 2:
                    if votes["claude"] != majority:
                        rows.append(Row(f"Rename Claude.ai `{cname}` to match `{majority}` (board and vault agree)",
                                             cname, self.rules["owners"]["claude_rename"], "S2"))
                    if votes["vault"] != majority:
                        rows.append(Row(f"Rename settings folder `{folder}` → `ai-{majority}`", path,
                                             self.rules["owners"]["vault_folder_rename"], "S2"))
                    if mine and votes["board"] != majority:
                        rows.extend(self.rename_board(mine, want_board, "S2"))
                else:
                    rows.append(Row(f"Pick the one name: Claude.ai `{name}`, board `{mine}`, vault `{folder}`",
                                         path, self.rules["owners"]["decide"], "S2"))

        # ── S3 (project part: workflow board line) ──
        if is_wf and self.rules["workflow"]["context_board_is_wkflw"]:
            wf_boards = [b["name"] for b in self.boards if b["name"].endswith(suf)]
            ok = board_kind == "project" and board_name in wf_boards
            R.append(self.res("S3", "ok" if ok else "bad",
                              f"`board:` is `{ctx.get('board')}`" + ("" if ok else f", should name {wf_boards or 'the - wkflw board'}"),
                              f"{ev}.instructions[{chosen[0]}].context.board"))
            if not ok and wf_boards:
                rows.append(Row(f"`board:` → `project \"{wf_boards[0]}\"`", path,
                                     self.rules["owners"]["context_update"], "S3"))
        else:
            R.append(self.res("S3", "na", "Not the workflow project", ev))

        # ── S6 (project part) ──
        if board_kind == "none":
            R.append(self.res("S6", "ok", "Declares `board: none`", ev))
        else:
            R.append(self.res("S6", "ok" if mine else "bad", f"Board `{mine}`" if mine else "No board and no `board: none`", ev))

        # ── S8 ──
        prefix = (ctx or {}).get("prefix") or ""
        sf = self.rules["settings_files"]
        pat_i = re.compile(sf["instructions"].replace("{prefix}", re.escape(prefix)))
        pat_r = re.compile(sf["prompt_reference"].replace("{prefix}", re.escape(prefix)))
        bad = []
        if not re.fullmatch(pc["prefix_pattern"], prefix):
            bad.append(f"prefix `{prefix}` isn't 2–3 letters")
        for e in sorted(fd["entries"], key=lambda e: e["name"]):
            if e["dir"]:
                bad.append(f"subfolder `{e['name']}/`")
                continue
            base = e["name"].rsplit("/", 1)[-1]
            if not (pat_i.match(base) or pat_r.match(base)):
                bad.append(f"`{e['name']}`")
                rows.append(Row(f"Move `{e['name']}` out of the settings folder (not a settings file)",
                                     f"{path}/{e['name']}", self.rules["owners"]["vault_move"], "S8"))
        if any(e["dir"] for e in fd["entries"]):
            rows.append(Row(f"Flatten `{folder}`: settings files belong directly in it", path,
                                 self.rules["owners"]["vault_move"], "S8"))
        R.append(self.res("S8", "bad" if bad else "ok", "; ".join(bad) or "Filenames and depth OK", f"{ev}.entries"))

        # ── S7 ──
        if not s5_known:
            R.append(self.res("S7", "unchecked", "S5 not known: nothing moves", ev))
        else:
            pn = prod[1]["n"]
            olds = sorted(n for n, f in files.items() if f["n"] is not None and f["n"] < pn)
            refs = sorted([e["name"] for e in fd["entries"] if re.search(r"-prompt-reference-v\d+\.md$", e["name"])],
                          key=lambda x: vnum(x) or -1)
            olds += refs[:-1]
            R.append(self.res("S7", "bad" if olds else "ok",
                              f"{len(olds)} old version file(s)" if olds else "Only production (+ not pasted)", ev))
            for o in olds:
                rows.append(Row(f"Archive `{o}` → `_archive/Claude/{folder}/`", f"{path}/{o}",
                                     self.rules["owners"]["settings_archive"], "S7"))

        # ── S9 ──
        is_dev = bool(ctx and ctx.get("dev") == "true")
        if board_kind == "none" or mine is None:
            R.append(self.res("S9", "na", "No board of its own", ev))
        elif self.snap["schema"] < 2:
            R.append(self.res("S9", "unchecked", "Snapshot schema 1 has no lanes", "snapshot.schema"))
        else:
            probs = self.s9_problems(self.all_board_names[mine], is_dev)
            what = "dev board shape" if is_dev else "no dev lanes"
            R.append(self.res("S9", "bad" if probs else "ok", "; ".join(probs) or f"`{mine}`: {what}",
                              f"board.projects[{mine}].lanes + tags"))
            if probs and is_dev:
                rows.append(Row(f"Dev board shape on `{mine}`: {'; '.join(probs)}", f"BanditBrains project \"{mine}\"",
                                self.rules["owners"]["dev_board_shape"], "S9"))
            elif probs:
                fix = "remove them" if is_wf else "remove them, or set `dev: true`"
                rows.append(Row(f"`{mine}` has dev lanes without `dev: true`: {fix}",
                                f"BanditBrains project \"{mine}\"", self.rules["owners"]["decide"], "S9"))

        # ── surfaces: S8 (code-{slug}/ per kind), S10, S11 ──
        fslug = folder[3:] if folder.startswith("ai-") else folder
        code_name = f"code-{fslug}"
        code = self.surfaces.get(code_name)
        cpath = f"MyNotes/{self.name}/Claude/{code_name}"
        sfr, s10r, s11r = self.rules["surfaces"], self.rules["s10"], self.rules["s11"]
        own = self.rules["owners"]
        schema3 = self.snap["schema"] >= 3
        if code is not None:
            s8 = next(r for r in R if r["rule"] == "S8")
            allowed = set()
            if not is_dev:  # Claude Code twin: any project without `dev: true`
                allowed |= set(sfr["twin_files"])
                allowed |= {f.rsplit("/", 1)[0] for f in sfr["twin_files"] if "/" in f}
            if is_dev:
                allowed |= set(sfr["mirror_files"])
            mdir = sfr["mirror_dir"]
            hard, soft = [], []
            for e in sorted(code["entries"], key=lambda e: e["name"]):
                n = e["name"]
                top, base = n.split("/", 1)[0], n.rsplit("/", 1)[-1]
                if top in sfr["forbidden"] or base in sfr["forbidden"]:
                    if top == ".claude" and n != ".claude":
                        continue  # reported once, on the folder itself
                    hard.append(f"`{code_name}/{n}`")
                    if base == "settings.local.json":
                        rows.append(Row(f"Remove `{n}` from the vault (a local secrets file, never mirrored)",
                                        f"{cpath}/{n}", own["decide"], "S8"))
                    else:
                        rows.append(Row(f"Rename `{n}/` → `{mdir}/` (Obsidian hides dot-folders)",
                                        f"{cpath}/{n}", own["vault_folder_rename"], "S8"))
                elif n in allowed or (is_dev and (n == mdir or n.startswith(mdir + "/"))):
                    continue
                else:
                    soft.append(f"`{code_name}/{n}`")
                    if not e["dir"]:
                        rows.append(Row(f"Move `{n}` out of `{code_name}/` (not a settings file)",
                                        f"{cpath}/{n}", own["vault_move"], "S8"))
            if hard or soft:
                extra = "; ".join(hard + soft)
                s8["note"] = extra if s8["status"] == "ok" else s8["note"] + "; " + extra
                if hard:
                    s8["status"] = "fail"
                elif s8["status"] == "ok":
                    s8["status"] = "warn"

        # S10 · Claude Code twin (any project without `dev: true`)
        if is_dev:
            R.append(self.res("S10", "na", "Dev project: its Claude Code surface is the dev mirror (S11)", ev))
        elif not schema3:
            R.append(self.res("S10", "unchecked", f"Snapshot schema {self.snap['schema']} has no surfaces", "snapshot.schema"))
        elif code is None:
            R.append(self.res("S10", "na", f"No `{code_name}/`: no Claude Code surface", ev))
        elif s10r["file"] not in code["files"]:
            R.append(self.res("S10", "bad", f"`{code_name}/{s10r['file']}` missing", f"vault.surfaces.{self.name}.{code_name}"))
            rows.append(Row(f"Write the Claude Code twin `{s10r['file']}` at production version", cpath,
                            own["twin_update"], "S10"))
        elif not s5_known:
            R.append(self.res("S10", "unchecked", "S5 not known: no production version to compare", ev))
        else:
            h = s10r["environment_heading"]
            ttext = code["files"][s10r["file"]]
            tv = version_of(ttext)
            pv = prod[1]["tok"]
            ptext = fd["instructions"][prod[0]]["text"]
            tcore, pcore = core_sha(ttext, h), core_sha(ptext, h)
            sev = f"vault.surfaces.{self.name}.{code_name}.files[{s10r['file']}]"
            if tv == pv and tcore == pcore:
                R.append(self.res("S10", "ok", f"Twin at {tv}, core `{tcore}` matches `{prod[0]}`", sev))
            elif tv == pv:
                R.append(self.res("S10", "bad", f"Same version {tv}, core differs: twin `{tcore}` ≠ `{prod[0]}` `{pcore}`", sev))
                rows.append(Row(f"Reconcile the twin cores at {tv}: Leo says which copy is right, then the other is rewritten",
                                cpath + "/" + s10r["file"], own["twin_update"], "S10"))
            elif pending and tv == newest[1]["tok"]:
                R.append(self.res("S10", "warn", f"Twin at {tv} = `{newest[0]}`: paste pending (S5)", sev))
            elif tv is not None and vkey(tv) < vkey(pv):
                R.append(self.res("S10", "warn", f"Twin at {tv}, production {pv}: not applied yet", sev))
                rows.append(Row(f"Update the Claude Code twin to {pv} (`{prod[0]}`)", cpath + "/" + s10r["file"],
                                own["twin_update"], "S10"))
            else:
                R.append(self.res("S10", "warn", f"Twin at {tv or 'no **Version:**'}, production {pv}: "
                                  "twin matches no vault version", sev))
                rows.append(Row(f"Twin version {tv or 'missing'} vs production {pv}: Leo says which is right",
                                cpath + "/" + s10r["file"], own["twin_update"], "S10"))

        # S11 · dev mirror
        if not is_dev:
            R.append(self.res("S11", "na", "Not a `dev: true` project", ev))
        elif not schema3:
            R.append(self.res("S11", "unchecked", f"Snapshot schema {self.snap['schema']} has no surfaces", "snapshot.schema"))
        elif code is None:
            R.append(self.res("S11", "bad", f"No `{code_name}/`: no dev mirror", ev))
            rows.append(Row(f"Create `{code_name}/`", cpath, own["surface_folder"], "S11"))
            rows.append(Row("Install the dev mirror in the repo (Stop hook + mirror-check.py)", cpath,
                            own["dev_mirror"], "S11"))
        else:
            sev = f"vault.surfaces.{self.name}.{code_name}"
            names = {e["name"] for e in code["entries"]}
            probs = [f"`{f}` missing" for f in s11r["required_files"] if f not in names]
            sj = code["files"].get(s11r["settings_file"])
            if s11r["settings_file"] in names and sj is None:
                probs.append(f"`{s11r['settings_file']}` not read")
            elif sj is not None:
                try:
                    cfg = json.loads(sj)
                    cmds = [h.get("command", "") for g in (cfg.get("hooks", {}) or {}).get(s11r["hook_event"], []) or []
                            for h in (g.get("hooks") or []) if h.get("type") == "command"]
                    if not any(s11r["hook_script"] in c for c in cmds):
                        probs.append(f"no `{s11r['hook_event']}` hook running `{s11r['hook_script']}`")
                except (ValueError, AttributeError, TypeError):
                    probs.append(f"`{s11r['settings_file']}` doesn't parse")
            # Freshness isn't scored (2026-09-30): GitHub's pushed_at lags the real remote, and the
            # hook itself reports a failed copy in the Claude Code session. `repo` is still accepted
            # so older snapshots load, and ignored.
            if probs:
                R.append(self.res("S11", "bad", "; ".join(probs), sev))
                rows.append(Row(f"Install or repair the dev mirror in the repo: {'; '.join(probs)}", cpath,
                                own["dev_mirror"], "S11"))
            else:
                R.append(self.res("S11", "ok", "Hook, script and mirrored files in place", sev))

        # S12 · Claude Code working folder (twin projects)
        R.append(self.s12(folder, fslug, ctx, is_dev, code, code_name, cpath, rows, unchecked))

        # S13, S15, S16 · vault content of a sprint project
        R.extend(self.vault_content(folder, fslug, rows))

        R.insert(0, s5)
        order = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S12", "S13", "S15", "S16"]
        R.sort(key=lambda r: order.index(r["rule"]))
        return {"folder": folder, "title": title, "results": R, "rows": rows, "unchecked": unchecked,
                "mine": mine, "is_wf": is_wf, "newest_pending": None if use_newest else pending,
                "wf_after_paste": is_wf, "board_line": (ctx or {}).get("board"), "path": path,
                "surface_path": cpath}

    def s12(self, folder, fslug, ctx, is_dev, code, code_name, cpath, rows, unchecked):
        r12, own = self.rules["s12"], self.rules["owners"]
        ev = f"vault.surfaces.{self.name}.{code_name}"
        if is_dev:
            return self.res("S12", "na", "Dev project: the repo keeps its own layout", ev)
        if code is None:
            return self.res("S12", "na", f"No `{code_name}/`: no Claude Code working folder", ev)
        if self.snap["schema"] < 4:
            return self.res("S12", "unchecked", f"Snapshot schema {self.snap['schema']} has no working-folder manifest",
                            "snapshot.schema")
        probs = []
        # the guard: file, hash, hooks
        names = {e["name"] for e in code["entries"]}
        guard = []
        src = code["files"].get(r12["hook_file"])
        if r12["hook_file"] not in names:
            guard.append(f"`{r12['hook_file']}` missing")
        elif src is None:
            guard.append(f"`{r12['hook_file']}` not read")
        elif sha12(src.encode("utf-8")) != str(r12["hook_sha12"]):
            guard.append(f"`{r12['hook_file']}` outdated ({sha12(src.encode('utf-8'))} ≠ {r12['hook_sha12']})")
        sj = code["files"].get(r12["settings_file"])
        if sj is None:
            guard.append(f"`{r12['settings_file']}` missing")
        else:
            try:
                cfg = json.loads(sj)
                for evn in r12["hook_events"]:
                    cmds = [h.get("command", "") for g in (cfg.get("hooks", {}) or {}).get(evn, []) or []
                            for h in (g.get("hooks") or []) if h.get("type") == "command"]
                    if not any(r12["hook_script"] in c for c in cmds):
                        guard.append(f"no `{evn}` hook running `{r12['hook_script']}`")
            except (ValueError, AttributeError, TypeError):
                guard.append(f"`{r12['settings_file']}` doesn't parse")
        if guard:
            probs += guard
            rows.append(Row(f"Install or update the working-folder guard: {'; '.join(guard)}", cpath,
                            own["workdir_guard"], "S12"))
        # the manifest
        man = code.get("workdir")
        mpath = r12["manifest"].replace("{domain}", self.name).replace("{slug}", fslug)
        taken = datetime.date.fromisoformat(self.snap["taken_at"][:10])
        age = lambda d: (taken - datetime.date.fromisoformat(d[:10])).days
        if man is None or age(man["generated_at"]) > r12["manifest_max_age_days"]:
            why = "no manifest" if man is None else f"manifest from {man['generated_at']}, older than {r12['manifest_max_age_days']} days"
            unchecked.append(f"{code_name}: {why} at `{mpath}` → start a Claude Code session in it; "
                             "its SessionStart hook asks for the upload")
            if probs:
                return self.res("S12", "bad", "; ".join(probs) + f"; layout unchecked ({why})", ev)
            return self.res("S12", "unchecked", f"Guard in place; layout unchecked ({why})", ev)
        prefix = (ctx or {}).get("prefix") or ""
        pat = re.compile(r12["task_folder_pattern"].replace("{prefix}", re.escape(prefix)))
        fix = lambda action, path: rows.append(Row(action, f"{fslug}:{path}", own["workdir_fix"], "S12"))
        n0 = len(rows)
        dext = tuple(r12["data_extensions"])
        for e in man["root"]:
            if e["name"] not in r12["root_allowed"] and not (not e["dir"] and e["name"].lower().endswith(dext)):
                probs.append(f"`{e['name']}{'/' if e['dir'] else ''}` outside the layout")
                fix(f"Move `{e['name']}{'/' if e['dir'] else ''}` into `work/{prefix}-{{task}}/` or `scratch/`, "
                    "or delete it", e["name"])
        for top in r12["task_dirs"]:
            for f in man["task_folders"].get(top, []):
                if not pat.match(f["name"]):
                    probs.append(f"`{top}/{f['name']}/` isn't `{prefix}-{{task}}`")
                    fix(f"Rename `{top}/{f['name']}/` → `{top}/{prefix}-{{task}}/`", f"{top}/{f['name']}")
        for f in man["loose"]:
            if f["path"] == "data/":
                probs.append(f"loose {f.get('ext', '')} file in `data/`")
                fix(f"Move the loose {f.get('ext', '')} file in `data/` into `data/{prefix}-{{task}}/`", "data/")
            else:
                probs.append(f"loose `{f['path']}`")
                fix(f"Move `{f['path']}` into a `{prefix}-{{task}}/` folder", f["path"])
        seen = set()
        for f in man["misplaced_data"]:
            key = (f["dir"], f["ext"])
            if key in seen:
                continue
            seen.add(key)
            probs.append(f"{f['ext']} outside `data/` (`{f['dir']}`)")
            where = "at the root" if f["dir"] == "." else f"in `{f['dir']}/`"
            fix(f"Move the {f['ext']} file(s) {where} to `data/{prefix}-{{task}}/`", f["dir"])
        bpat = re.compile(r12["backup_name_pattern"])
        for b in man["backup"]:
            if b["dir"] or not bpat.match(b["name"]) or b["name"].lower().endswith(dext):
                what = f"`{r12['backup_dir']}/{b['name']}{'/' if b['dir'] else ''}`"
                probs.append(f"{what} isn't a settings rollback copy")
                fix(f"Move {what} out: superseded work → `work/{prefix}-{{task}}/superseded/`, anything else "
                    "→ its task folder, or delete it", f"{r12['backup_dir']}/{b['name']}")
        ret = r12["retention_days"]
        old = sorted(f["path"] for f in man["scratch"] if age(f["modified"]) > ret["scratch"])
        if old:
            probs.append(f"{len(old)} scratch file(s) older than {ret['scratch']} days")
            fix(f"Delete {len(old)} file(s) older than {ret['scratch']} days: " + ", ".join(f"`{o}`" for o in old),
                "scratch/")
        for f in man["task_folders"].get("_closed", []):
            if age(f["modified"]) > ret["_closed"]:
                probs.append(f"`_closed/{f['name']}/` closed {f['modified']}, older than {ret['_closed']} days")
                fix(f"Delete `_closed/{f['name']}/` (closed {f['modified']})", f"_closed/{f['name']}")
        for r in rows[n0:]:
            r.proj = folder
        note = "; ".join(probs) or f"Guard current, layout clean (manifest {man['generated_at']})"
        if man["truncated"]:
            note += " · manifest truncated: fix these, then re-run"
        return self.res("S12", "bad" if probs else "ok", note, ev + ".workdir")

    # ---------- vault content (S13–S16, schema 5) ----------
    def is_sprint_project(self, pd):
        pat = re.compile(self.rules["vault_content"]["sprint_folder_pattern"])
        return any(e["dir"] and "/" not in e["name"] and pat.match(e["name"]) for e in pd["entries"])

    @staticmethod
    def parse_fm(raw):
        """(mapping or None, error or None). error = (line number in the block, key on or above it)."""
        if raw is None:
            return None, None
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            mark = getattr(e, "problem_mark", None) or getattr(e, "context_mark", None)
            lines = raw.split("\n")
            n = min(mark.line, len(lines) - 1) if mark is not None else 0
            key = None
            for i in range(n, -1, -1):
                m = re.match(r"^([A-Za-z0-9_-]+):", lines[i]) if lines else None
                if m:
                    key = m.group(1)
                    break
            return None, (n + 1, key)
        return (data if isinstance(data, dict) else None), None

    def vault_content(self, folder, fslug, rows):
        rules, own = self.rules["vault_content"], self.rules["owners"]
        out = []
        ev = f"vault.projects.{self.name}.{fslug}"
        if self.snap["schema"] < 5:
            return [self.res(r, "unchecked", f"Snapshot schema {self.snap['schema']} has no project files", "snapshot.schema")
                    for r in ("S13", "S15", "S16")]
        pd = self.vprojects.get(fslug)
        if pd is None:
            return [self.res(r, "na", f"No `Projects/{fslug}/`", ev) for r in ("S13", "S15", "S16")]
        if not self.is_sprint_project(pd):
            return [self.res(r, "na", "No sprint folders", ev) for r in ("S13", "S15", "S16")]
        base = f"MyNotes/{self.name}/Projects/{fslug}"
        n0 = len(rows)
        parsed, broken = {}, []
        for f in sorted(pd["frontmatter"]):
            data, err = self.parse_fm(pd["frontmatter"][f])
            if err:
                line, key = err
                broken.append(f"`{f}` (line {line}, key `{key or '?'}`)")
                rows.append(Row(f"Quote the value of `{key or '?'}` in `{f}` so its frontmatter parses (YAML style)",
                                f"{base}/{f}", own["frontmatter_fix"], "S15"))
            elif data is not None:
                parsed[f] = data
        # S13 · a brief of a sprint card sits in that sprint's folder
        misplaced = []
        prefix = rules["sprint_tag_prefix"]
        for f in sorted(parsed):
            fm = parsed[f]
            if fm.get("type") != rules["brief_type"]:
                continue
            bt = str(fm.get("board-task") or "")
            sprints = self.sprint_of.get(bt) or self.sprint_of.get(bt.upper())
            if not sprints:
                continue
            top = f.split("/", 1)[0] if "/" in f else ""
            want = [f"sprint-{s[len(prefix):] if s.startswith(prefix) else s}" for s in sprints]
            if top not in want:
                misplaced.append(f"`{f}` (card {bt} → `{want[0]}/`)")
                rows.append(Row(f"Move the brief `{f}` into `{want[0]}/` (its card's sprint)", f"{base}/{f}",
                                own["brief_move"], "S13"))
        out.append(self.res("S13", "bad" if misplaced else "ok",
                            "; ".join(misplaced) or "Every sprint card's brief is in its sprint folder", ev))
        # S15 · frontmatter parses
        out.append(self.res("S15", "bad" if broken else "ok",
                            "Doesn't parse: " + "; ".join(broken) if broken else f"{len(pd['frontmatter'])} note(s) parse", ev))
        # S16 · the root holds only the hub, sprint-* folders and planning/
        pat = re.compile(rules["sprint_folder_pattern"])
        stray = []
        for e in sorted(pd["entries"], key=lambda e: e["name"]):
            n = e["name"]
            if "/" in n:
                continue
            if (not e["dir"] and n == f"{fslug}.md") or (e["dir"] and (pat.match(n) or n == rules["planning_dir"])):
                continue
            stray.append(f"`{n}{'/' if e['dir'] else ''}`")
            if e["dir"]:
                rows.append(Row(f"Move `{n}/` into `{rules['planning_dir']}/` or its card's sprint folder", f"{base}/{n}",
                                own["root_move"], "S16"))
            else:
                rows.append(Row(f"Move `{n}` into `{rules['planning_dir']}/`", f"{base}/{n}", own["root_move"], "S16"))
        out.append(self.res("S16", "bad" if stray else "ok",
                            "At the root: " + ", ".join(stray) if stray else "Hub, sprint folders and `planning/` only", ev))
        for r in rows[n0:]:
            r.proj = folder
        return out

    def s14(self):
        """Domain-wide: no filename twice across Projects/ and _inbox/."""
        if self.snap["schema"] < 5:
            return self.res("S14", "unchecked", f"Snapshot schema {self.snap['schema']} has no project files", "snapshot.schema")
        rules, own = self.rules["vault_content"], self.rules["owners"]
        seen = {}
        for ps in sorted(self.vprojects):
            for e in self.vprojects[ps]["entries"]:
                if not e["dir"] and e["name"].endswith(".md"):
                    seen.setdefault(e["name"].rsplit("/", 1)[-1], []).append(f"Projects/{ps}/{e['name']}")
        for n in sorted(self.snap["vault"]["inbox"].get(self.name, [])):
            if n.endswith(".md"):
                seen.setdefault(n, []).append(f"_inbox/{n}")
        dups = sorted((n, sorted(locs)) for n, locs in seen.items() if len(locs) > 1 and n not in rules["unique_exempt"])
        for n, locs in dups:
            self.rows.append(Row(f"`{n}` exists {len(locs)} times: archive the consumed copy (on proof) or rename one",
                                 ", ".join(f"MyNotes/{self.name}/{l}" for l in locs), own["duplicate_name"], "S14"))
        return self.res("S14", "bad" if dups else "ok",
                        "; ".join(f"`{n}` × {len(l)}" for n, l in dups) or "No filename twice in `Projects/` and `_inbox/`",
                        f"vault.projects.{self.name} + vault.inbox.{self.name}")

    def s9_problems(self, board, is_dev):
        s9 = self.rules["s9"]
        dev_tags = set(s9["lane_tags"]) | set(s9["stage_tags"])
        lanes = sorted(board.get("lanes") or [], key=lambda ln: ln["position"])
        tag_vals = lambda ln: set(ln["matcher"]["values"]) if ln["matcher"]["field"] == "tag" else set()
        if not is_dev:
            hit = sorted(ln["name"] for ln in lanes
                         if any(v.startswith(("lane/", "stage/")) or v in dev_tags for v in tag_vals(ln)))
            return [f"dev lane(s) {', '.join(f'`{h}`' for h in hit)}"] if hit else []
        probs = []
        missing = [x for x in s9["lane_tags"] + s9["stage_tags"] if x not in self.snap["tags"]]
        if missing:
            probs.append("missing tags " + ", ".join(f"`{m}`" for m in missing))
        matched = set().union(*[tag_vals(ln) for ln in lanes]) if lanes else set()
        no_lane = [x for x in s9["lane_tags"] if x not in matched]
        if no_lane:
            probs.append("no lane for " + ", ".join(f"`{m}`" for m in no_lane))
        if lanes and s9["first_lane_tag"] not in tag_vals(lanes[0]):
            probs.append(f"first lane `{lanes[0]['name']}` isn't `{s9['first_lane_tag']}`")
        return probs

    def rename_board(self, old, new, rule):
        r = Row(f"Rename board `{old}` → `{new}`", f"BanditBrains project \"{old}\"",
                self.rules["owners"]["board_rename"], rule)
        r.linked_old, r.linked_new = old, new
        return [r]

    # ---------- domain-wide ----------
    def score_domain(self):
        suf = self.rules["names"]["workflow_suffix"]
        D = self.domain_results
        D.insert(0, self.res("S1", "ok" if self.top else "bad",
                             f"Board folder `{self.name}`" + ("" if self.top else " missing"), "board.folders"))
        if not self.top:
            self.rows.append(Row(f"Create or rename the board folder to `{self.name}`", "BanditBrains folders",
                                 self.rules["owners"]["board_folder_rename"], "S1"))
        wf = [b for b in self.boards if b["name"].endswith(suf)]
        wtype = [b for b in self.boards if b["type"] == self.rules["workflow"]["board_type"]]
        wf_projects = [p for p in self.projects if any(r["rule"] == "S3" and r["status"] != "na" for r in p["results"])]
        probs = []
        if len(wf) != 1:
            probs.append(f"{len(wf)} boards end in `{suf}`")
        for b in wf:
            if b["type"] != "workflow":
                probs.append(f"`{b['name']}` is type `{b['type']}`")
                self.rows.append(Row(f"Retype board `{b['name']}` → workflow", f"BanditBrains project \"{b['name']}\"",
                                     self.rules["owners"]["board_retype"], "S3"))
        for b in wtype:
            if not b["name"].endswith(suf):
                probs.append(f"`{b['name']}` is type workflow without `{suf}`")
        after = [p for p in self.projects if p["wf_after_paste"]]
        if len(wf_projects) != 1:
            note = (f"{len(wf_projects)} projects have `type: workflow`: "
                    + ", ".join(f"`{p['folder']}`" for p in wf_projects))
            if len(after) == 1:
                note += f" — fixed once pending pastes land (only `{after[0]['folder']}` after)"
            probs.append(note)
            if len(wf_projects) > 1 and len(after) != 1:
                self.rows.append(Row("Pick the one workflow project; retype the others", self.name,
                                     self.rules["owners"]["decide"], "S3"))
        D.insert(1, self.res("S3", "bad" if probs else "ok", "; ".join(probs) or f"`{wf[0]['name']}`", "board.projects"))
        D.append(self.s14())
        pats = [re.compile(p) for p in self.rules["names"]["banned_board_patterns"]]
        for b in self.boards:
            if any(p.search(b["name"]) for p in pats):
                D.append(self.res("S2", "bad", f"Board `{b['name']}` has a banned prefix/suffix", "board.projects"))
        for b in self.boards:
            if b["name"] not in self.claimed:
                D.append(self.res("S6", "bad", f"Board `{b['name']}` has no vault project", "board.projects"))
                if self.snap["schema"] >= 2 and self.s9_problems(b, False):
                    D.append(self.res("S9", "bad", f"Board `{b['name']}` has dev lanes and no dev project",
                                      "board.projects"))
                    self.rows.append(Row(f"`{b['name']}` has dev lanes and no `dev: true` project: remove them, or onboard it",
                                         f"BanditBrains project \"{b['name']}\"", self.rules["owners"]["decide"], "S9"))
        # linked rows: every board rename → settings row for each board: line naming the old name
        final = []
        for r in self.rows:
            final.append(r)
            if getattr(r, "linked_old", None):
                for p in self.projects:
                    if p["board_line"] == f'project "{r.linked_old}"':
                        final.append(Row(f'`board:` → `project "{r.linked_new}"`, next version', p["path"],
                                         self.rules["owners"]["context_update"], r.rule))
                        final[-1].pair_with = r
        order = self.rules["row_order"]
        # stable sort by owner order, keep pairs adjacent (settings before board)
        self.rows = sorted(final, key=lambda r: (order.index(r.owner) if r.owner in order else 99))


# ───────────────────────── output ─────────────────────────
def count(results, level, levels):
    rs = [r for r in results if levels[r["rule"]] == level and r["status"] not in ("na", "unchecked")]
    return sum(r["status"] == "ok" for r in rs), len(rs)


def render(dom, date, rules_sha, snap_sha, script_sha, rulebook_updated):
    L = dom.levels
    allres = dom.domain_results + [r for p in dom.projects for r in p["results"]]
    mo, mt = count(allres, "must", L)
    so, st = count(allres, "should", L)
    out = [f"# 🔍 {dom.name} structure audit — {date}", "",
           f"> {len(dom.projects)} projects · musts {mo}/{mt} · shoulds {so}/{st} · {len(dom.rows)} fix rows · rulebook {rulebook_updated}", ""]
    out += ["## 🌐 Domain", "", "| Rule | Result | Note | Evidence |", "|---|---|---|---|"]
    for r in dom.domain_results:
        out.append(f"| {r['rule']} | {MARK[r['status']]} | {r['note']} | `{r['evidence']}` |")
    if dom.system:
        out.append(f"| — | — | System boards, not audited: {', '.join(dom.system)} | `board.projects` |")
    out += ["", "## 📦 Projects", ""]
    for p in dom.projects:
        mo, mt = count(p["results"], "must", L)
        so, st = count(p["results"], "should", L)
        out += [f"### {p['title']}", f"`{p['folder']} · musts {mo}/{mt} · shoulds {so}/{st}`", "",
                "| Rule | Result | Note | Evidence |", "|---|---|---|---|"]
        for r in p["results"]:
            out.append(f"| {r['rule']} | {MARK[r['status']]} | {r['note']} | `{r['evidence']}` |")
        out.append("")
    out += ["## 🔧 Fix rows", "", "| # | Action | Target | Owner | Rule |", "|---|---|---|---|---|"]
    idx = {}
    for i, r in enumerate(dom.rows, 1):
        idx[id(r)] = i
    for i, r in enumerate(dom.rows, 1):
        tag = r.rule
        if getattr(r, "pair_with", None):
            tag += f" · with {idx[id(r.pair_with)]}"
        out.append(f"| {i} | {r.action} | `{r.target}` | {r.owner} | {tag} |")
    out += ["", "## ❔ Unchecked", ""] + ([f"- {u}" for u in dom.unchecked] or ["- None"])
    out += ["", "---", f"`rules {rulebook_updated} · rules sha {rules_sha} · snapshot sha {snap_sha} · "
                     f"script v{SCRIPT_VERSION} sha {script_sha}`", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True)
    ap.add_argument("--rulebook", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--domain", action="append")
    ap.add_argument("--out", default=".")
    ap.add_argument("--replay")
    ap.add_argument("--project", help="Domain/ai-folder: print one project's scores and rows")
    a = ap.parse_args()
    try:
        rules, rsha = load_rules(a.rules, a.rulebook)
        snap, ssha = load_snapshot(a.snapshot)
    except ContractError as e:
        print(f"CONTRACT BROKEN — nothing scored: {e}")
        return 2
    script_sha = sha12(Path(__file__).read_bytes())
    date = snap["taken_at"][:10]
    if a.project:
        dom, _, folder = a.project.partition("/")
        if dom not in snap["vault"]["domains"] or folder not in snap["vault"]["settings"].get(dom, {}):
            print(f"CONTRACT BROKEN — `{a.project}` is not a settings folder in the snapshot")
            return 2
        d = Domain(dom, snap, rules).score()
        p = next(x for x in d.projects if x["folder"] == folder)
        mine = [r for r in d.rows if p["path"] in r.target or p["surface_path"] in r.target
                or getattr(r, "proj", None) == folder
                or r.target == p["title"]
                or (p["mine"] and r.target == f"BanditBrains project \"{p['mine']}\"")]
        L = d.levels
        mo, mt = count(p["results"], "must", L)
        so, st = count(p["results"], "should", L)
        out = [f"### {p['title']}", f"`{folder} · musts {mo}/{mt} · shoulds {so}/{st} · {date}`", "",
               "| Rule | Result | Note |", "|---|---|---|"]
        out += [f"| {r['rule']} | {MARK[r['status']]} | {r['note']} |" for r in p["results"]]
        out += ["", "| # | Action | Target | Owner | Rule |", "|---|---|---|---|---|"]
        out += [f"| {i} | {r.action} | `{r.target}` | {r.owner} | {r.rule} |" for i, r in enumerate(mine, 1)] or []
        print("\n".join(out))
        return 0
    domains = a.domain or sorted(snap["vault"]["domains"])
    for d in domains:
        if d not in snap["vault"]["domains"]:
            print(f"CONTRACT BROKEN — `{d}` is not a vault domain ({', '.join(snap['vault']['domains'])})")
            return 2
    reports = {d: render(Domain(d, snap, rules).score(), date, rsha, ssha, script_sha,
                         rules["rulebook_updated"]) for d in domains}
    if a.replay:
        text = Path(a.replay).read_text()
        d = re.search(r"^# 🔍 (\S+) structure audit", text, re.M)
        if not d or d.group(1) not in reports or reports[d.group(1)] != text:
            print("REPLAY MISMATCH — this report is not what these inputs produce. Treat it as invalid.")
            return 3
        print("REPLAY OK")
        return 0
    Path(a.out).mkdir(parents=True, exist_ok=True)
    for d, text in reports.items():
        Path(a.out, f"audit-{d}-{date}.md").write_text(text)
        print(f"{d}: {text.splitlines()[2][2:]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
