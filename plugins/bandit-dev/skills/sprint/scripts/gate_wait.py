#!/usr/bin/env python3
"""Stop and SubagentStop hook: refuses to end a wave while one of its gate agents (the code review, the browser
check) is still running in the background, so the wave never stops between a gate and its verdict.

What it reads, in this order:
  1. `background_tasks` in the hook input (Claude Code hooks: Stop and SubagentStop carry it, scoped to the parent
     session): a running task of type `subagent` whose `agent_type` is a gate agent holds the stop.
  2. Without `background_tasks`, the transcript (`agent_transcript_path` on SubagentStop, else `transcript_path`):
     an `Agent` launch of a gate agent whose result says `async_launched`, with no later `<task-notification>`
     naming that launch's tool-use id, holds the stop.
A gate agent ending its own turn is never held (two gates may run side by side). No gate running: exit 0, silent.
A held stop exits 2 with the reason on stderr; Claude Code ends the turn anyway after eight blocks in a row.

Contract: references/execute.md → The wave, step 4b in this skill.
"""
import json
import re
import sys

GATES = ("code-reviewer", "ui-verifier")
NOTIFIED = re.compile(r"<tool-use-id>([^<\s]+)</tool-use-id>")


def gate(name):
    name = str(name or "").lower()
    return next((g for g in GATES if g in name), None)


def from_tasks(tasks):
    return sorted({gate(t.get("agent_type") or t.get("description")) for t in tasks
                   if t.get("type") == "subagent" and t.get("status") == "running"
                   and gate(t.get("agent_type") or t.get("description"))})


def from_transcript(path):
    """Gate agents launched in the background with no completion notice later in the transcript."""
    launched, done = {}, set()
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except (OSError, TypeError):
        return []
    with fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            content = (entry.get("message") or {}).get("content")
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "tool_use" and part.get("name") in ("Agent", "Task"):
                        args = part.get("input") or {}
                        g = gate(args.get("subagent_type")) or gate(args.get("description"))
                        if g:
                            launched[part.get("id")] = [g, False]
                    elif part.get("type") == "tool_result" and part.get("tool_use_id") in launched:
                        result = entry.get("toolUseResult")
                        if isinstance(result, dict) and result.get("status") == "async_launched":
                            launched[part["tool_use_id"]][1] = True
            done |= set(NOTIFIED.findall(json.dumps(entry.get("attachment") or "")))
            if isinstance(content, str):
                done |= set(NOTIFIED.findall(content))
    return sorted({g for tid, (g, background) in launched.items() if background and tid not in done})


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get("hook_event_name") == "SubagentStop" and gate(payload.get("agent_type")):
        return 0
    if isinstance(payload.get("background_tasks"), list):
        running = from_tasks(payload["background_tasks"])
    else:
        running = from_transcript(payload.get("agent_transcript_path") or payload.get("transcript_path"))
    if not running:
        return 0
    print(f"A gate agent is still running in the background: {', '.join(running)}. Its verdict is not back, so "
          "the wave cannot end yet: do the wave's other steps, and merge, move the card or write its ledger line "
          "only after the verdict arrives (bandit-dev:sprint execute.md, The wave, step 4b).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
