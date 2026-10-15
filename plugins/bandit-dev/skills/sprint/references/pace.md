# 🎙️ Interview, pace and proactive means

> Read once at the start of `plan`: how questions are asked and how investigation runs.

## 🎙️ Interview and pace

- **The user's words are the baseline.** Restate their request in their own words first. Build exactly that; anything that differs (a rule the code forces, a split, a different approach) is a decision row before it is written anywhere.
- **Read before asking.** The repo, the cards, the briefs, the ledger and the chat answer most questions: read them. Ask only what none of them can answer. A question the code could answer is a failure, not diligence.
- **Gather before asking.** Run the read-only investigations first (below), so every question arrives with an answer to approve.
- **One consolidated list per gate**, grouped by card, each item with a recommendation. "Go with the recommendations" is a valid answer and applies to the whole list. Ask follow-ups only for what the answers raise.
- **Never re-ask.** Before any question, check the chat, the cards and the ledger for the answer (a date, a decision, an approval). Use it and record it.
- **Plain words, no codes.** Never invent labels (Q1, A2, D3, F1, "option B", step numbers) for the user to read or answer with; name the thing in words. Never report counts of what was created.
- **Short reports.** After each step: what was found, what was done, what is next, in three lines at most. No waiting between steps that need no input; stop only at steps 3, 9 and 10.
- A decision that opens a **large new requirement** is parked as a card outside the sprint, with the rule recorded; ask one yes or no whether it joins. The user's word that a card stays in the sprint is final.

---

## 🛰️ Proactive means

- **Investigate in parallel, read-only.** One investigator per card for open questions (what exists in code, what the card claims, what is missing); at most one live-browser check at a time, told to write nothing on existing data (planning only; see Test data in `references/plan.md`). Brief them with the card's Spec and the report shape in `references/plan.md`.
- **Spot-check decisive claims** before they enter a card or plan; an unconfirmed claim goes under "Verify first".
- **Anticipate the usual traps** at the step where they bite: XL at sizing, stale Specs at step 9, migration numbers at step 5, a card edited by someone else before any rewrite.
- **Surface problems as decision rows** in the one decision table (`references/plan.md` → Conventions), plain words, no numbers; one answer approves all, some or none.
- **Offer the next move** at the end of every step in one line.
