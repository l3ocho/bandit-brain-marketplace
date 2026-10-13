---
name: "rewrite"
description: "Rewrites text the user already has (messy notes, docs, brain dumps, transcripts) into clean, scannable, ND-friendly markdown with emoji-anchored headings, in one pass, nothing added. Use to clean up, restructure, deduplicate or make text readable. Not for clarifying a vague idea (bandit:clarify)."
---

# ✍️ Rewrite

Turns messy, hard-to-parse text into clear markdown for neurodivergent readers. It rewrites what is
there: no questions, no new ideas.

## 🧭 Router

`/bandit:rewrite`, with the content pasted or attached. One procedure:

| Step | Does | Reference |
|---|---|---|
| 1 · Ingest and audit | Inventory, structure, redundancy map, data type per chunk, unclear spots | `references/rewrite.md` |
| 2 · Design the structure | Heading outline, H1–H4, one emoji landmark per heading | `references/rewrite.md` |
| 3 · Write | Gather, merge, rewrite plainly, format by data type | `references/rewrite.md` |
| 4 · Final pass | Dedup, heading scan, length, consistency; then output and open questions | `references/rewrite.md` |

## 🔒 Hard rules

1. **Nothing added.** Expand only what is there; a gap goes into `## ❓ Open questions` at the end,
   with an offer to run `/bandit:clarify` on it
2. **Nothing dropped.** The final pass checks every inventory item made it in
3. **Format follows the data:** tables for comparisons, numbered lists for sequences, checkboxes for actions
4. **Code stays as written:** structure the text around it
5. **Deliver the file** (inline for short input). A vault save goes through bandit:notes

## ⚠️ Gotchas

- Adds ideas, opinions or recommendations that weren't in the source → expand only what's there; flag gaps instead of filling them.
- Drops content during the merge → the final pass checks every inventory item made it in.
- Writes straight into BanditCloud with a hard-coded path → deliver the file; vault saves go through bandit:notes.
- Treats a bare "clarify" with no content as its job → that's bandit:clarify.

## 🚫 Never

- Invent new points, facts or decisions
- Rewrite code inside code blocks
- Save into the MyNotes vault directly
