#!/usr/bin/env python3
"""PostToolUse hook (note writes): inside the wave-records agent, a note write answers in a few lines, not the whole note.

Every note write tool of the app answers with the whole note, text included: a ledger section write brought the
whole ledger back into the chat each time (about 15,000 tokens a write). The records agent writes a wave's records
one section at a time, so this hook replaces the answer it sees (`updatedMCPToolOutput`, Claude Code hooks →
PostToolUse) with the note's id, title, kind, status, tags, place and size, its headings, and whether the text
written is what the note now holds (`sectionMatches` for a section write, `textMatches` for a whole save). The note
itself is unchanged: only what the chat sees is shorter. A read (`notes_get`) is never shortened.

Runs only for the agent whose type ends in `wave-records` (the hook's `agent_type`); any other chat, a refused
write (`ok: false`) and an answer it cannot read pass through as they are (no output).
"""
import json
import re
import sys

TOOL = re.compile(r"^mcp__.+__(notes_create|notes_update|notes_update_section|notes_set_fields|notes_set_status|"
                  r"notes_file|notes_move|notes_link_card|notes_unlink_card)$")
AGENT = "wave-records"
KEEP = ("id", "title", "kind", "status", "tags", "boardId", "boardColumnId", "lane", "updatedAt")
HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.M)


def answer_of(response):
    """(the tool's answer as a mapping, how it came: "text" content list, "content" mapping, "json" string or "dict")."""
    if isinstance(response, str):
        try:
            got = json.loads(response)
        except ValueError:
            return None, None
        return (got, "json") if isinstance(got, dict) else (None, None)
    if isinstance(response, list):
        text = next((p.get("text") for p in response if isinstance(p, dict) and p.get("type") == "text"), None)
        got, _ = answer_of(text) if isinstance(text, str) else (None, None)
        return (got, "text") if got else (None, None)
    if isinstance(response, dict) and isinstance(response.get("content"), list):
        got, _ = answer_of(response["content"])
        return (got, "content") if got else (None, None)
    return (response, "dict") if isinstance(response, dict) else (None, None)


def section_of(body, heading):
    """The text under `heading` (its words, or `## words`) up to the next heading of the same or a higher level."""
    want = heading.strip()
    level = len(want) - len(want.lstrip("#")) if want.startswith("#") else 0
    words = want.lstrip("#").strip()
    for m in HEADING.finditer(body):
        if m.group(2) == words and (not level or len(m.group(1)) == level):
            depth = len(m.group(1))
            rest = body[m.end():]
            nxt = next((h for h in HEADING.finditer(rest) if len(h.group(1)) <= depth), None)
            return rest[: nxt.start() if nxt else None]
    return None


def short(tool, tool_input, note):
    out = {k: note[k] for k in KEEP if k in note}
    body = note.get("body") if isinstance(note.get("body"), str) else ""
    out["bodyChars"] = len(body)
    out["headings"] = [f"{h[0]} {h[1]}" for h in HEADING.findall(body)]
    if tool == "notes_update_section" and isinstance(tool_input.get("heading"), str):
        now = section_of(body, tool_input["heading"])
        out["section"] = tool_input["heading"]
        out["sectionMatches"] = now is not None and now.strip() == str(tool_input.get("text") or "").strip()
    elif tool in ("notes_update", "notes_create") and isinstance(tool_input.get("text"), str):
        out["textMatches"] = body.strip() == tool_input["text"].strip()
    out["shortened"] = "for the records agent: the note is saved whole; read it with notes_get"
    return out


def reply(payload):
    """The hook's JSON output, or None to let the answer through."""
    if not isinstance(payload, dict) or not str(payload.get("agent_type") or "").endswith(AGENT):
        return None
    m = TOOL.match(str(payload.get("tool_name") or ""))
    if not m:
        return None
    response = payload.get("tool_response")
    answer, shape = answer_of(response)
    if not answer or answer.get("ok") is not True or not isinstance(answer.get("note"), dict):
        return None
    small = {"ok": True, "note": short(m.group(1), payload.get("tool_input") or {}, answer["note"])}
    text = json.dumps(small, ensure_ascii=False)
    if shape == "text":
        new = [{"type": "text", "text": text}]
    elif shape == "content":
        new = {**response, "content": [{"type": "text", "text": text}]}
    elif shape == "json":
        new = text
    else:
        new = small
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedMCPToolOutput": new}}


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    out = reply(payload)
    if out:
        print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
