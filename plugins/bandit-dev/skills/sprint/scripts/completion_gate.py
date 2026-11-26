#!/usr/bin/env python3
"""PreToolUse hook (`update_tasks`): a card of a sprint is completed only once every one of its sub-tasks is ticked.

Refused with exit 2 (the reason on stderr), so the call never runs: an `update_tasks` entry with `complete: true` for

  1. a card of a sprint whose sub-tasks the chat's record shows open: the open lines are named;
  2. a card the chat has not read: the read that settles it (`get_task`) is named, so a card that is ready
     passes on the next try.

The debug card is a card of its sprint like any other: its issue and approval lines hold its completion too.

The hook cannot read the board, so it reads the chat's own record, oldest first, as the sub-task gate does: each
`get_task` answer sets a card's sub-tasks (id, title, ticked), its completed flag and its sprint; each accepted
`manage_subtasks` tick, add, promote and each `delete_tasks` subtask entry changes them; `get_sprints { sprintId }`
answers, `add_cards` and cards created in a sprint mark sprint cards; `reopen_tasks` reopens. Short ids and uuids are
matched through the answers that carry both. Only the conversation's own lines are read (`user` and `assistant`),
never the request copies Claude Code also writes to the file.

**Which record.** Inside a subagent (a `run` wave agent, a side-by-side card agent, the records agent) the hook input
carries `agent_id`, and `transcript_path` still names the main chat's file: the subagent's own record is
`{that file without .jsonl}/subagents/agent-{agent_id}.jsonl` (measured on Claude Code 2.1.326, 2026-11-26), and that
is the one read. When it is missing, the main file is read.

Passed: a card read as in no sprint, a card already completed (completing it again changes nothing), an entry
naming no card (`originSystem` completions). Silent on every other call, and when the payload cannot be read.

Contract: references/templates.md → Check lines in this skill.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dependency_gate import answer_of, refused  # noqa: E402  (one reader of a tool's answer)

TOOL = re.compile(r"^mcp__.+__(update_tasks|get_task|get_sprints|manage_subtasks|manage_sprints|create_tasks|"
                  r"delete_tasks|reopen_tasks)$")
SHORT = re.compile(r"^[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*-[Tt]?\d+$")
OWN_LINES = ("user", "assistant")


class Record:
    """What the chat has read and written on the board, keyed by card (its short id once known)."""

    def __init__(self):
        self.lines = {}      # card → {subtask id: [title, ticked]}
        self.owner = {}      # subtask id → card
        self.alias = {}      # uuid, former id → card
        self.in_sprint = {}  # card → True (in a sprint) / False (read as in none)
        self.done = set()
        self.added = 0

    def key(self, ref):
        if not isinstance(ref, str) or not ref.strip():
            return None
        ref = ref.strip()
        return self.alias.get(ref) or self.alias.get(ref.upper()) or (ref.upper() if SHORT.match(ref) else ref)

    def learn(self, uid, short):
        key = short.strip().upper() if isinstance(short, str) and short.strip() else uid
        if not isinstance(key, str):
            return None
        for ref in (uid,):
            if isinstance(ref, str) and ref != key:
                for table in (self.lines, self.in_sprint):
                    if ref in table and key not in table:
                        table[key] = table.pop(ref)
                if ref in self.done:
                    self.done.discard(ref)
                    self.done.add(key)
                for sid, card in list(self.owner.items()):
                    if card == ref:
                        self.owner[sid] = key
                self.alias[ref] = key
        self.alias[key] = key
        return key

    def set_lines(self, key, subtasks):
        for sid in [s for s, c in self.owner.items() if c == key]:
            del self.owner[sid]
        self.lines[key] = {}
        for s in subtasks or []:
            if isinstance(s, dict) and s.get("id"):
                self.lines[key][s["id"]] = [str(s.get("title") or ""), bool(s.get("completed"))]
                self.owner[s["id"]] = key

    def apply(self, tool, given, answer):
        given = given if isinstance(given, dict) else {}
        if tool == "get_task" and isinstance(answer, dict):
            key = self.learn(answer.get("id"), answer.get("shortId"))
            asked = given.get("taskId")
            if key and isinstance(asked, str) and asked.strip() and self.key(asked) != key:
                self.alias[asked.strip().upper() if SHORT.match(asked.strip()) else asked.strip()] = key
            if key:
                self.set_lines(key, answer.get("subtasks"))
                self.in_sprint[key] = bool(answer.get("sprint"))
                (self.done.add if answer.get("completed") else self.done.discard)(key)
        elif tool == "get_sprints" and isinstance(answer, dict) and isinstance(answer.get("cards"), list):
            for c in answer["cards"]:
                if isinstance(c, dict):
                    key = self.learn(c.get("id"), c.get("shortId"))
                    if key:
                        self.in_sprint[key] = True
                        (self.done.add if c.get("completed") else self.done.discard)(key)
        elif tool == "manage_sprints" and given.get("action") in ("add_cards", "remove_card"):
            refs = given.get("taskIds") if isinstance(given.get("taskIds"), list) else [given.get("taskId")]
            for k in (self.key(r) for r in refs):
                if k:
                    self.in_sprint[k] = given["action"] == "add_cards"
        elif tool == "manage_subtasks":
            action, sid = given.get("action"), given.get("subtaskId")
            card = self.owner.get(sid)
            if action == "tick" and card:
                self.lines[card][sid][1] = bool(given.get("completed"))
            elif action == "promote" and card:
                self.lines[card].pop(sid, None)
                self.owner.pop(sid, None)
            elif action == "add":
                key = self.key(given.get("taskId"))
                if key in self.lines:  # a new open line whose id the answer does not give
                    self.added += 1
                    self.lines[key][f"added-{self.added}"] = [str(given.get("title") or ""), False]
                    self.owner[f"added-{self.added}"] = key
        elif tool == "delete_tasks" and isinstance(answer, dict):
            items = given.get("items") if isinstance(given.get("items"), list) else []
            results = answer.get("results") if isinstance(answer.get("results"), list) else [{}] * len(items)
            for item, result in zip(items, results):
                if isinstance(item, dict) and item.get("kind") == "subtask" and not refused(result):
                    card = self.owner.pop(item.get("subtaskId"), None)
                    if card:
                        self.lines[card].pop(item.get("subtaskId"), None)
        elif tool == "reopen_tasks":
            for k in (self.key(r) for r in given.get("taskIds") or []):
                self.done.discard(k)
        elif tool == "update_tasks" and isinstance(answer, dict):
            items = given.get("items") if isinstance(given.get("items"), list) else []
            results = answer.get("results") if isinstance(answer.get("results"), list) else []
            for item, result in zip(items, results):
                if isinstance(item, dict) and item.get("complete") is True and not refused(result):
                    k = self.key(item.get("taskId"))
                    if k:
                        self.done.add(k)
        elif tool == "create_tasks" and isinstance(answer, dict):
            items = given.get("items") if isinstance(given.get("items"), list) else []
            results = answer.get("results") if isinstance(answer.get("results"), list) else []
            for item, result in zip(items, results):
                if isinstance(item, dict) and isinstance(result, dict) and not refused(result) and item.get("sprintId"):
                    key = self.learn(result.get("taskId"), result.get("shortId"))
                    if key:
                        self.in_sprint[key] = True  # its sub-tasks' ids come with its get_task


def record_path(payload):
    """The record of the chat making the call: a subagent's own file when the input names one."""
    main = payload.get("transcript_path")
    agent = payload.get("agent_id")
    if isinstance(main, str) and isinstance(agent, str) and agent.strip():
        own = Path(main[:-6] if main.endswith(".jsonl") else main) / "subagents" / f"agent-{agent.strip()}.jsonl"
        if own.exists():
            return str(own)
    return main


def read_record(transcript):
    record, calls = Record(), {}
    try:
        lines = open(transcript, encoding="utf-8", errors="replace")
    except (OSError, TypeError):
        return record
    with lines:
        for line in lines:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict) or entry.get("type") not in OWN_LINES:
                continue
            message = entry.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            for item in content if isinstance(content, list) else []:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "tool_use":
                    calls[item.get("id")] = (item.get("name"), item.get("input"))
                elif item.get("type") == "tool_result" and item.get("tool_use_id") in calls:
                    name, given = calls.pop(item["tool_use_id"])
                    m = TOOL.match(name or "")
                    answer = answer_of(item.get("content"))
                    if m and not item.get("is_error") and not refused(answer):
                        record.apply(m.group(1), given, answer)
    return record


def refusal(tool, given, transcript):
    """The lines of the reason to refuse this call, or None."""
    m = TOOL.match(tool or "")
    if not m or m.group(1) != "update_tasks" or not isinstance(given, dict):
        return None
    refs = [i.get("taskId") for i in given.get("items") or []
            if isinstance(i, dict) and i.get("complete") is True and isinstance(i.get("taskId"), str)]
    if not refs:
        return None
    record = read_record(transcript)
    lines = []
    for ref in dict.fromkeys(refs):
        key = record.key(ref)
        if key in record.done or record.in_sprint.get(key) is False:
            continue
        if key not in record.lines:
            lines.append(f"- {ref}: not read in this chat. get_task {ref}; if every sub-task is ticked, retry.")
            continue
        open_lines = [t for t, ticked in record.lines[key].values() if not ticked]
        if open_lines:
            lines.append(f"- {key}: open sub-tasks: " + "; ".join(f"\"{t}\"" for t in open_lines))
    return lines or None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    lines = refusal(payload.get("tool_name"), payload.get("tool_input"), record_path(payload))
    if not lines:
        return 0
    print("\n".join(["✅ Completion gate: a card of a sprint is completed only once every one of its sub-tasks is ticked "
                     "(bandit-dev:sprint references/templates.md → Check lines).", *lines,
                     "Tick each line only when its work, verdict or approval is in, read the card back (get_task), then "
                     "retry. Never tick a line just to pass this gate."]), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
