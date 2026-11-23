# 🤝 Other skills and chats writing a note

> Read when another skill, or a chat, writes a note: who writes what, as kinds and places, and the exceptions to the inbox rule.

## 🤝 Other skills and chats writing a note

Any note created by another skill or in a chat follows the same rules. It asks this skill for the
note's kind, name and place and never names a tool path of its own. It is created as a **new**
note in the Inbox (create without a duplicate first), carries its kind, its `summary` and the
kind's fields (Part 2 §5), follows the body shape in Part 2 §12, and waits there for the user's
review. Skills never edit an existing note in the Inbox, except their own draft from this
conversation on the user's explicit request (`references/model.md` → *The inbox is the user's*).
A project whose Project Context says `notes: none` gets no note from any skill: the skill says so
in one line and hands its text over in the chat instead.

| | How (`references/storage-app.md`) |
|---|---|
| A draft for review | `notes_create` on its board, status `inbox` |
| Its place | A board, and a column of it (Places) |
| Written straight in | Filed with `notes_file` in the same step |

**Who writes what:**

| Skill | Kind | Place |
|---|---|---|
| bandit:minutes | `minutes` | Inbox first: created in the Inbox of the domain's workflow board, then filed there by the review |
| bandit:plan (both modes) | `reference` (the project plan, the architecture, the WBS) | **Written straight in**, not to the Inbox, because they're worked on across many sessions: the project's board, in the column of the area it is about (Places). Still Part 2: kind, status, summary, name |
| bandit-dev:sprint | the sprint's records (plan, execution prompt, ledger, report, briefs) | **Written straight in**, for the same reason: the project's board with the tag `sprint-{name}` |
| bandit:tasks (dev projects) | a card's `brief` and `plan` | Linked to its card from the start and waiting in the Inbox for review: a plan is linked with no summary, so it waits until the review gives it one (`references/storage-app.md` → Status and filing). Part 2 §13 |
| bandit:project | `reference`: the project's reference doc (`{slug}-reference`) and, for a project that runs on Claude.ai, the copy of its instructions (`{slug}-instructions`) | **Written straight in**, on the user's yes to its row: the project's board, in the hub note's column. One note each, updated in place: the app keeps the text before each save as a version |
| bandit:audit | `log` (a domain's structure audit report, `audit-{YYYY-MM-DD}`) and `reference` (the self-check stamps, `{domain}-audit-stamps`) | **Written straight in**, as the script printed it: the domain's workflow project's board. The report is archived when the next audit or `close` replaces it; the stamps note is updated one section at a time. Its snapshot is a data file in `.audit/` in the folder Claude Code runs from, not a note |
| bandit:tasks `done`, bandit-dev:sprint `close` | a finished card's conclusions | The `Conclusions` section of the card's linked note, replaced at each close; a card with no note gets a `note` linked to it, on the user's yes, waiting in the Inbox (`references/conclusions.md`) |

- **A project's instructions and settings are not notes.** The file a project runs on (the
  Claude.ai project instructions, or `CLAUDE.md` and `.claude/` in its folder) is bandit:project's,
  and lives with the project. The two reference notes in the table are the only settings text in
  the app.
- **Files that are not text** (a sprint's map, a data file, a recording, a working-folder
  manifest) are never notes: each skill names their home in the project's folder.
- **Leftovers.** A note used only to produce another (an inbox draft filed elsewhere, a superseded
  draft, an applied feedback note) is archived (status `archived`), or deleted on the user's word,
  **in the same step that consumed it**, and only on proof: the successor exists and was read.
  Never because a note looks done or its card is missing; unsure → it stays.
- **bandit:tasks** owns the task vocabulary. Notes reuse it verbatim (kind, handler, lane as the
  bare value) and name their card with the card link. This skill never writes to the board.
- **Dev projects** (`dev: true` in the Project Context): plan notes and the WBS card links exist
  **only** there (Part 2 §13). Without the flag nothing changes. Plan notes go **inbox-first**, like
  every skill-written note, except sprint records, which are written straight in. Because a plan
  exists only on dev projects, `file` and `lint` apply the plan-note rules to any plan note,
  whichever project they run from (usually the domain workflow project).
- **Lookup for bandit:tasks: the notes linked to this card.** bandit:tasks names the card, and the
  note's title from its `Brief:` or `Technical plan` line (a line written before, ending in `.md`,
  has it stripped first). `notes_list` of the card's board; the notes whose `cards` hold the card
  are its notes: its brief, and its plan unless it is a sprint plan (tagged with the sprint,
  Part 2 §13). Reviewed means out of the Inbox. Places stay here; bandit:tasks never restates them.
