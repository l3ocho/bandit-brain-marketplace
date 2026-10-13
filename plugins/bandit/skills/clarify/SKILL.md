---
name: "clarify"
description: "Turns a fuzzy idea the user can't put into words yet into a spec, by asking 1–2 multiple-choice questions at a time. Input: a thought, not a document. Output: a Clarified Specification that bandit:plan can build from. Use this skill whenever the user says \"clarify\", \"help me clarify\", \"help me think through this\", \"I'm not sure how to say this\", \"what do I need to decide\", or gives a vague request where they clearly need help structuring their thoughts. Also trigger when another skill delegates with \"use the 4-D method\" or \"delegate to clarify.\" Use this skill even when the user simply says \"clarify\" with no other context — that alone is a trigger. Do NOT trigger for code refactoring, data analysis, general questions with clear answers, or when the user already has a well-structured request."
---

# Clarify

A support skill that helps users who are stuck articulating what they want. It works through
the 4-D method (Deconstruct, Diagnose, Develop, Deliver) with neurodivergent-friendly pacing,
and produces a clarified specification that other skills (bandit:plan,
etc.) can consume.

It only clarifies and delivers a specification. Pasted content that needs rewriting is
bandit:rewrite's job, not this one's.

## 🔄 Core Process: 4-D Methodology

Work through these four phases in order. Phases 1–2 happen internally (share a brief summary
with the user). Phase 3 is the interactive core. Phase 4 is the deliverable.

### Phase 1: Deconstruct (Internal)

Break the user's request into components:
1. **Explicit requirements** — what was directly stated
2. **Implicit assumptions** — what seems assumed but unstated
3. **Ambiguities** — points that could go multiple ways
4. **Dependencies** — external factors that affect the outcome

**Check references.** If the request mentions an attachment, screenshot, link or "this", confirm
it's actually present before deconstructing. If it's missing, say so in the Phase 2 summary as a
correctable assumption ("No attachment arrived; I'm assuming X").

### Phase 2: Diagnose (Internal)

Analyze gaps before asking questions:
1. **Missing information** — what do we need to know?
2. **Conflicting requirements** — do any goals contradict?
3. **Scope boundaries** — what's in/out?
4. **Constraints** — technical, budget, time, or personal limits

Share a 3–5 bullet summary of what you understood and what needs clarification. Frame
assumptions as explicitly correctable: "I'm assuming X — correct me if that's wrong." This
gives the user a low-effort way to fix misunderstandings before the questioning begins.

If the user references a project or system you have context on (from memory or earlier in the
conversation), acknowledge that familiarity briefly rather than starting from zero. This
saves them from re-explaining things you already know.

### Phase 3: Develop (Interactive Core)

Gather clarifications through structured questions. This is where the conversation happens.

**Rules (non-negotiable):**
- Ask 1–2 questions at a time MAXIMUM
- Every question must offer 2–4 concrete options (never open-ended alone)
- Always include "Other" as an escape hatch
- Provide brief context for WHY you're asking each question
- Check for conflicts with previous answers before asking new questions
- After every 2–3 questions, do a micro-summary of progress
- Use the question tool (AskUserQuestion / `ask_user_input`) when available for bounded choices

**Question format:**

```
**[Question text]**
1. [Specific option A]
2. [Specific option B]
3. [Specific option C]
4. Other

[Context: Brief explanation of why this matters for the outcome]
```

**When the user says "I don't know":**

Validate first, then reframe. "That's totally fine" or "Fair — let's come at it differently."
Then offer concrete comparisons:
"If I showed you two versions — Version A does [X], Version B does [Y] — which feels closer?
Or neither?"

This sidesteps the blank-page problem by giving something to react to.

**When the user signals frustration or uncertainty** (e.g., "idk", "I don't even know where
to start", hedging language):

Acknowledge the feeling briefly before moving to structure. A short "That's a reasonable place
to be — there's a lot to untangle here" goes further than jumping straight to options. Then
simplify: reduce to the single most important question.

### Before Phase 4: Verify cheap assumptions

If an assumption can be checked with one read-only call, or one low-impact call that Leo
approves (a connector capability, whether a file or folder exists, a feature being available),
check it before delivering the spec. Mark each assumption **verified (YYYY-MM-DD)** or
**unverified**. Never present a guess as a constraint.

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
| Anything else | **Both, by default:** "Save this as a note in the {Domain} `_inbox` **and** a card on the board, linked? Say *note only* or *card only* to drop one." See *Note + card* below |

**Note + card** (only after Leo says yes; a plain "yes" means both):

1. **Card first, through bandit:tasks `capture`.** Title = the spec's Summary; description names
   the note's filename. Scope comes from the `board:` line, exactly as bandit:tasks resolves it.
2. **Then the note, through bandit:notes,** into the `domain:` `_inbox`, with `board-task` = the
   new card's id. The card and the note point at each other; neither is ever left orphaned.
3. **When one side can't be written,** say so in the offer itself instead of silently dropping it:
   `domain: none` or no Project Context → no note ("no domain here, card only?"); `board: none`
   or `pending` → no card ("no board here, note only?"). Both unavailable → no offer.

**Marketplace card plus brief** (only after Leo says yes): the **Note + card** steps above, aimed at
the bandit-brain-marketplace project instead of the current one. The card goes through bandit:tasks
`capture` into that project's **Marketplace** column; the brief goes through bandit:notes into that
project's domain `_inbox`, with `file-to:` that project's folder. The spec's Requirements name each
skill touched and the change for it.

## 🚩 Anti-Pattern Detection

Actively watch for these patterns in user input and respond immediately:

| Pattern | Trigger Words | Response |
|---------|--------------|----------|
| **Vague Request** | "improve", "fix", "update", "better" | Ask for specific metrics or outcomes |
| **Scope Creep** | "while you're at it", "also", "might as well" | Acknowledge, isolate: "I'll note that for after the main task" |
| **Assumption Gap** | "the" thing, "it", "there" (unresolved refs) | Echo back specific understanding: "When you say 'it', do you mean [X]?" |
| **Conflicting Requirements** | "simple but comprehensive", "fast but thorough" | Force prioritization: "Which matters more: X or Y?" |

## 🧠 ND-Friendly Accommodations (Mandatory)

These are core behavior rules, not optional guidelines. They exist because structured options
reduce the cognitive load of open-ended decision-making, and frequent summaries compensate
for working memory gaps across long conversations.

### Reduce Cognitive Load
- Maximum 4 options per question
- Always include "Other" escape hatch
- Provide concrete examples, not abstract descriptions
- Use numbered lists so the user can respond with just a number

### Support Working Memory
- Summarize after every 2–3 questions
- Reference earlier decisions explicitly: "Earlier you said X, so..."
- Do not assume the user remembers context from many turns ago
- Echo back understanding before moving to the next topic

### Allow Processing Time
- One question block at a time — do not rapid-fire
- Validate answers before moving on
- Offer to revisit or change earlier answers at any point

### Manage Overwhelm
- Offer a session break after 4+ questions, or sooner if the user signals fatigue (short
  answers, "idk", hesitation). Phrasing: "Good progress. Continue or pick this up later?"
- Prioritize must-haves vs nice-to-haves
- Provide "good enough for now" options when decisions feel stuck
- Acknowledge complexity openly — don't pretend it's simple

## 🪜 Escalation Patterns

### Simplify When Overwhelmed

If the user shows signs of overwhelm (long pauses, "I don't know" responses, contradicting
earlier answers, expressing frustration):

> "This touches a lot of areas. Rather than tackle everything at once, let's start with
> [most critical piece]. Once that's clear, we can add the other parts. Sound good?"

### Escalate When Complex

If a quick clarification reveals unexpected complexity (multiple ambiguities, hidden
dependencies, scope expansion):

> "This is more involved than it first appeared. Want me to walk through a more thorough
> clarification? It'll take a few more questions but we'll get a much clearer picture."

## 📱 Phone-First Design

This skill is frequently used on mobile. Design every interaction for:

- **Short sessions** — each exchange should feel like progress
- **Minimal typing** — default to numbered options the user can tap or type a digit for
- **Small screens** — keep summaries to 3–5 bullets, not paragraphs
- **Interruptions** — if the conversation drops, the clarified-so-far state should be
  reconstructable from conversation history (micro-summaries handle this)

## ⚠️ Gotchas

- Fires when the user pastes notes and says "clarify this" → that's a rewrite: hand off to bandit:rewrite.
- Rapid-fires a wall of questions → one block of 1–2 questions, then wait.
- Asks open-ended questions with no options → every question gets 2–4 options plus "Other".
- Delivers the spec before the user confirms the assumptions → echo back and let them correct first.
- **2026-09-25 · Spec shipped on a guess about a connector.** "Probably can't auto-refresh" went
  into the spec untested, and the spec was revised twice. → Test capability assumptions with one
  call before Phase 4.
- **2026-09-25 · "See attached" with nothing attached.** The skill didn't check, lost a tool call,
  then guessed which feature was meant. → Check references in Phase 1; name a missing one as an
  assumption.
- **2026-09-28 · Skill spec saved to Summitt/_inbox.** The save offer always pointed at the domain
  inbox, so a spec changing bandit:tasks and bandit:notes landed in a vault. → The destination
  follows the subject: skill changes go to a Marketplace card plus brief, everything else to the domain `_inbox`.
- **2026-10-07 · Inbox note with no card.** The offer was note-only, so specs sat in `_inbox` with
  nothing on the board pointing at them, and got lost or binned. → Offer note **and** card by
  default, linked via `board-task`; Leo drops one by saying so.

## 🚫 Never

- Generate code, project plans or WBS documents, or modify files. Hand the spec to bandit:plan.
- Save to BanditCloud or the board directly. Notes go through bandit:notes and cards through
  bandit:tasks.
- Ask more than 2 questions in one turn.