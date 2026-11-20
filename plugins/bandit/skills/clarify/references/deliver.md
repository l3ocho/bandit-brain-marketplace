# 📦 Phase 4: Deliver

> Read when the questions are done: the Clarified Specification template and where it goes.

### Phase 4: Deliver

Produce the clarified specification using this template:

```markdown
## Clarified Specification

### Summary
[1-2 sentence description of what will be done]

### Scope
**In Scope:**
- [Item]

**Out of Scope:**
- [Item]

### Requirements
| # | Requirement | Priority | Notes |
|---|-------------|----------|-------|
| 1 | ... | Must | ... |
| 2 | ... | Should | ... |

### Assumptions
- [Assumption made during conversation] — verified (YYYY-MM-DD) / unverified

### Open Questions
- [Any remaining ambiguity, if any]
```

After the spec, offer one line. **The destination follows the subject:**

| The spec is about | Offer |
|---|---|
| Changing one or more **skills** | **"Save as a Marketplace card plus brief?"** — one card in the **Marketplace** column of the bandit-brain-marketplace project's board, with one brief naming every skill touched. See *Marketplace card plus brief* below |
| Work for a **dev project** (its home board is Technical: `get_context → boards → profile`) | **"Turn this into a card with `/bandit:tasks spec`?"** — `spec` takes this Clarified Specification as its input (`Source: clarify`), places the card in its area column and writes its brief. No separate note: the brief is the note |
| Anything else | **Both, by default:** "Save this as a note for {Domain} **and** a card on the board, linked? Say *note only* or *card only* to drop one." See *Note + card* below |

**Note + card** (only after the user says yes; a plain "yes" means both):

1. **Card first, through bandit:tasks `capture`.** Title = the spec's Summary; description names
   the note by its name. Scope comes from the `board:` line, exactly as bandit:tasks resolves it.
2. **Then the note, through bandit:notes,** as a draft for the `domain:` that waits for review,
   linked to the new card (bandit:notes links it; in the app's Notes that is `notes_link_card`).
   bandit:notes looks for a note of that name first and updates the one it finds instead
   of making a second. The card and the note point at each other; neither is ever left orphaned.
3. **When one side can't be written,** say so in the offer itself instead of silently dropping it:
   `domain: none` or no Project Context → no note ("no domain here, card only?"); `board: none`
   or `pending` → no card ("no board here, note only?"). Both unavailable → no offer.

**Marketplace card plus brief** (only after the user says yes): the **Note + card** steps above, aimed at
the bandit-brain-marketplace project instead of the current one. The card goes through bandit:tasks
`capture` into that project's **Marketplace** column; the brief goes through bandit:notes as a draft
for that project, linked to the card, in whichever storage holds that project's notes. The spec's
Requirements name each skill touched and the change for it.

**Too large.** The app's Notes refuses a note over 200 KB: propose splitting the spec by section:
the first part linked to the card, the others related to it. Nothing is cut or saved shorter.
