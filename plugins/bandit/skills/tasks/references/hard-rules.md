# 🔒 Hard rules — every skill, every write

Part of `bandit:tasks`, read by every skill of the marketplace before it writes a card, a note or a
comment. One line per rule, stated as an order; each rule's detail stays in its one home, named on
the line. A rule here is never softened, skipped or rounded to the nearest fit: a write that would
break one is not sent, and the reason is said in one line.

## 🏷️ Names

- A note's title is lowercase kebab-case: `{slug}-YYYY-MM-DD` for a dated note, `{slug}` for an evergreen one, never a kind label in front (bandit:notes `references/conventions.md` §4).
- A card's short id follows its board; an id already written in a paper, a note, a commit or a chat is never rewritten (`references/board.md` → Card IDs).
- A tag name never starts with `lane/`, `stage/` or `sprint/`: those are the app's (`references/board.md` → Tags).
- One slug per project, the Project Context's `project:`, used everywhere it is named (bandit:project `references/project-context.md`).

## 🧰 Tool limits

- At most 100 entries in one bulk call, one entry per task; read every entry's result (`references/board.md` → Many cards in one call).
- No hardcoded id, ever: every id is resolved live through `get_context` (`references/scope.md`).
- Write only inside the domain, and only where the `write:` line allows when there is one (`references/scope.md`).
- A refused call is reported with its reason, never retried as a variant (`references/errors.md`).

## 📏 Field limits

- A card description is block-tag HTML only: no markdown, no `<br>`, a `<pre>` only between two blocks; read back after the write (`references/board.md` → Card descriptions).
- A card's Spec section is locked once written: a change goes through a `Spec change needed:` comment (`references/dev.md` → Spec lock).
- At most one `stage/*` tag on a card, and none beside `lane/incident` (`references/board.md` → Tags).
- A dev card's checklist holds its build steps and a `Gate:` line for each card that blocks it; a sprint card then carries its check lines last, ticked only when each check's verdict is in, and its approval sits on the sprint's debug card (a sprint committed before that rule: the approval line last on the card) (`references/dev.md` → Card fields; bandit-dev:sprint `references/templates.md` → Check lines, Approval line).
- A note holds at most 200 KB; a longer one is split by section on the user's yes, never cut (bandit:notes `references/storage-app.md` → Refusals).
- A note's summary is one sentence of at most 25 words (bandit:notes `references/conventions.md` §5).

## 🗂️ Where information goes

- A card's description holds what the card is: its Spec and its short Technical plan. Never its state, its history or a log.
- Anything long goes in a note linked to the card: a plan, a brief, a spec draft, a report, minutes (bandit:notes `references/other-skills.md`).
- A comment is the card's dated log: what was delivered, decided or found, and by whom. Never a Spec change, never placement or scheduling.
- A sub-task is one step in a few words, never prose.
- A note's body never carries card state (column, lane, stage): the card holds it (bandit:notes `references/conventions.md` §13).
