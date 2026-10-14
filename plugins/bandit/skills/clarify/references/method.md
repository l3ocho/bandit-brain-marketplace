# 🔄 The 4-D method: phases 1–3

> Read at the start of every clarification: Deconstruct, Diagnose, Develop, and the cheap-assumption check before delivering.


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

If an assumption can be checked with one read-only call, or one low-impact call that the user
approves (a connector capability, whether a file or folder exists, a feature being available),
check it before delivering the spec. Mark each assumption **verified (YYYY-MM-DD)** or
**unverified**. Never present a guess as a constraint.
