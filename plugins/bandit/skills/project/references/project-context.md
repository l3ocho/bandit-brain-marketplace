# 🧭 The Project Context block

> The one block every skill reads to learn which project it is in. This file owns its format; other skills point here and never restate it.

## 🧭 Project Context Section

This skill **owns the Project Context**: the one block every skill reads to learn which project
it is in (`bandit:notes`, `bandit:minutes`, `bandit:tasks`, `bandit:plan`, `bandit:finance`). The same block works on every surface: in the
Claude.ai project instructions, and in a repo's `CLAUDE.md` on Claude Code. Other skills read it
and point here; they never restate its format.

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

Read by every `bandit` skill.
**Home board first. Read and write across the domain. Nothing outside it.**
Names only: skills resolve IDs live via `get_context`. No hardcoded IDs, ever.
```

| Key | Values | Filled from (phases: `references/interview.md`) |
|---|---|---|
| `domain` | MyNotes domain folder (e.g. `Acme`), or `none` | Phase 4 Domain question. `none` for a custom path and artifact-only |
| `project` | The project's own slug (e.g. `home-reno`) | Phase 4 slug question. When it wasn't asked, suggest a kebab-case slug from the project name and confirm it |
| `type` | `product_service` · `workflow` · `claude_marketplace` | Phase 1 question 1 |
| `board` | `project "{name}"` (the **home board**, filed inside the domain's board folder) · `none` · `pending` | Phase 1 question 5. Names exactly as `get_context → boards` returns them, quoted. `folder "…"` and `global` are retired (2026-10-14) |
| `prefix` | 2–3 character filename prefix, or `none` | Phase 4 prefix. `none` when artifact-only |
| `dev` *(optional)* | `true`, or the line is absent | Phase 1 dev question (`references/interview.md`). Only for technical development projects that use the dev card workflow (bandit:tasks, bandit:notes) and sprints (bandit-dev:sprint, Claude Code) |
| `finance` *(optional)* | `accounts "{name}", "{name}"`: Finance account names exactly as `finance_get_context` returns them, quoted, comma-separated; or the line is absent | Phase 1 Finance question (`references/interview.md`). Limits bandit:finance to those accounts; absent = every account the member can see (bandit:finance `references/scope.md` owns the rule) |

**Format rules** (other skills parse this, so it is fixed): the heading text is `Project
Context`; one `key: value` per line; these five required keys, lower-case, plus the optional
`dev: true` line right after `prefix` (written only when the project opted in; otherwise
omit the line, never `dev: false`) and the optional `finance:` line after it (written only when
the project limits Finance; never empty, never `all`); nothing else inside the block except the closing lines. `domain`
and `board` together set the board scope: the domain is the board's top-level folder of the same
name, with its subfolders; the home board comes first, the rest of the domain is open to read and
write, and nothing outside it is (bandit:tasks `references/scope.md` owns the rule).

**How readers treat it:** a missing required key → ask; a missing `dev` line → not a dev project
(never ask); a missing `finance` line → every visible account (never ask); a value that doesn't check out (the board name no
longer resolves, the domain isn't in `MyNotes`) → stop and say so, never guess at the nearest
match. `board: none` or `pending` → bandit:tasks reads the domain and writes nothing (except
`/bandit:tasks load` on `pending`).

### Repo copy (Claude Code)

For a `dev: true` project, Claude Code reads the same block from the repo's `CLAUDE.md`. This
skill **produces the exact block text** (identical to the Claude.ai one) and hands it over as a
repo change for Claude Code to make; it never writes to the repo itself. Whenever an update changes
the Claude.ai block, the hand-over adds one line: *the repo `CLAUDE.md` Project Context needs the
same edit.*

**Dev mirror.** When onboarding or auditing a `dev: true` project, read `references/dev-mirror.md`
and hand over its repo change: the mirror-check script in `.claude/hooks/`, a `Stop` command hook
in `.claude/settings.json` that runs it, and the gitignored stamp. From then on the script itself
copies `CLAUDE.md` + `.claude/` into the synced `MyNotes/{Domain}/Claude/code-{slug}/` at each
turn's end (no model, no connector), `.claude/` stored as `claude/`, never `settings.local.json` or `.claude/worktrees/`.
Git stays the source. Hand over the installed reference's script, never the vault mirror's (it lags).

### Claude Code twin (projects without `dev: true`)

A project without `dev: true` (any `type:`) has a Claude Code surface when the user answers yes to the
Claude Code question (`references/interview.md`, Phase 1) or `Claude/code-{slug}/` already exists.
It then runs as **twins**: the Claude.ai instructions and a Claude Code `CLAUDE.md`. The surface
never changes scope: `type:` decides it (a `product_service` twin still writes only inside its own
`board:`). A `dev: true` project gets the dev mirror instead, never a twin.

| Part | Rule |
|---|---|
| Core | Byte-identical in both: everything outside the Environment section, `**Version:**` included |
| `## 🖥️ Environment` | The one section that differs (`references/reference-template.md`): Claude.ai = planning, no local files; Claude Code = local working files, execution |
| Vault copy | `MyNotes/{Domain}/Claude/code-{slug}/CLAUDE.md`, as an approved row: created fail-closed, then edited with its bare-hex etag on each version. Old versions live in `ai-{slug}/` |
| Live file | Handed to Claude Code as a local change. This skill never writes the local folder |
| Reference doc | One copy only, the `{prefix}-prompt-reference-v{N}.md` in `ai-{slug}/`. Claude.ai reads its **Project copy** (`references/output.md`); the Claude Code `## 🖥️ Environment` names that vault path and reads it through BanditCloud when a rule points to it. Never copied into the local folder, never `@`-imported (that loads it every session) |
| Permissions | `code-{slug}/claude/settings.json`: the permission rules and hooks the Claude Code twin runs under. Same handling as the vault copy: an approved row, created fail-closed, edited with its bare-hex etag, handed to Claude Code as a local change. Never `settings.local.json` |
| Working folder (S12) | The layout guard: `code-{slug}/claude/hooks/workdir.py` (this skill's `scripts/workdir.py`, byte for byte), its two hooks and allow rules in `settings.json`, and one Environment line. Read `references/workdir.md` on onboarding, on every twin version change, and for an S12 row |

**Twin sync.** Any version change to either twin produces the matching change for the other in
the same output, and ends with one line: *apply both: paste the Claude.ai instructions, and have
Claude Code update its `CLAUDE.md`.*
