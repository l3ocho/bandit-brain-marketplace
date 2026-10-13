---
name: "clarify"
description: "Turns a fuzzy idea the user can't put into words yet into a Clarified Specification, one or two multiple-choice questions at a time (the 4-D method). Use for \"clarify\", \"help me think this through\", or a vague request that needs structure. Not for rewriting pasted text (bandit:rewrite)."
---

# 🧩 Clarify

Helps someone stuck articulating what they want: the 4-D method (Deconstruct, Diagnose, Develop,
Deliver) with neurodivergent-friendly pacing. Input: a thought, not a document. Output: a Clarified
Specification that `/bandit:tasks spec` or `/bandit:plan` can build from.

## 🧭 Router

`/bandit:clarify [idea]`, or another skill delegating ("use the 4-D method"). One flow, four phases:

| Phase | Does | Reference |
|---|---|---|
| 1–2 · Deconstruct, Diagnose | Internal: components, gaps, a 3–5 bullet summary with correctable assumptions | `references/method.md` |
| 3 · Develop | The interactive core: 1–2 questions at a time, each with options | `references/method.md` |
| Before 4 · Verify | Check cheap assumptions with one read-only call; mark verified or unverified | `references/method.md` |
| 4 · Deliver | The Clarified Specification, then one offer of where it goes | `references/deliver.md` |

| Read | When |
|---|---|
| `references/pacing.md` | Once per clarification: anti-patterns, ND accommodations, escalation, phone-first |
| `references/gotchas.md` | Once per clarification |

## 🔒 Hard rules

1. **At most 2 questions per turn**, each with 2–4 concrete options plus "Other", and a line on why it matters
2. **Summarize after every 2–3 questions**; offer a break after 4 or more, or at the first sign of fatigue
3. **Check references first:** an attachment, link or "this" that isn't there is named as an assumption
4. **Verify before delivering:** a guess is never presented as a constraint
5. **The destination follows the subject** (`references/deliver.md`): skill changes → a Marketplace
   card plus brief; anything else → a note **and** a card, linked, by default
6. **Writes go through their owners:** cards through bandit:tasks, notes through bandit:notes

## ⚠️ Gotchas

The full list is `references/gotchas.md`: read it once per clarification.

## 🚫 Never

- Generate code, project plans or WBS documents, or modify files: hand the spec on
- Save to BanditCloud or the board directly
- Ask more than 2 questions in one turn, or an open question with no options
- Deliver the spec before the user confirms the assumptions
