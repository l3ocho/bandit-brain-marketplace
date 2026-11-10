#!/usr/bin/env python3
"""PreToolUse hook (board writes): a card description is written so the app shows it formatted.

The app shows a description as rich text only when the whole value opens AND closes with a block tag
(`<p>`, `<h1>`–`<h6>`, `<ul>`, `<ol>`, `<blockquote>`); anything else is shown as plain text with every
tag as literal characters (app `src/domains/tasks/ui/rich-text.ts` → `looksLikeHtml`, copied below).
A `<pre>` block is fine inside, never first or last (bandit:tasks `references/board.md` → Card descriptions).

Any MCP server's `create_tasks` and `update_tasks`, recognised by the call's own shape. For each entry
with a non-empty `description`, the call is refused with exit 2 (the reason on stderr) when:

  1. the value does not open and close with one of those block tags (the app's own test);
  2. it holds escaped markup (`&lt;` before br, p, b, ul, ol, li or h1–h6);
  3. it holds a `<br>` tag (a new line is a new `<p>`);
  4. outside a `<pre>` block or `<code>`, it holds markdown: `**`, a `[text](url)` link, or a line or block that
     starts with `- `, `* ` or `# `.

Silent on every other call, on an empty or null description, and when the payload cannot be read.
"""
import json
import re
import sys

TOOL = re.compile(r"^mcp__.+__(create_tasks|update_tasks)$")
# The app's own test, word for word (rich-text.ts → HTML_DOCUMENT).
APP_HTML = re.compile(r"^\s*<(p|h[1-6]|ul|ol|blockquote)(?:\s[^>]*)?>[\s\S]*</(?:p|h[1-6]|ul|ol|blockquote)>\s*$", re.I)
ESCAPED = re.compile(r"&lt;/?(?:br|p|b|ul|ol|li|h[1-6])\b", re.I)
BR = re.compile(r"<br\s*/?>", re.I)
LITERAL = re.compile(r"<(pre|code)\b[^>]*>[\s\S]*?</\1>", re.I)  # prompt blocks and code: their text is literal
MARKDOWN = (
    (re.compile(r"\*\*"), "markdown bold (`**`)"),
    (re.compile(r"\[[^\]\n]+\]\([^)\s]+\)"), "a markdown link (`[text](url)`)"),
    (re.compile(r"(?:^|\n|<(?:p|li|h[1-6]|blockquote)\b[^>]*>)[ \t]*(?:[-*] |#{1,6} )", re.I),
     "a markdown list or heading line (`- `, `* `, `# `)"),
)
FIX = ("Write it as HTML: every line in `<p>…</p>`, headings `<h2>`/`<h3>`, lists `<ul><li><p>…</p></li></ul>`, "
       "bold and code only inside a block; a `<pre>` block only between two blocks, never last, so close a prompt "
       "block with its `<h2>Source</h2><p>…</p>` (bandit:tasks references/board.md → Card descriptions).")


def problems(description):
    """What is wrong with one description, as plain-words lines; empty when it is fine."""
    if not isinstance(description, str) or not description.strip():
        return []
    found = []
    if not APP_HTML.match(description):
        head = description.lstrip()[:12]
        tail = description.rstrip()[-12:]
        found.append(f"the app would show it as raw text: it must open and close with <p>, <h1-6>, <ul>, <ol> or "
                     f"<blockquote> (it opens {head!r} and ends {tail!r})")
    if ESCAPED.search(description):
        found.append("escaped markup (`&lt;p`, `&lt;br` …) that the app shows as literal tags")
    if BR.search(description):
        found.append("a `<br>` tag (a new line is a new `<p>`)")
    outside = LITERAL.sub(" ", description)
    found += [what for pattern, what in MARKDOWN if pattern.search(outside)]
    return found


def refusal(tool, given):
    """The lines to refuse this call with, or None."""
    if not TOOL.match(tool or "") or not isinstance(given, dict):
        return None
    lines = []
    for i, item in enumerate(given.get("items") if isinstance(given.get("items"), list) else []):
        if not isinstance(item, dict):
            continue
        name = item.get("taskId") or item.get("title") or f"entry {i + 1}"
        lines += [f"- {name}: {p}." for p in problems(item.get("description"))]
    return lines or None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    lines = refusal(payload.get("tool_name"), payload.get("tool_input"))
    if not lines:
        return 0
    print("\n".join(["📝 Description gate: a card description must be HTML the app shows formatted, or the card "
                     "shows raw tags.", *lines, FIX, "Then retry this call."]), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
