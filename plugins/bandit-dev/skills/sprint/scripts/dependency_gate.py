#!/usr/bin/env python3
"""PostToolUse hook (board writes): when a card is made to block another, the blocked card owes a gate.

A card created with `dependencies.blocks` / `blockedBy`, or a link added with `link_tasks`, makes one
card wait for another. The blocked card must then carry a gate sub-task: one unticked line, last in
its checklist, saying what has to come back from the blocker. The hook cannot write to the board, so
it puts a notice into the session's context (`additionalContext`) naming the cards and the steps owed.

Any MCP server's `create_tasks` and `link_tasks`, recognised by the call's own shape. Silent when the
write was refused, when no link was made, for a created card that already lists its own gate for that
blocker, and for a sprint card (title `Sprint …`), whose checklist is the plan's fixed steps. After
`link_tasks` the answer holds no checklist, so the notice says to skip a card that already has its gate.
"""
import json
import re
import sys

TOOL = re.compile(r"^mcp__.+__(create_tasks|link_tasks)$")
SPRINT = "Sprint "


def answer_of(response):
    """The tool's own answer as one mapping, whether it comes as JSON, text content or a mapping."""
    if response is None:
        return None
    if isinstance(response, str):
        try:
            return answer_of(json.loads(response))
        except ValueError:
            return None
    if isinstance(response, list):
        text = next((p.get("text") for p in response if isinstance(p, dict) and p.get("type") == "text"), None)
        return answer_of(text) if text else None
    if isinstance(response, dict) and isinstance(response.get("content"), list):
        return answer_of(response["content"])
    return response if isinstance(response, dict) else None


def refused(answer):
    return isinstance(answer, dict) and answer.get("ok") is False


def ids(value):
    return [v for v in value if isinstance(v, str) and v.strip()] if isinstance(value, list) else []


def has_gate(item, blocker):
    return any(isinstance(s, str) and s.lower().startswith("gate") and blocker in s for s in item.get("subtasks") or [])


def links_made(tool_name, tool_input, response):
    """Every (blocker, blocked) pair this write made that still owes a gate."""
    m = TOOL.match(tool_name or "")
    if not m or not isinstance(tool_input, dict):
        return []
    answer = answer_of(response)
    if refused(answer):
        return []
    if m.group(1) == "link_tasks":
        blocker, blocked = tool_input.get("blockerTaskId"), tool_input.get("blockedTaskId")
        return [(blocker, blocked)] if isinstance(blocker, str) and isinstance(blocked, str) else []
    results = (answer or {}).get("results") if isinstance(answer, dict) else None
    links = []
    for i, item in enumerate(tool_input.get("items") if isinstance(tool_input.get("items"), list) else []):
        result = results[i] if isinstance(results, list) and i < len(results) else None
        if not isinstance(item, dict) or refused(result):
            continue
        title = item.get("title") if isinstance(item.get("title"), str) else "untitled"
        if title.startswith(SPRINT):
            continue
        result = result if isinstance(result, dict) else {}
        me = result.get("shortId") or result.get("taskId") or result.get("id") or f'the new card "{title}"'
        deps = item.get("dependencies") if isinstance(item.get("dependencies"), dict) else {}
        links += [(me, blocked) for blocked in ids(deps.get("blocks"))]
        links += [(blocker, me) for blocker in ids(deps.get("blockedBy")) if not has_gate(item, blocker)]
    return links


def notice(payload):
    links = links_made(payload.get("tool_name"), payload.get("tool_input") or {}, payload.get("tool_response"))
    if not links:
        return None
    return "\n".join([
        "🔗 Dependency gate: every blocked card carries a gate sub-task for each blocker.",
        *(f'- {a} now blocks {b}: add to {b} a sub-task "Gate: {a} delivered/feedback received (<what it '
          f"hands over>) before <{b}'s next step, e.g. deploy>\", unless {b} already has a gate for {a}." for a, b in links),
        'For each: manage_subtasks { action: "add" } on the blocked card → manage_subtasks { action: "reorder" } '
        "with the FULL order so the gate is last → get_task to read it back → add_comment on the blocked card "
        "naming the link and the gate. Say in your reply which gates you added.",
        "Skip if a gate for this blocker already exists on the blocked card. A sprint card blocked by its batch "
        "or the previous sprint needs no gate: its checklist is the plan's fixed steps.",
    ])


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    text = notice(payload) if isinstance(payload, dict) else None
    if text:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
