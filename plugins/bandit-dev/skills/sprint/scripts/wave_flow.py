#!/usr/bin/env python3
"""Measures one wave from the Claude Code chat logs and prints the wave report's Flow and Tokens blocks
(references/templates.md → Wave report). Numbers come only from the logs; what the logs cannot show
prints "not measured", never an estimate.

Logs: the session files `{log dir}/*.jsonl` and their agents `{log dir}/{session}/subagents/agent-*.jsonl`,
each agent named by `agentType` in its `.meta.json`. The log dir is ~/.claude/projects/ plus the repo path
with every `/` and `.` turned into `-`.

Counting:
  step         one assistant message; log lines sharing a `message.id` are one step
  re-read      cache_read_input_tokens · new = input_tokens + cache_creation_input_tokens · written = output_tokens
  context      input + cache_read + cache_creation of a step; start = the main chat's first step, peak = its largest
  card         from its `echo CARD-START {card}` mark to the next mark or the end of the window
  full check   a Bash call whose command contains the recipe's `verify` command; failed = its result is an error
  test run     a Bash call matching --test; targeted when the command carries more after the match
  gate round   one Agent launch, counted by its type
  repeat run   a full check or test run whose exact command ran before with no file edit in between
  duration     from the call to its result; a call started in the background is "not measured"

Usage:
  wave_flow.py --since ISO [--until ISO] [--logs DIR | --repo PATH] [--verify CMD] [--test REGEX]
  (--verify defaults to `recipe.py get verify` in the current project; without it full checks are "not measured")
Exit codes: 0 ok · 2 usage · 3 no logs in the window.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

EDITS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
NM = "not measured"


def when(text):
    try:
        return datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        return None


def read(path):
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            out.append(row)
    return out


def parts(logs):
    """(part name, rows) for the main chat files and each agent file."""
    found = []
    for f in sorted(logs.glob("*.jsonl")):
        found.append(("main chat", read(f)))
        for a in sorted((logs / f.stem / "subagents").glob("agent-*.jsonl")):
            meta = a.with_suffix(".meta.json")
            kind = "other agent"
            if meta.exists():
                try:
                    kind = json.loads(meta.read_text(encoding="utf-8")).get("agentType") or kind
                except ValueError:
                    pass
            found.append((kind, read(a)))
    return found


def blocks(row):
    content = (row.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


def result_text(block):
    c = block.get("content")
    if isinstance(c, list):
        return "".join(x.get("text", "") for x in c if isinstance(x, dict))
    return str(c or "")


def minutes(seconds):
    return f"{round(seconds / 60)} min"


def hmm(seconds):
    m = int(round(seconds / 60))
    return f"{m // 60}:{m % 60:02d}"


def big(n):
    return f"{n / 1e6:.1f} M" if n >= 1e6 else f"{round(n / 1e3)} K"


def measure(logs, since, until):
    steps = {}            # (part, message id) → (time, usage)
    calls = {}            # tool_use id → dict(name, input, time, part)
    results = {}          # tool_use id → (time, text, is_error)
    marks = []            # (time, card)
    edits = []            # times of file edits (main chat and agents)
    for part, rows in parts(logs):
        for row in rows:
            t = when(row.get("timestamp"))
            if t is None or t < since or (until and t > until):
                continue
            msg = row.get("message") or {}
            if row.get("type") == "assistant" and msg.get("id"):
                steps.setdefault((part, msg["id"]), (t, msg.get("usage") or {}))
            for b in blocks(row):
                if b.get("type") == "tool_use":
                    calls[b.get("id")] = {"name": b.get("name"), "input": b.get("input") or {}, "time": t, "part": part}
                    cmd = str((b.get("input") or {}).get("command", ""))
                    m = re.search(r"echo\s+['\"]?CARD-START\s+([^\s'\"]+)", cmd)
                    if m:
                        marks.append((t, m.group(1)))
                    if b.get("name") in EDITS:
                        edits.append(t)
                elif b.get("type") == "tool_result":
                    results[b.get("tool_use_id")] = (t, result_text(b), bool(b.get("is_error")))
    return steps, calls, results, sorted(marks), sorted(edits)


def report(steps, calls, results, marks, edits, verify, test, since, until):
    if not steps:
        return None
    times = sorted(t for t, _ in steps.values())
    end = until or times[-1]
    lines = ["#### ⏱️ Flow"]
    windows = [(c, t, marks[i + 1][0] if i + 1 < len(marks) else end) for i, (t, c) in enumerate(marks)]
    per_card = " · per card: " + ", ".join(f"{c} {hmm((b - a).total_seconds())}" for c, a, b in windows) if windows else " · per card: " + NM
    lines.append(f"- Time: {hmm((times[-1] - times[0]).total_seconds())}{per_card}")

    def dur(cid):
        c = calls[cid]
        if c["input"].get("run_in_background") or cid not in results:
            return None
        return (results[cid][0] - c["time"]).total_seconds()

    bash = sorted((c["time"], cid) for cid, c in calls.items() if c["name"] == "Bash")
    checks = [cid for _, cid in bash if verify and verify in str(calls[cid]["input"].get("command", ""))]
    tests = [cid for _, cid in bash if test and re.search(test, str(calls[cid]["input"].get("command", "")))
             and cid not in checks]
    if verify:
        secs = [d for d in (dur(c) for c in checks) if d is not None]
        failed = [c for c in checks if c in results and results[c][2]]
        why = "; ".join(results[c][1].strip().splitlines()[-1][:80] for c in failed if results[c][1].strip())
        bg = len(checks) - len(secs)
        lines.append(f"- Full checks: {len(checks)} runs, {minutes(sum(secs))} total"
                     f"{f' ({bg} in the background: {NM})' if bg else ''}, {len(failed)} failed"
                     f"{f' ({why})' if why else ''}")
    else:
        lines.append(f"- Full checks: {NM} (no verify command)")
    if test:
        targeted = sum(1 for c in tests if re.split(test, str(calls[c]["input"].get("command", "")), maxsplit=1)[-1].strip())
        lines.append(f"- Test runs: {len(tests) - targeted} whole suite, {targeted} targeted")
    else:
        lines.append(f"- Test runs: {NM} (no test command given)")
    agents = Counter(str(c["input"].get("subagent_type") or "general-purpose") for c in calls.values()
                     if c["name"] in ("Agent", "Task"))
    review = sum(n for k, n in agents.items() if "review" in k)
    ui = sum(n for k, n in agents.items() if "ui" in k.lower())
    others = ", ".join(f"{k} {n}" for k, n in sorted(agents.items()) if "review" not in k and "ui" not in k.lower())
    lines.append(f"- Gates: code review {review} rounds, UI check {ui} rounds" + (f" · other agents: {others}" if others else ""))
    seen, repeats = {}, []
    for t, cid in bash:
        if cid not in checks and cid not in tests:
            continue
        cmd = str(calls[cid]["input"].get("command", "")).strip()
        if cmd in seen and not any(seen[cmd] < e < t for e in edits):
            repeats.append(cmd)
        seen[cmd] = t
    lines.append(f"- Repeat runs: {len(repeats)}" + (f" ({'; '.join(sorted(set(r[:60] for r in repeats)))})" if repeats else ""))
    timed = sorted(((dur(cid), cid) for cid in calls if dur(cid) is not None), reverse=True)[:3]
    sinks = " · ".join(f"{i + 1}. {calls[c]['name']} {str(calls[c]['input'].get('command') or calls[c]['input'].get('description') or '')[:40]} {minutes(d)}".replace("  ", " ")
                       for i, (d, c) in enumerate(timed))
    lines.append(f"- Time sinks: {sinks or NM}")

    lines += ["", "#### 🪙 Tokens"]
    total = defaultdict(lambda: [0, 0, 0, 0])   # part → re-read, new, written, steps
    main_ctx = []
    for (part, _), (t, u) in sorted(steps.items(), key=lambda kv: kv[1][0]):
        rr = u.get("cache_read_input_tokens") or 0
        new = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
        w = u.get("output_tokens") or 0
        p = total[part]
        p[0] += rr; p[1] += new; p[2] += w; p[3] += 1
        if part == "main chat":
            main_ctx.append(rr + new)
    rr, new, w = (sum(p[i] for p in total.values()) for i in range(3))
    allt = rr + new + w or 1
    lines.append(f"- Total: {big(rr)} re-read from cache · {big(new)} new · {big(w)} written")
    share = lambda p: f"{big(sum(p[:3]))} ({round(100 * sum(p[:3]) / allt)}%)"  # noqa: E731
    split = [f"main chat {share(total['main chat'])}"] if "main chat" in total else []
    split += [f"{k} {share(p)}" for k, p in sorted(total.items()) if k != "main chat"]
    lines.append("- Split: " + " · ".join(split))
    if windows:
        cards = []
        for c, a, b in windows:
            n = sum((u.get("cache_read_input_tokens") or 0) + (u.get("input_tokens") or 0)
                    + (u.get("cache_creation_input_tokens") or 0) + (u.get("output_tokens") or 0)
                    for (t, u) in steps.values() if a <= t < b or (b == end and t == b))
            cards.append(f"{c} {big(n)}")
        lines.append("- Per card: " + ", ".join(cards))
    else:
        lines.append(f"- Per card: {NM} (no CARD-START mark)")
    if main_ctx:
        lines.append(f"- Main chat: {total['main chat'][3]} steps · start context {big(main_ctx[0])} · peak context {big(max(main_ctx))}")
    else:
        lines.append(f"- Main chat: {NM}")
    sizes = Counter()
    for cid, (t, text, _) in results.items():
        if cid in calls:
            sizes[calls[cid]["name"]] += len(text)
    top = " · ".join(f"{i + 1}. {k} {round(v / 1e3)} K chars" for i, (k, v) in enumerate(sizes.most_common(3)))
    lines.append(f"- Biggest tool outputs: {top or NM}")
    return "\n".join(lines)


def default_verify():
    here = Path(__file__).resolve().parent / "recipe.py"
    r = subprocess.run([sys.executable, str(here), "get", "verify"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--since", required=True)
    ap.add_argument("--until")
    ap.add_argument("--logs")
    ap.add_argument("--repo")
    ap.add_argument("--verify")
    ap.add_argument("--test")
    a = ap.parse_args(argv)
    since, until = when(a.since), when(a.until) if a.until else None
    if since is None or (a.until and until is None):
        print("wave_flow: --since and --until take ISO times (2026-11-04T09:00:00Z)", file=sys.stderr)
        return 2
    repo = Path(a.repo or Path.cwd()).resolve()
    logs = Path(a.logs) if a.logs else Path.home() / ".claude" / "projects" / re.sub(r"[/.]", "-", str(repo))
    verify = a.verify if a.verify is not None else default_verify()
    data = measure(logs, since, until)
    text = report(*data, verify, a.test, since, until)
    if text is None:
        print(f"wave_flow: no logged steps in {logs} for that window", file=sys.stderr)
        return 3
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
