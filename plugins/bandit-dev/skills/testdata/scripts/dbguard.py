#!/usr/bin/env python3
"""The only way the testdata skill touches a database. It reads the project's `bandit.yaml`
`testdata` section (through the sprint skill's recipe reader), refuses anything but a test
database, never prints an address or password, and records every row it creates so `clean`
removes those rows and nothing else.

Usage:
  dbguard.py [--file PATH] check DB                       the database is allowed and reachable by name
  dbguard.py [--file PATH] read DB  < query.sql           runs inside a READ ONLY transaction, rolled back
  dbguard.py [--file PATH] create DB --kind fill|card --label NAME [--yes] < insert.sql
                                                          INSERTs only, one transaction, every id recorded
  dbguard.py [--file PATH] clean DB RECORD|fill|card LABEL [--yes] [--dry-run]
                                                          deletes exactly the record's rows, checks none is left
  dbguard.py [--file PATH] records [DB]                   lists open run records

DB is development, test or staging, each named under `testdata.databases`. Its command reads SQL
on stdin (psql): it names env vars, never an address or password. Staging writes need --yes,
given only after the user's yes in the chat. Records live in `.testdata/{DB}/` at the repo root,
which must be git-ignored.

Exit codes: 0 ok · 2 usage · 3 recipe (missing file or key, named) · 5 the database command failed
or rows were left · 6 refused by the guard.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sprint" / "scripts"))
import recipe  # noqa: E402  (the one reader of bandit.yaml)

ALLOWED = ("development", "test", "staging")
ASK_EVERY_RUN = ("staging",)
SECRET = re.compile(r"\w+://|passw(or)?d\s*=|PGPASSWORD\s*=", re.I)
ENV_REF = re.compile(r"\$\{?([A-Za-z_]\w*)")
IDENT = re.compile(r"^[A-Za-z_][\w.]*$")
RETURNING = re.compile(r"RETURNING\s+'testdata'\s*,\s*'([\w.]+)'\s*,\s*'(\w+)'\s*,\s*(\w+)(::text)?\s*$", re.I | re.S)
INSERT = re.compile(r"^INSERT\s+INTO\s+\"?([\w.]+)\"?", re.I)
REDACT = [(re.compile(r"\w+://\S+"), "[address]"), (re.compile(r"(passw(or)?d\s*=\s*)\S+", re.I), r"\1[hidden]")]
PREAMBLE = "\\set QUIET on\n\\set ON_ERROR_STOP on\n\\pset tuples_only on\n\\pset format unaligned\n"
MAX_LINES = 200


def refuse(code, msg):
    print(f"testdata: {msg}", file=sys.stderr)
    sys.exit(code)


def redact(text):
    for pattern, repl in REDACT:
        text = pattern.sub(repl, text)
    return text


def section(path):
    data = recipe.load(path)
    if data.get("testdata") in (None, "", {}):
        refuse(3, f"{path.name} has no `testdata` section: add schema, logic and databases (the sprint skill's references/bandit-yaml.md)")
    for key in ("testdata.schema", "testdata.logic", "testdata.databases"):
        recipe.lookup(data, key)
    dbs = data["testdata"]["databases"]
    if not isinstance(dbs, dict):
        refuse(3, "`testdata.databases` must map each database name to its command")
    extra = [k for k in dbs if k not in ALLOWED]
    if extra:
        refuse(6, f"`testdata.databases` lists {', '.join(extra)}: only {', '.join(ALLOWED)} are test "
                  "databases. Remove the others; testdata never runs anywhere else")
    return dbs


def command(path, db, write):
    """The database's command, after every guard: allowed name, no literal secret, env vars set,
    records folder git-ignored (writes only). The command itself is never printed."""
    if db not in ALLOWED:
        refuse(6, f"`{db}` is not a test database: testdata runs only on {', '.join(ALLOWED)}")
    dbs = section(path)
    if db not in dbs or not dbs[db]:
        refuse(3, f"missing key `testdata.databases.{db}`")
    cmd = str(dbs[db])
    if SECRET.search(cmd):
        refuse(6, f"the `{db}` command holds an address or password: name an env var instead "
                  "(\"$DATABASE_URL\") or run inside the database container with its own login")
    host_part = re.sub(r"'[^']*'", "", cmd)  # single-quoted parts expand inside the command, not here
    unset = [v for v in ENV_REF.findall(host_part) if not os.environ.get(v)]
    if unset:
        refuse(6, f"env var {', '.join(f'`{v}`' for v in unset)} is not set: the `{db}` address is read from it")
    if write:
        root = path.parent
        r = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", ".testdata/x"], capture_output=True)
        if r.returncode != 0:
            refuse(6, f"`.testdata/` is not git-ignored in {root}: add it to .gitignore before any write")
    return cmd


def run(path, cmd, sql):
    r = subprocess.run(cmd, shell=True, cwd=path.parent, input=PREAMBLE + sql, capture_output=True, text=True)
    if r.returncode != 0:
        refuse(5, f"the database command failed ({r.returncode}), nothing was kept: "
                  f"{redact((r.stderr or r.stdout).strip())[-400:]}")
    return redact(r.stdout)


def statements(sql):
    """Split on semicolons outside quotes and dollar quotes. Comment lines are dropped."""
    sql = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    out, buf, quote, i = [], [], None, 0
    while i < len(sql):
        c = sql[i]
        if quote is None and sql.startswith("$$", i):
            quote, i = "$$", i + 2
            buf.append("$$")
            continue
        if quote == "$$" and sql.startswith("$$", i):
            quote, i = None, i + 2
            buf.append("$$")
            continue
        if c == "'" and quote in (None, "'"):
            quote = None if quote == "'" else "'"
        if c == ";" and quote is None:
            out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)
        i += 1
    out.append("".join(buf).strip())
    return [s for s in out if s]


def no_meta(sql):
    if any(l.lstrip().startswith("\\") for l in sql.splitlines()):
        refuse(6, "a line starts with a backslash: psql meta-commands are not allowed")


def check_inserts(sql):
    stmts = statements(sql)
    if not stmts:
        refuse(2, "no SQL on stdin")
    for s in stmts:
        head = s.split(None, 1)[0].upper()
        m = INSERT.match(s)
        if not m:
            refuse(6, f"`create` runs INSERTs only, found {head}: it never changes or removes a row it did not create")
        r = RETURNING.search(s)
        if not r or r.group(1).strip('"') != m.group(1) or r.group(2) != r.group(3):
            refuse(6, f"the INSERT into `{m.group(1)}` must end with "
                      f"RETURNING 'testdata', '{m.group(1)}', '<key>', <key>::text so its rows are recorded")
    return stmts


def records_dir(path, db):
    return path.parent / ".testdata" / db


def ask_every_run(db, yes):
    if db in ASK_EVERY_RUN and not yes:
        refuse(6, f"`{db}` asks the user's yes on every run: ask in the chat, quote the yes, then pass --yes")


def cmd_create(path, db, kind, label, yes):
    if kind not in ("fill", "card") or not re.fullmatch(r"[\w-]{1,60}", label or ""):
        refuse(2, "create needs --kind fill|card and --label NAME (letters, digits, - and _)")
    cmd = command(path, db, write=True)
    ask_every_run(db, yes)
    sql = sys.stdin.read()
    no_meta(sql)
    stmts = check_inserts(sql)
    out = run(path, cmd, "BEGIN;\n" + ";\n".join(stmts) + ";\nCOMMIT;\n")
    rows = [l.split("|")[1:4] for l in out.splitlines() if l.startswith("testdata|") and l.count("|") == 3]
    folder = records_dir(path, db)
    folder.mkdir(parents=True, exist_ok=True)
    rec = folder / f"{time.strftime('%Y%m%d-%H%M%S')}-{kind}-{label}.json"
    rec.write_text(json.dumps({"db": db, "kind": kind, "label": label,
                               "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "rows": rows}, indent=1),
                   encoding="utf-8")
    counts = {}
    for t, _, _ in rows:
        counts[t] = counts.get(t, 0) + 1
    print(f"testdata: created {len(rows)} rows on {db} ({', '.join(f'{t} {n}' for t, n in counts.items())})")
    print(f"testdata: record {rec.relative_to(path.parent)}")


def delete_sql(rows):
    """Children first: the reverse of the creation order, one DELETE per run of the same table."""
    groups = []
    for table, key, rid in reversed(rows):
        if not IDENT.match(table) or not IDENT.match(key):
            refuse(6, f"record row names `{table}`.`{key}`: not a plain identifier")
        if groups and groups[-1][:2] == (table, key):
            groups[-1][2].append(rid)
        else:
            groups.append((table, key, [rid]))
    quoted = lambda ids: ", ".join("'" + i.replace("'", "''") + "'" for i in ids)
    deletes = [f"DELETE FROM {t} WHERE {k}::text IN ({quoted(ids)})" for t, k, ids in groups]
    left = [f"SELECT 'left', '{t}', count(*) FROM {t} WHERE {k}::text IN ({quoted(ids)})" for t, k, ids in groups]
    return deletes, left


def cmd_clean(path, db, record, yes, dry):
    rec_path = Path(record)
    if not rec_path.is_absolute():
        rec_path = path.parent / rec_path
    try:
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        refuse(2, f"cannot read the record {record}: {e}")
    if rec.get("db") != db:
        refuse(6, f"the record was made on `{rec.get('db')}`, not `{db}`: clean it there")
    deletes, left = delete_sql(rec.get("rows", []))
    if dry:
        print(";\n".join(deletes) + ";" if deletes else "-- nothing to delete")
        return
    cmd = command(path, db, write=True)
    ask_every_run(db, yes)
    if deletes:
        run(path, cmd, "BEGIN;\n" + ";\n".join(deletes) + ";\nCOMMIT;\n")
        out = run(path, cmd, "BEGIN READ ONLY;\n" + ";\n".join(left) + ";\nROLLBACK;\n")
        still = [l for l in out.splitlines() if l.startswith("left|") and not l.endswith("|0")]
        if still:
            refuse(5, "rows the record names are still there: " + "; ".join(l.split("|", 1)[1] for l in still))
    done = rec_path.parent / "cleaned"
    done.mkdir(exist_ok=True)
    rec_path.rename(done / rec_path.name)
    print(f"testdata: removed the {len(rec.get('rows', []))} rows of {rec_path.name} from {db}; none left")


def cmd_read(path, db):
    cmd = command(path, db, write=False)
    sql = sys.stdin.read()
    no_meta(sql)
    if not sql.strip():
        refuse(2, "no SQL on stdin")
    lines = run(path, cmd, "BEGIN READ ONLY;\n" + sql.rstrip().rstrip(";") + ";\nROLLBACK;\n").splitlines()
    print("\n".join(lines[:MAX_LINES]))
    if len(lines) > MAX_LINES:
        print(f"testdata: {len(lines) - MAX_LINES} more lines not shown: ask for counts and shapes, not rows")


def find_records(path, db, kind, label=None):
    """The open records of one kind (and label) on one database; `clean` takes each in turn."""
    found = []
    for f in sorted(records_dir(path, db).glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        if rec.get("kind") == kind and (label is None or rec.get("label") == label):
            found.append(f)
    if not found:
        refuse(2, f"no open {kind} record{f' labelled {label}' if label else ''} on `{db}`")
    return found


def cmd_records(path, db):
    base = path.parent / ".testdata"
    found = sorted((base / db).glob("*.json") if db else base.glob("*/*.json"))
    for f in found:
        rec = json.loads(f.read_text(encoding="utf-8"))
        print(f"{rec['db']}\t{rec['kind']}\t{rec['label']}\t{len(rec['rows'])} rows\t{f.relative_to(path.parent)}")
    if not found:
        print("testdata: no open record")


def main(argv):
    path = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()) / "bandit.yaml"
    if len(argv) >= 2 and argv[0] == "--file":
        path, argv = Path(argv[1]).resolve(), argv[2:]
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    flags, opts, rest, i = set(), {}, [], 0
    while i < len(args):
        if args[i] in ("--yes", "--dry-run"):
            flags.add(args[i])
        elif args[i] in ("--kind", "--label") and i + 1 < len(args):
            opts[args[i]] = args[i + 1]
            i += 1
        else:
            rest.append(args[i])
        i += 1
    args = rest
    if cmd == "check" and len(args) == 1:
        command(path, args[0], write=True)
        print(f"testdata: `{args[0]}` is a test database, its command names no secret, records are git-ignored")
    elif cmd == "read" and len(args) == 1:
        cmd_read(path, args[0])
    elif cmd == "create" and len(args) == 1:
        cmd_create(path, args[0], opts.get("--kind"), opts.get("--label"), "--yes" in flags)
    elif cmd == "clean" and len(args) == 2 and args[1] == "fill":
        for rec in find_records(path, args[0], "fill"):
            cmd_clean(path, args[0], str(rec), "--yes" in flags, "--dry-run" in flags)
    elif cmd == "clean" and len(args) == 3 and args[1] == "card":
        for rec in find_records(path, args[0], "card", args[2]):
            cmd_clean(path, args[0], str(rec), "--yes" in flags, "--dry-run" in flags)
    elif cmd == "clean" and len(args) == 2:
        cmd_clean(path, args[0], args[1], "--yes" in flags, "--dry-run" in flags)
    elif cmd == "records" and len(args) <= 1:
        cmd_records(path, args[0] if args else None)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
