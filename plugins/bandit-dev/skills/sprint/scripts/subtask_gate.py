#!/usr/bin/env python3
"""PreToolUse hook (board writes): a sprint card gets its build steps as sub-tasks before anything else.

Two calls are refused with exit 2 (the reason on stderr), so the call never runs:

  1. The sprint's commit, `manage_sprints { action: "move", status: "ready_to_execute" }`, while any card
     of that sprint has no build step on the board.
  2. Writing a card's Technical plan (`update_tasks` or `create_tasks` with a description whose
     `<h2>Technical plan</h2>` section is filled) while that card has no build step.

A build step is a sub-task that is neither a `Gate:` line nor the approval line (`Tested and approved by you`).
The hook cannot read the board, so it reads the chat's own record (`transcript_path`), oldest first: each
`get_task` answer sets a card's sub-tasks as the app returned them; each accepted `manage_subtasks` add, and
each created card's `subtasks`, adds to them; `get_sprints { sprintId }` answers, `add_cards` and cards created
in a sprint give a sprint's cards. Short ids and uuids are matched through the answers that carry both,
and an id `get_task` was asked for that the card no longer carries (a former or temporary id) through its answer.
A card the record has not read is refused too, with the read that settles it (`get_task`), so a card that
already has its build steps passes on the next try.

Skipped: the debug card (title `Debug: …`), an old-way sprint card (title `Sprint …`) and a completed card.
Silent on every other call, and when the payload cannot be read.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dependency_gate import answer_of, refused  # noqa: E402  (one reader of a tool's answer)

TOOL = re.compile(r"^mcp__.+__(manage_sprints|update_tasks|create_tasks|get_task|get_sprints|manage_subtasks)$")
COMMIT = "ready_to_execute"
APPROVAL = "tested and approved by you"
PLAN = re.compile(r"<h2[^>]*>\s*Technical plan\s*</h2>(.*?)(?=<h2|\Z)", re.S | re.I)
PLACEHOLDER = "how it will be built"
HTML = re.compile(r"<[^>]+>|&nbsp;")
SKIP = ("Debug:", "Sprint ")
SHORT = re.compile(r"^[A-Za-z]+-[Tt]?\d+$")  # a proper id ({prefix}-{n}) or a temporary one ({prefix}-T{n})


def plan_filled(description):
    m = PLAN.search(description) if isinstance(description, str) else None
    text = " ".join(HTML.sub(" ", m.group(1)).split()) if m else ""
    return bool(text) and not text.lower().startswith(PLACEHOLDER)


def build_steps(titles):
    return [t for t in titles or [] if isinstance(t, str) and t.strip()
            and not t.strip().lower().startswith("gate:") and t.strip().lower() != APPROVAL]


class Record:
    """What the chat has read and written on the board, keyed by card (its short id once known)."""

    def __init__(self):
        self.steps, self.alias, self.sprints, self.titles, self.done = {}, {}, {}, {}, set()

    def key(self, ref):
        if not isinstance(ref, str) or not ref.strip():
            return None
        ref = ref.strip()
        return self.alias.get(ref) or self.alias.get(ref.upper()) or (ref.upper() if SHORT.match(ref) else ref)

    def learn(self, uid, short, title=None):
        """Tie a uuid to its short id, moving anything recorded under the uuid alone."""
        key = short.strip().upper() if isinstance(short, str) and short.strip() else uid
        if not isinstance(key, str):
            return None
        for ref in (uid, key):
            if isinstance(ref, str) and ref != key:
                if ref in self.steps and key not in self.steps:
                    self.steps[key] = self.steps.pop(ref)
                for cards in self.sprints.values():
                    cards[:] = [key if c == ref else c for c in cards]
                self.alias[ref] = key
        self.alias[key] = key
        if isinstance(title, str):
            self.titles[key] = title
        return key

    def add_steps(self, ref, titles):
        key = self.key(ref)
        if key:
            self.steps[key] = (self.steps.get(key) or []) + [t for t in titles if isinstance(t, str)]

    def apply(self, tool, given, answer):
        given = given if isinstance(given, dict) else {}
        if tool == "get_task" and isinstance(answer, dict):
            key = self.learn(answer.get("id"), answer.get("shortId"), answer.get("title"))
            asked = given.get("taskId")
            if key and isinstance(asked, str) and asked.strip() and self.key(asked) != key:
                self.alias[asked.strip().upper() if SHORT.match(asked.strip()) else asked.strip()] = key  # a former id
            if key:
                self.steps[key] = [s.get("title") for s in answer.get("subtasks") or [] if isinstance(s, dict)]
                (self.done.add if answer.get("completed") else self.done.discard)(key)
        elif tool == "get_sprints" and isinstance(answer, dict) and isinstance(answer.get("cards"), list):
            cards = [c for c in answer["cards"] if isinstance(c, dict)]
            self.sprints[answer.get("id") or given.get("sprintId")] = [
                k for k in (self.learn(c.get("id"), c.get("shortId"), c.get("title")) for c in cards) if k]
            self.done |= {self.key(c.get("shortId") or c.get("id")) for c in cards if c.get("completed")}
        elif tool == "manage_subtasks" and given.get("action") == "add":
            self.add_steps(given.get("taskId"), [given.get("title")])
        elif tool == "manage_sprints" and given.get("action") in ("add_cards", "remove_card"):
            cards = self.sprints.setdefault(given.get("sprintId"), [])
            refs = given.get("taskIds") if isinstance(given.get("taskIds"), list) else [given.get("taskId")]
            for k in (self.key(r) for r in refs):
                if k and given["action"] == "add_cards" and k not in cards:
                    cards.append(k)
                elif k in cards and given["action"] == "remove_card":
                    cards.remove(k)
        elif tool == "create_tasks" and isinstance(answer, dict):
            results = answer.get("results") if isinstance(answer.get("results"), list) else []
            items = given.get("items") if isinstance(given.get("items"), list) else []
            for item, result in zip(items, results):
                if not isinstance(item, dict) or not isinstance(result, dict) or refused(result):
                    continue
                key = self.learn(result.get("taskId"), result.get("shortId"), item.get("title"))
                if key:
                    self.steps[key] = [t for t in item.get("subtasks") or [] if isinstance(t, str)]
                    if item.get("sprintId"):
                        self.sprints.setdefault(item["sprintId"], []).append(key)


def read_record(transcript):
    record, calls = Record(), {}
    try:
        lines = open(transcript, encoding="utf-8", errors="replace")
    except (OSError, TypeError):
        return record
    with lines:
        for line in lines:
            try:
                content = json.loads(line).get("message", {}).get("content")
            except (ValueError, AttributeError):
                continue
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


def owed(record, refs):
    """(cards with no build step, cards the chat has not read), skipping the debug, old-way and completed cards."""
    missing, unread = [], []
    for key in dict.fromkeys(record.key(r) for r in refs):
        if not key or key in record.done or record.titles.get(key, "").startswith(SKIP):
            continue
        if key not in record.steps:
            unread.append(key)
        elif not build_steps(record.steps[key]):
            missing.append(key)
    return missing, unread


def refusal(tool, given, transcript):
    """The reason to refuse this call, or None."""
    m = TOOL.match(tool or "")
    if not m or not isinstance(given, dict):
        return None
    kind = m.group(1)
    if kind == "manage_sprints" and given.get("action") == "move" and given.get("status") == COMMIT:
        record = read_record(transcript)
        cards = record.sprints.get(given.get("sprintId"))
        if cards is None:
            return [f"- The chat has not read this sprint's cards: get_sprints {{ sprintId: \"{given.get('sprintId')}\" }}, "
                    "then get_task each card."]
        missing, unread = owed(record, cards)
        what = "the sprint cannot be committed"
    elif kind in ("update_tasks", "create_tasks"):
        items = [i for i in given.get("items") or [] if isinstance(i, dict) and plan_filled(i.get("description"))]
        if kind == "create_tasks":
            missing = [i.get("title") or "a new card" for i in items
                       if not build_steps(i.get("subtasks")) and not str(i.get("title") or "").startswith(SKIP)]
            unread, what = [], "a card is created with its build steps in `subtasks` when its Technical plan is written"
        elif items:
            missing, unread = owed(read_record(transcript), [i.get("taskId") for i in items])
            what = "its Technical plan is written only once its build steps exist"
        else:
            return None
    else:
        return None
    if not missing and not unread:
        return None
    return ([f"- {c}: no build step on the board, so {what}. Write its build steps from its plan section as sub-tasks "
             "(manage_subtasks { action: \"add\" }, one line each; an add lands at the top, so add them last to first "
             "or reorder), the approval line `Tested and approved by you` last, then get_task to read it back."
             for c in missing]
            + [f"- {c}: not read in this chat. get_task {c}; if it already has its build steps, retry." for c in unread])


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    lines = refusal(payload.get("tool_name"), payload.get("tool_input"), payload.get("transcript_path"))
    if not lines:
        return 0
    print("\n".join(["🧩 Sub-task gate: every sprint card carries its build steps as sub-tasks before its Technical plan "
                     "and before the sprint is committed (bandit-dev:sprint plan, steps 7 and 12).", *lines,
                     "Then retry this call. Say in your reply which cards got their build steps."]), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
