#!/usr/bin/env python3
"""Score the user's domains against the structure rules.

Kept: S1 to S4, S6, S9, S12, S13. Retired, numbers not reused: S5, S7, S8, S10, S11 (2.0.0: they
compared files of a settings folder and a second copy that no longer exist) and S14 to S16.

Usage:
  check_structure.py --rules structure-rules.yaml --rulebook structure-rulebook.md \
      --snapshot snapshot.json [--domain D ...] [--out DIR]
  check_structure.py --replay report.md --rules ... --rulebook ... --snapshot ...
  check_structure.py --project Acme/home-reno --rules ... --rulebook ... --snapshot ...
      (one project only, for /bandit:audit check: its rows, no domain block, nothing written)

Same inputs → same bytes. Exit 0 = scored, 2 = an input broke its contract
(nothing scored), 3 = replay mismatch (the report is not what these inputs produce).
The model never scores by hand: it builds the snapshot, runs this, and shows the output.

A project is a self-check stamp: `{domain}/{project}`, written by `/bandit:audit check` inside the
project, holding its Project Context, its surface and, for a working folder, its guard and
manifest. A domain is a top-level board folder. Only snapshots of schema 8 load: an older one was
built from a storage that is gone, and its report cannot be replayed.
"""
import argparse, datetime, hashlib, json, re, sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML missing: pip install pyyaml")

SCRIPT_VERSION = "7"
SNAPSHOT_SCHEMA = 8
RETIRED = ("S5", "S7", "S8", "S10", "S11", "S14", "S15", "S16")
KEPT = ["S1", "S2", "S3", "S4", "S6", "S9", "S12", "S13"]
SURFACES = ("claude-ai", "claude-code")
MARK = {"ok": "✅", "warn": "⚠️", "fail": "❌", "na": "—", "unchecked": "unchecked"}


class ContractError(Exception):
    pass


# ───────────────────────── inputs and contracts ─────────────────────────
def sha12(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def load_rules(path, rulebook_path):
    raw = Path(path).read_bytes()
    rules = yaml.safe_load(raw)
    for key in ("schema", "rulebook_updated", "levels", "names", "workflow", "project_context",
                "stamps", "owners", "row_order", "s9", "s12", "sprint_briefs"):
        if key not in rules:
            raise ContractError(f"rules: missing key `{key}`")
    # Parts of the rules that are logic, not settings: the script implements them in code,
    # so a change in the YAML without a script update is refused rather than ignored.
    if sorted(rules["levels"], key=lambda r: int(r[1:])) != KEPT:
        retired = sorted(set(rules["levels"]) & set(RETIRED))
        if retired:
            raise ContractError(f"rules.levels: {', '.join(retired)} retired: this script no longer scores them")
        raise ContractError(f"rules.levels must be exactly {', '.join(KEPT)}: update the script too")
    pc = rules["project_context"]
    if pc.get("optional_keys", []) != ["dev", "notes"] or pc.get("dev_values") != ["true"] \
            or pc.get("notes_values") != ["none", "app"]:
        raise ContractError("rules.project_context optional_keys/dev_values/notes_values changed: update the script too")
    for k in ("lane_tags", "stage_tags", "first_lane_tag", "dev_profile"):
        if k not in rules["s9"]:
            raise ContractError(f"rules.s9: missing `{k}`")
    if not rules["s9"]["lane_tags"] or rules["s9"]["first_lane_tag"] != rules["s9"]["lane_tags"][0]:
        raise ContractError("rules.s9.first_lane_tag must be the first of lane_tags")
    for blk, keys in (("stamps", ("note_title", "max_age_days")),
                      ("s12", ("hook_file", "hook_sha12", "settings_file", "hook_events", "hook_script",
                               "manifest", "manifest_max_age_days", "root_allowed", "task_dirs",
                               "task_folder_pattern", "data_extensions", "retention_days",
                               "backup_dir", "backup_name_pattern")),
                      ("sprint_briefs", ("brief_kind",))):
        for k in keys:
            if k not in rules[blk]:
                raise ContractError(f"rules.{blk}: missing `{k}`")
    if "board_profile" not in rules["workflow"]:
        raise ContractError("rules.workflow: missing `board_profile`")
    for k in ("board_profile", "board_rename", "board_folder_rename", "dev_board_shape", "context_update",
              "claude_rename", "self_check", "decide", "workdir_guard", "workdir_fix", "brief_tag"):
        if k not in rules["owners"]:
            raise ContractError(f"rules.owners: missing `{k}`")
    m = re.search(r"^updated:\s*(\S+)", Path(rulebook_path).read_text(), re.M)
    if not m:
        raise ContractError("rulebook: no `updated:` in frontmatter")
    if str(rules["rulebook_updated"]) != m.group(1):
        raise ContractError(f"rules say rulebook_updated {rules['rulebook_updated']}, "
                            f"rulebook says {m.group(1)}: update both in one proposal")
    return rules, sha12(raw)


def kebab(name):
    """A sprint name as its tag word: lower case, runs of anything but letters and digits as one hyphen."""
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")


def manifest_ok(wd):
    return (isinstance(wd, dict) and wd.get("schema") == 1 and isinstance(wd.get("generated_at"), str)
            and all(isinstance(wd.get(k), list) for k in ("root", "hosted", "loose", "scratch", "misplaced_data", "backup"))
            and isinstance(wd.get("task_folders"), dict)
            and all(isinstance(v, list) for v in wd["task_folders"].values())
            and isinstance(wd.get("truncated"), bool))


def load_snapshot(path):
    raw = Path(path).read_bytes()
    s = json.loads(raw)
    if s.get("schema") != SNAPSHOT_SCHEMA:
        raise ContractError(f"snapshot: schema {s.get('schema')} is not {SNAPSHOT_SCHEMA}. A snapshot of an earlier "
                            "schema read a storage that is gone: take a new one (`references/snapshot.md`); "
                            "its report cannot be replayed and is archived as it is")
    errs = []
    need = lambda cond, msg: None if cond else errs.append(msg)
    need(isinstance(s.get("taken_at"), str), "snapshot.taken_at missing")
    b = s.get("board", {})
    need(isinstance(b.get("folders"), list), "board.folders must be a list")
    need(isinstance(b.get("projects"), list), "board.projects must be a list")
    need(isinstance(s.get("tags"), list) and all(isinstance(x, str) for x in s.get("tags", [])),
         "tags must be a list of tag names")
    for i, p in enumerate(b.get("projects", [])):
        for k in ("name", "profile", "folder", "visibility", "system_owner"):
            need(k in p, f"board.projects[{i}] missing `{k}`")
        need(isinstance(p.get("lanes"), list), f"board.projects[{i}].lanes must be a list")
        for j, ln in enumerate(p.get("lanes") or []):
            for k in ("name", "position", "matcher"):
                need(k in ln, f"board.projects[{i}].lanes[{j}] missing `{k}`")
            m = ln.get("matcher") or {}
            need("field" in m and isinstance(m.get("values"), list),
                 f"board.projects[{i}].lanes[{j}].matcher needs `field` and `values`")
    for i, f in enumerate(b.get("folders", [])):
        for k in ("name", "parent"):
            need(k in f, f"board.folders[{i}] missing `{k}`")
    sc = b.get("sprint_cards")
    need(isinstance(sc, list) and all(isinstance(c, dict) and isinstance(c.get("id"), str)
                                      and (c.get("short_id") is None or isinstance(c.get("short_id"), str))
                                      and isinstance(c.get("sprints"), list) for c in (sc or [])),
         "board.sprint_cards must be a list of {id, short_id, sprints}")
    need(isinstance(s.get("stamps"), dict), "stamps must be an object (empty when no project has checked in)")
    for key, st in (s.get("stamps") or {}).items():
        ev = f"stamps.{key}"
        if not isinstance(st, dict):
            errs.append(f"{ev} must be an object")
            continue
        need(re.fullmatch(r"[^/]+/[^/]+", key) is not None, f"{ev}: the key is `{{domain}}/{{project}}`")
        need(st.get("surface") in SURFACES, f"{ev}.surface must be one of {', '.join(SURFACES)}")
        need(st.get("name") is None or isinstance(st.get("name"), str), f"{ev}.name must be text or null")
        need(isinstance(st.get("version"), str) and st.get("version"), f"{ev}.version must be text")
        need(isinstance(st.get("checked"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", st.get("checked") or "") is not None,
             f"{ev}.checked must be a date")
        ctx = st.get("context")
        need(ctx is None or (isinstance(ctx, dict) and all(isinstance(v, str) for v in ctx.values())),
             f"{ev}.context must map keys to text, or be null when the instructions have no block")
        guard = st.get("guard")
        need("guard" in st, f"{ev}.guard missing (null when the project has no working folder)")
        if guard is not None:
            need(isinstance(guard, dict)
                 and (guard.get("script_sha12") is None or isinstance(guard.get("script_sha12"), str))
                 and isinstance(guard.get("settings_parses"), bool)
                 and isinstance(guard.get("hooks"), list) and all(isinstance(h, str) for h in guard["hooks"]),
                 f"{ev}.guard must be {{script_sha12, settings_parses, hooks}}")
        need("workdir" in st, f"{ev}.workdir missing (null when there is no manifest)")
        need(st.get("workdir") is None or manifest_ok(st.get("workdir")), f"{ev}.workdir isn't a schema-1 manifest")
    need(isinstance(s.get("notes"), dict), "notes must be an object (one entry per domain)")
    for dom, projs in (s.get("notes") or {}).items():
        for slug_, pd in (projs or {}).items():
            errs.extend(notes_entry_errors(f"notes.{dom}.{slug_}", pd))
    folder_names = {f.get("name") for f in b.get("folders", [])}
    for i, p in enumerate(b.get("projects", [])):
        need(p.get("folder") in folder_names or p.get("folder") is None,
             f"board.projects[{i}] folder `{p.get('folder')}` not in board.folders")
    if errs:
        raise ContractError("snapshot: " + "; ".join(errs))
    return s, sha12(raw)


def notes_entry_errors(ev_, pd):
    """A project's notes, as its board's list (`notes_list`, card-linked briefs read with `notes_get`)."""
    errs = []
    notes = pd.get("notes") if isinstance(pd, dict) else None
    if not isinstance(notes, list):
        return [f"{ev_}.notes must be a list"]
    for i, n in enumerate(notes):
        if not isinstance(n, dict):
            errs.append(f"{ev_}.notes[{i}] must be an object")
            continue
        for k in ("id", "title", "kind", "status"):
            if not isinstance(n.get(k), str):
                errs.append(f"{ev_}.notes[{i}].{k} must be text")
        if not (isinstance(n.get("cards"), list) and all(isinstance(c, str) for c in n["cards"])):
            errs.append(f"{ev_}.notes[{i}].cards must be a list of card ids")
        tags = n.get("tags")
        if not (tags is None or (isinstance(tags, list) and all(isinstance(x, str) for x in tags))):
            errs.append(f"{ev_}.notes[{i}].tags must be a list of tags, or null when not read")
        if n.get("kind") == "brief" and n.get("cards") and tags is None:
            errs.append(f"{ev_}: brief `{n.get('title')}` is linked to a card, but its tags weren't read (notes_get)")
    return errs


# ───────────────────────── helpers ─────────────────────────
def slug(name):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


def parse_board(value):
    """`project "X"` → ("project", "X"); `none` → ("none", None)."""
    if value is None:
        return (None, None)
    m = re.fullmatch(r'(project|folder)\s+"(.+)"', value.strip())
    if m:
        return (m.group(1), m.group(2))
    return (value.strip(), None)


def domain_path(value):
    """`Acme` → ["Acme"]; `Acme / Clients / Beta` → the folder names from the top-level one down."""
    return [s.strip() for s in str(value or "").split("/") if s.strip()]


def parse_write(value):
    """`board "X", board "Y" column "Z"` → [("X", None), ("Y", "Z")]; anything else in the line → None."""
    items, rest = [], str(value or "").strip()
    pat = re.compile(r'board\s+"([^"]+)"(?:\s+column\s+"([^"]+)")?\s*(?:,\s*|$)')
    while rest:
        m = pat.match(rest)
        if not m:
            return None
        items.append((m.group(1), m.group(2)))
        rest = rest[m.end():]
    return items or None


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
        self.folders = folders
        sub = self.below(name)
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
        self.notes = snap["notes"].get(name, {})
        self.sprint_of = {}
        for c in snap["board"].get("sprint_cards") or []:
            for key in (c["id"], (c.get("short_id") or "").upper()):
                if key:
                    self.sprint_of[key] = sorted(c["sprints"])

    def below(self, name):
        """Every folder under `name`, at any depth (folders nest three levels deep)."""
        out, todo = set(), [name]
        while todo:
            node = todo.pop()
            kids = {f["name"] for f in self.folders if f["parent"] == node} - out
            out |= kids
            todo += kids
        return out

    def path_folder(self, segs):
        """The last folder of a domain path when each one is the parent of the next, from this domain down; else None."""
        if not segs or segs[0] != self.name:
            return None
        for parent, child in zip(segs, segs[1:]):
            if not any(f["name"] == child and f["parent"] == parent for f in self.folders):
                return None
        return segs[-1]

    def res(self, rule, status, note, evidence):
        if status == "bad":
            status = "fail" if self.levels[rule] == "must" else "warn"
        return {"rule": rule, "status": status, "note": note, "evidence": evidence}

    def score(self):
        stamps = self.snap["stamps"]
        for key in sorted(stamps):
            if key.split("/", 1)[0] == self.name:
                prod = self.score_project(key, stamps[key])
                self.projects.append(prod)
                self.rows += prod["rows"]
                self.unchecked += prod["unchecked"]
                if prod["mine"]:
                    self.claimed.add(prod["mine"])
        self.score_domain()
        return self

    # ---------- per project ----------
    def score_project(self, key, stamp):
        R, rows, unchecked = [], [], []
        ev = f"stamps.{key}"
        pslug = key.split("/", 1)[1]
        ctx = stamp.get("context")
        cname = stamp.get("name")
        on_ai = stamp["surface"] == "claude-ai"
        title = cname or pslug
        target = f"{key} ({'Claude.ai' if on_ai else 'Claude Code'})"
        own = self.rules["owners"]
        taken = datetime.date.fromisoformat(self.snap["taken_at"][:10])
        age = (taken - datetime.date.fromisoformat(stamp["checked"])).days
        if age > self.rules["stamps"]["max_age_days"]:
            unchecked.append(f"{key}: checked in on {stamp['checked']}, {age} days ago → run `/bandit:audit check` inside it")

        # ── S4 ──
        pc = self.rules["project_context"]
        board_kind, board_name = parse_board(ctx.get("board")) if ctx else (None, None)
        s4_board_problems = []
        if ctx is None:
            R.append(self.res("S4", "bad", "No Project Context in its instructions", ev + ".context"))
            rows.append(Row("Add the Project Context block", target, own["context_update"], "S4"))
        else:
            problems = [f"missing `{k}`" for k in pc["required_keys"] if not ctx.get(k)]
            segs = domain_path(ctx.get("domain"))
            scope_folder = self.name
            if ctx.get("domain") and segs[:1] != [self.name]:
                problems.append(f"domain `{ctx['domain']}` ≠ `{self.name}`")
            elif len(segs) > 1:
                scope_folder = self.path_folder(segs)
                if scope_folder is None:
                    problems.append(f"domain `{ctx['domain']}` isn't a folder path under `{self.name}`")
            scope_boards = ({p["name"] for p in self.boards
                             if p["folder"] == scope_folder or p["folder"] in self.below(scope_folder)}
                            if scope_folder else set())
            if "write" in ctx:
                targets = parse_write(ctx["write"])
                if targets is None:
                    problems.append(f"write `{ctx['write']}` isn't `board \"…\"` or `board \"…\" column \"…\"`, comma-separated")
                else:
                    problems += [f"write names board `{b}`, outside the domain" for b, _ in targets if b not in scope_boards]
            if ctx.get("project") and ctx["project"] != pslug:
                problems.append(f"project `{ctx['project']}` ≠ the stamp's `{pslug}`")
            if ctx.get("type") and ctx["type"] not in pc["types"]:
                problems.append(f"type `{ctx['type']}` unknown")
            if "dev" in ctx and ctx["dev"] not in pc["dev_values"]:
                problems.append(f"dev `{ctx['dev']}` must be `true` or absent")
            if "notes" in ctx and ctx["notes"] not in pc["notes_values"]:
                problems.append(f"notes `{ctx['notes']}` must be `none`, `app` or absent")
            if ctx.get("prefix") and not re.fullmatch(pc["prefix_pattern"], ctx["prefix"]):
                problems.append(f"prefix `{ctx['prefix']}` isn't 2–3 letters or `none`")
            if board_kind not in pc["board_forms"]:
                problems.append(f"board form `{board_kind}` not allowed ({', '.join(pc['board_forms'])})")
            elif board_kind == "project" and board_name not in self.all_board_names:
                problems.append(f"board `{board_name}` doesn't resolve")
            elif board_kind == "project" and pc.get("board_in_domain") and scope_folder \
                    and board_name not in scope_boards:
                problems.append(f"board `{board_name}` is outside the `{scope_folder}` folder")
            R.append(self.res("S4", "bad" if problems else "ok",
                              "; ".join(problems) or f"5 required keys (+ optional `dev`, `notes`), board `{ctx['board']}` resolves",
                              ev + ".context"))
            s4_board_problems = [p for p in problems if p.startswith("board")]
            for p in problems:
                if not p.startswith("board"):
                    rows.append(Row(f"Project Context: {p}", target, own["context_update"], "S4"))

        # which board is this project's?
        suf = self.rules["names"]["workflow_suffix"]
        is_wf = bool(ctx and ctx.get("type") == self.rules["workflow"]["project_type"])
        is_dev = bool(ctx and ctx.get("dev") == "true")
        mine = None
        if board_kind == "project" and board_name in {b["name"] for b in self.boards}:
            mine = board_name
        else:
            for b in self.boards:
                bn = b["name"][:-len(suf)] if b["name"].endswith(suf) else b["name"]
                if slug(bn) == pslug:
                    mine = b["name"]
        wf_rule = is_wf and self.rules["workflow"]["context_board_is_wkflw"]
        if ctx is not None and s4_board_problems and not wf_rule:
            if mine:
                rows.append(Row(f'`board:` → `project "{mine}"` ({s4_board_problems[0]})', target,
                                own["context_update"], "S4"))
            else:
                rows.append(Row(f"Decide `{pslug}`'s board: an existing board or `none` ({s4_board_problems[0]})",
                                target, own["decide"], "S4"))

        # ── S1 (project part) and S2: a Claude.ai project's name ──
        if not on_ai:
            R.append(self.res("S1", "na", "Runs in Claude Code: no Claude.ai name", ev + ".surface"))
            R.append(self.res("S2", "na", "Runs in Claude Code: no second name to match", ev + ".surface"))
        elif cname is None:
            R.append(self.res("S1", "unchecked", "Claude.ai name not in the stamp", ev + ".name"))
            R.append(self.res("S2", "unchecked", "Claude.ai name not in the stamp", ev + ".name"))
            unchecked.append(f"{key}: the session did not show the project's name → run `/bandit:audit check` and give it")
        else:
            R.append(self.res("S1", "ok" if cname.startswith(self.L) else "bad",
                              f"Claude.ai `{cname}`" + ("" if cname.startswith(self.L) else f" doesn't start with {self.L}"),
                              ev + ".name"))
            if not cname.startswith(self.L):
                rows.append(Row(f"Rename Claude.ai project `{cname}` to start with `{self.L}`", cname,
                                own["claude_rename"], "S1"))
            pre = self.rules["names"]["claude_prefix"].replace("{L}", self.L)
            name = cname[len(pre):] if cname.startswith(pre) else cname
            want_board = name + (suf if is_wf else "")
            issues = []
            if board_kind == "none":
                pass
            elif mine is None:
                issues.append("no board found")
            elif mine != want_board:
                issues.append(f"board `{mine}` ≠ `{want_board}`")
            R.append(self.res("S2", "bad" if issues else "ok",
                              "; ".join(issues) or f"`{name}` on Claude.ai and on the board", ev + ".name + board"))
            if issues and mine:
                rows.append(Row(f"Pick the one name: Claude.ai `{name}` or board `{mine}`; the other is renamed",
                                target, own["decide"], "S2"))

        # ── S3 (project part: workflow board line) ──
        if wf_rule:
            wf_boards = [b["name"] for b in self.boards if b["name"].endswith(suf)]
            ok = board_kind == "project" and board_name in wf_boards
            R.append(self.res("S3", "ok" if ok else "bad",
                              f"`board:` is `{ctx.get('board')}`" + ("" if ok else f", should name {wf_boards or 'the - wkflw board'}"),
                              ev + ".context.board"))
            if not ok and wf_boards:
                rows.append(Row(f"`board:` → `project \"{wf_boards[0]}\"`", target, own["context_update"], "S3"))
        else:
            R.append(self.res("S3", "na", "Not the workflow project", ev))

        # ── S6 (project part) ──
        if board_kind == "none":
            R.append(self.res("S6", "ok", "Declares `board: none`", ev))
        else:
            R.append(self.res("S6", "ok" if mine else "bad", f"Board `{mine}`" if mine else "No board and no `board: none`", ev))

        # ── S9 ──
        if board_kind == "none" or mine is None:
            R.append(self.res("S9", "na", "No board of its own", ev))
        else:
            probs = self.s9_problems(self.all_board_names[mine], is_dev)
            what = "dev board shape" if is_dev else "no dev lanes"
            R.append(self.res("S9", "bad" if probs else "ok", "; ".join(probs) or f"`{mine}`: {what}",
                              f"board.projects[{mine}].lanes + tags"))
            if probs and is_dev:
                rows.append(Row(f"Dev board shape on `{mine}`: {'; '.join(probs)}", f"Bandit Brain project \"{mine}\"",
                                own["dev_board_shape"], "S9"))
            elif probs:
                fix = "remove them" if is_wf else "remove them, or set `dev: true`"
                rows.append(Row(f"`{mine}` has dev lanes without `dev: true`: {fix}",
                                f"Bandit Brain project \"{mine}\"", own["decide"], "S9"))

        R.append(self.s12(key, pslug, stamp, ctx, is_dev, target, rows, unchecked))
        R.append(self.sprint_briefs(key, pslug, ctx, rows))

        R.sort(key=lambda r: KEPT.index(r["rule"]))
        for r in rows:
            if not hasattr(r, "proj"):
                r.proj = key
        return {"key": key, "title": title, "results": R, "rows": rows, "unchecked": unchecked,
                "mine": mine, "is_wf": is_wf, "board_line": (ctx or {}).get("board"), "target": target}

    # ---------- S12 · the working folder of a project in Claude Code without dev: true ----------
    def s12(self, key, fslug, stamp, ctx, is_dev, target, rows, unchecked):
        r12, own = self.rules["s12"], self.rules["owners"]
        ev = f"stamps.{key}"
        if stamp["surface"] != "claude-code":
            return self.res("S12", "na", "Runs on Claude.ai: no working folder", ev + ".surface")
        if is_dev:
            return self.res("S12", "na", "Dev project: the repository keeps its own layout", ev)
        probs = []
        guard = []
        g = stamp.get("guard")
        if g is None or g.get("script_sha12") is None:
            guard.append(f"`{r12['hook_file']}` missing")
        elif g["script_sha12"] != str(r12["hook_sha12"]):
            guard.append(f"`{r12['hook_file']}` outdated ({g['script_sha12']} ≠ {r12['hook_sha12']})")
        if g is None:
            guard.append(f"`{r12['settings_file']}` missing")
        elif not g["settings_parses"]:
            guard.append(f"`{r12['settings_file']}` doesn't parse")
        else:
            for evn in r12["hook_events"]:
                if evn not in g["hooks"]:
                    guard.append(f"no `{evn}` hook running `{r12['hook_script']}`")
        if guard:
            probs += guard
            r = Row(f"Install or update the working-folder guard: {'; '.join(guard)}", target,
                    own["workdir_guard"], "S12")
            r.proj = key
            rows.append(r)
        man = stamp.get("workdir")
        taken = datetime.date.fromisoformat(self.snap["taken_at"][:10])
        age = lambda d: (taken - datetime.date.fromisoformat(d[:10])).days
        if man is None or age(man["generated_at"]) > r12["manifest_max_age_days"]:
            why = "no manifest" if man is None else f"manifest from {man['generated_at']}, older than {r12['manifest_max_age_days']} days"
            unchecked.append(f"{key}: {why} (`{r12['manifest']}`) → start a Claude Code session in its folder, "
                             "then run `/bandit:audit check` there")
            if probs:
                return self.res("S12", "bad", "; ".join(probs) + f"; layout unchecked ({why})", ev + ".guard")
            return self.res("S12", "unchecked", f"Guard in place; layout unchecked ({why})", ev + ".workdir")
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
            r.proj = key
        note = "; ".join(probs) or f"Guard current, layout clean (manifest {man['generated_at']})"
        if man["truncated"]:
            note += " · manifest truncated: fix these, then re-run"
        return self.res("S12", "bad" if probs else "ok", note, ev + ".workdir")


    # ---------- S13 · the brief of a card in a sprint carries its sprint's tag ----------
    def want_tags(self, card):
        """The sprint-{name} tags of the sprints holding a card, or []."""
        sprints = self.sprint_of.get(card) or self.sprint_of.get(card.upper()) or []
        # A sprint's name is free text; its tag is the name in kebab-case (bandit:notes).
        return [f"sprint-{kebab(s)}" for s in sprints]

    def sprint_briefs(self, key, fslug, ctx, rows):
        rules, own = self.rules["sprint_briefs"], self.rules["owners"]
        ev = f"notes.{self.name}.{fslug}"
        if ctx and ctx.get("notes") == "none":
            return self.res("S13", "na", "`notes: none`: the helpers keep no notes for it", ev)
        pd = self.notes.get(fslug)
        if pd is None:
            return self.res("S13", "na", "No notes read for it (no board of its own)", ev)
        board = pd.get("board") or "its board"
        missing, seen = [], 0
        for n in sorted(pd["notes"], key=lambda n: (n["title"], n["id"])):
            if n["kind"] != rules["brief_kind"]:
                continue
            want = sorted({w for c in n["cards"] for w in self.want_tags(c)})
            if not want:
                continue
            seen += 1
            if not set(want) & set(n["tags"] or []):
                missing.append(f"`{n['title']}` (card {', '.join(n['cards'])} → tag `{want[0]}`)")
                r = Row(f"Tag the brief `{n['title']}` `{want[0]}` (its card's sprint), keeping its other tags",
                        f"Bandit Brain note \"{n['title']}\" ({n['id']}) on \"{board}\"", own["brief_tag"], "S13")
                r.proj = key
                rows.append(r)
        if not seen:
            return self.res("S13", "na", "No brief of a card in a sprint", ev)
        return self.res("S13", "bad" if missing else "ok",
                        "; ".join(missing) or "Every brief of a card in a sprint carries its sprint's tag", ev)

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
        if board["profile"] != s9["dev_profile"]:
            probs.append(f"profile `{board['profile']}`, a dev project's board is `{s9['dev_profile']}`")
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

    # ---------- domain-wide ----------
    def score_domain(self):
        suf = self.rules["names"]["workflow_suffix"]
        D = self.domain_results
        D.insert(0, self.res("S1", "ok" if self.top else "bad",
                             f"Board folder `{self.name}`" + ("" if self.top else " missing"), "board.folders"))
        if not self.top:
            self.rows.append(Row(f"Create or rename the board folder to `{self.name}`", "Bandit Brain folders",
                                 self.rules["owners"]["board_folder_rename"], "S1"))
        wf = [b for b in self.boards if b["name"].endswith(suf)]
        wkind = self.rules["workflow"]["board_profile"]
        wf_projects = [p for p in self.projects if any(r["rule"] == "S3" and r["status"] != "na" for r in p["results"])]
        probs = []
        if len(wf) != 1:
            probs.append(f"{len(wf)} boards end in `{suf}`")
        for b in wf:
            if b["profile"] != wkind:
                probs.append(f"`{b['name']}` is profile `{b['profile']}`")
                self.rows.append(Row(f"Switch board `{b['name']}` → profile {wkind} (its creator)",
                                     f"Bandit Brain project \"{b['name']}\"", self.rules["owners"]["board_profile"], "S3"))
        if len(wf_projects) != 1:
            probs.append(f"{len(wf_projects)} projects have `type: workflow`: "
                         + ", ".join(f"`{p['key']}`" for p in wf_projects))
            if len(wf_projects) > 1:
                self.rows.append(Row("Pick the one workflow project; retype the others", self.name,
                                     self.rules["owners"]["decide"], "S3"))
        D.insert(1, self.res("S3", "bad" if probs else "ok", "; ".join(probs) or f"`{wf[0]['name']}`", "board.projects"))
        pats = [re.compile(p) for p in self.rules["names"]["banned_board_patterns"]]
        for b in self.boards:
            if any(p.search(b["name"]) for p in pats):
                D.append(self.res("S2", "bad", f"Board `{b['name']}` has a banned prefix/suffix", "board.projects"))
                self.rows.append(Row(f"Rename board `{b['name']}`: no such prefix or suffix",
                                     f"Bandit Brain project \"{b['name']}\"", self.rules["owners"]["board_rename"], "S2"))
        for b in self.boards:
            if b["name"] not in self.claimed:
                D.append(self.res("S6", "bad", f"Board `{b['name']}`: no project has checked in for it", "board.projects"))
                self.unchecked.append(f"board `{b['name']}`: no stamp names it → run `/bandit:audit check` in its project, "
                                      "or archive the board if it has none")
                if self.s9_problems(b, False):
                    D.append(self.res("S9", "bad", f"Board `{b['name']}` has dev lanes and no dev project",
                                      "board.projects"))
                    self.rows.append(Row(f"`{b['name']}` has dev lanes and no `dev: true` project: remove them, or onboard it",
                                         f"Bandit Brain project \"{b['name']}\"", self.rules["owners"]["decide"], "S9"))
        order = self.rules["row_order"]
        # stable sort by owner order
        self.rows = sorted(self.rows, key=lambda r: (order.index(r.owner) if r.owner in order else 99))


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
        out += [f"### {p['title']}", f"`{p['key']} · musts {mo}/{mt} · shoulds {so}/{st}`", "",
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


def top_folders(snap):
    return sorted(f["name"] for f in snap["board"]["folders"] if f["parent"] is None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True)
    ap.add_argument("--rulebook", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--domain", action="append")
    ap.add_argument("--out", default=".")
    ap.add_argument("--replay")
    ap.add_argument("--project", help="Domain/project: print one project's scores and rows")
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
        dom = a.project.partition("/")[0]
        if a.project not in snap["stamps"]:
            print(f"CONTRACT BROKEN — `{a.project}` has no stamp in the snapshot")
            return 2
        d = Domain(dom, snap, rules).score()
        p = next(x for x in d.projects if x["key"] == a.project)
        mine = [r for r in d.rows if getattr(r, "proj", None) == a.project
                or (p["mine"] and r.target == f"Bandit Brain project \"{p['mine']}\"")]
        L = d.levels
        mo, mt = count(p["results"], "must", L)
        so, st = count(p["results"], "should", L)
        out = [f"### {p['title']}", f"`{a.project} · musts {mo}/{mt} · shoulds {so}/{st} · {date}`", "",
               "| Rule | Result | Note |", "|---|---|---|"]
        out += [f"| {r['rule']} | {MARK[r['status']]} | {r['note']} |" for r in p["results"]]
        out += ["", "| # | Action | Target | Owner | Rule |", "|---|---|---|---|---|"]
        out += [f"| {i} | {r.action} | `{r.target}` | {r.owner} | {r.rule} |" for i, r in enumerate(mine, 1)] or []
        print("\n".join(out))
        return 0
    known = top_folders(snap)
    stamped = sorted({k.split("/", 1)[0] for k in snap["stamps"]})
    domains = a.domain or sorted(set(known) | set(stamped))
    for d in domains:
        if d not in known and d not in stamped:
            print(f"CONTRACT BROKEN — `{d}` is neither a top-level board folder nor a stamped domain ({', '.join(known)})")
            return 2
    reports = {d: render(Domain(d, snap, rules).score(), date, rsha, ssha, script_sha,
                         rules["rulebook_updated"]) for d in domains}
    if a.replay:
        text = Path(a.replay).read_text()
        d = re.search(r"^# 🔍 (\S+) structure audit", text, re.M)
        # Trailing newlines aside (a note's text may come back without its last one), byte for byte.
        if not d or d.group(1) not in reports or reports[d.group(1)].rstrip("\n") != text.rstrip("\n"):
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
