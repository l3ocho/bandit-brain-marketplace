# 🧭 The Project Context block

> The one block every skill reads to learn which project it is in. This file owns its format; other skills point here and never restate it.

## 🧭 Project Context Section

This skill **owns the Project Context**: the one block every skill reads to learn which project
it is in (`bandit:notes`, `bandit:minutes`, `bandit:tasks`, `bandit:plan`, `bandit:finance`). A
project has **one** copy of it, in its one instructions file: the Claude.ai project instructions
for a project that runs on Claude.ai, the folder's `CLAUDE.md` for a project that runs in Claude
Code (`references/surfaces.md`). Other skills read it and point here; they never restate its format.

Always insert it, **immediately after Project Overview** — the other skills read it before doing
anything, so it must be near the top.

```markdown
## 🧭 Project Context

domain: {domain}
project: {project}
type: {type}
board: {board}
prefix: {prefix}
{dev: true — this line only when the project opted in}
{finance: accounts "{name}", "{name}" — this line only when the project limits Finance to some accounts}
{design: column "{name}" — this line only when the project turns design cards on}
{write: board "{name}", board "{name}" column "{name}" — this line only when the project writes on fewer boards or columns than its domain}
{notes: none — this line only when the helpers keep no notes for this project}

Read by every `bandit` skill.
**Home board first. Read and write across the domain. Nothing outside it.**
Names only: skills resolve IDs live via `get_context`. No hardcoded IDs, ever.
```

| Key | Values | Filled from (phases: `references/interview.md`) |
|---|---|---|
| `domain` | The project's board folder: a top-level folder name (e.g. `Acme`), or, for a project that should see and change only a subfolder, the path of folder names from the top-level one down joined by ` / ` (e.g. `Acme / Clients / Beta`; folders nest three levels deep); or `none` for a project with no board folder | Phase 1 Domain question, from the live folders of `get_context` |
| `project` | The project's own slug (e.g. `home-reno`) | Phase 1 slug question: suggest a kebab-case slug from the project name and confirm it |
| `type` | `product_service` · `workflow` · `claude_marketplace` | Phase 1 question 1 |
| `board` | `project "{name}"` (the **home board**, filed inside the domain's board folder) · `none` · `pending` | Phase 1 question 5. Names exactly as `get_context → boards` returns them, quoted. `folder "…"` and `global` are retired (2026-10-14) |
| `prefix` | 2–3 characters, or `none`. Names the project's working-folder task folders (`references/workdir.md`) | Phase 1 prefix question |
| `dev` *(optional)* | `true`, or the line is absent | Phase 1 dev question (`references/interview.md`). Only for technical development projects that use the dev card workflow (bandit:tasks, bandit:notes) and sprints (bandit-dev:sprint, Claude Code). Their home board is Technical: bandit:tasks' dev rules follow the board's profile, and this line marks the project for sprints and onboarding's dev board shape |
| `finance` *(optional)* | `accounts "{name}", "{name}"`: Finance account names exactly as `finance_get_context` returns them, quoted, comma-separated; or the line is absent | Phase 1 Finance question (`references/interview.md`). Limits bandit:finance to those accounts; absent = every account the member can see (bandit:finance `references/scope.md` owns the rule) |
| `design` *(optional)* | `column "{name}"`, or `column "{name}" on board "{board}"`: a column name exactly as `get_context` returns it, quoted; or the line is absent | Added when the user turns design cards on (an instructions update); onboarding does not ask. A screen-changing card then gets its own design card in that column, whose handover unblocks the build (bandit:tasks `references/dev-workflow.md` → Design card owns the rule) |
| `write` *(optional)* | `board "{name}"` or `board "{name}" column "{name}"`, comma-separated: board and column names exactly as `get_context` returns them, quoted; or the line is absent | Added on the user's word in an instructions update; onboarding does not ask. The project writes only on those boards, and on a board named with a column only in that column; it still reads its whole domain. Absent = it writes across its domain (bandit:tasks `references/scope.md` owns the rule) |
| `notes` *(optional)* | `none`, `app`, or the line is absent | Phase 1 Notes question (`references/interview.md`). The project's notes are in the app's Notes, on its board: that is what an absent line means, and what `app` says in a block written before 2.0.0 (valid, never a finding, never added to a new block). `none` = the helpers write no note for this project and say so when asked to: its records are kept elsewhere by the project's own rules. bandit:notes owns what the storage does (`references/model.md` there) |

**Format rules** (other skills parse this, so it is fixed): the heading text is `Project
Context`; one `key: value` per line; these five required keys, lower-case, plus the optional
`dev: true` line right after `prefix` (written only when the project opted in; otherwise
omit the line, never `dev: false`) the optional `finance:` line after it (written only when
the project limits Finance; never empty, never `all`), the optional `design:` line after that
(written only when the project turns design cards on), the optional `write:` line after it (written only when the project writes on fewer boards or columns than its domain; never empty) and the optional `notes:` line last
(`none`, or the older `app`; never any other value); nothing else
inside the block except the closing lines. `domain`
and `board` together set the board scope: the domain is the board folder the `domain:` line names
(a top-level folder, or the folder its path leads to), with every subfolder in it; the home board comes first, the rest of the domain is open to read and
write, and nothing outside it is (bandit:tasks `references/scope.md` owns the rule).

**How readers treat it:** a missing required key → ask; a missing `dev` line → not a dev project
(never ask); a missing `finance` line → every visible account (never ask); a missing `design` line → the design step runs on the build card itself (never ask); a missing `write` line → the project writes across its domain (never ask); a missing `notes` line → the notes are in the app's Notes (never ask); `notes: none` → no note is written or filed for this project, and the helper says so in one line; a value that doesn't check out (the board name no
longer resolves, the domain is not a board folder) → stop and say so, never guess at the nearest
match. `board: none` or `pending` → bandit:tasks reads the domain and writes nothing (except
`/bandit:tasks load` on `pending`).

**One copy.** There is no second copy of the block to keep in step: a project runs on one surface
and its one instructions file carries the block. A block found in two places for the same project
(an old Claude.ai project beside a `CLAUDE.md`) is a finding of this skill's audit: the row names
the one that is live and proposes retiring the other (`references/audit.md`).
