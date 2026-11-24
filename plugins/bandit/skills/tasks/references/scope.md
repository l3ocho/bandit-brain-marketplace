# 🗺️ Scope — the home board and the domain

Read the `## 🧭 Project Context` section before every read or write: in the Claude.ai project
instructions, or in the repo's `CLAUDE.md` on Claude Code. The block's format is owned by
bandit:project. Three keys set the scope:

| Key | Gives | Example |
|---|---|---|
| `board:` | The **home board**: the project's own board, the default for new cards, shown first | `board: project "Home Reno"` |
| `domain:` | The **domain**: the board folder it names, **with every subfolder in it**, at any depth: a top-level folder (structure rule S1 makes the names match), or a path of folder names from the top-level one down joined by ` / ` for a project that should see and change only that subfolder | `domain: Acme` → folder `Acme` + `Clients` + `Clients`'s own `Beta`; `domain: Acme / Clients` → `Clients` + `Beta` |
| `write:` *(optional)* | The **writable part** of the domain: only these boards, and on a board named with a column only that column. Reads stay the whole domain | `write: board "Office" column "Legal"` |

```
board: project "Home Reno"
board: none
board: pending
```

## 🧱 The rule

**Home board first. Read and write across the domain. Nothing outside it.**

| Where a card sits | Read | Write |
|---|---|---|
| Home board | ✅ | ✅ The default for every new card |
| Another board in the domain | ✅ | ✅ Name the board in the reply ("on Garden"), and add a card comment naming the source project: `From {project}: {what changed}` |
| Outside the domain, linked to a domain card (it blocks one, or one blocks it) | Title, board and state only | ❌ Never |
| Outside the domain, not linked | ❌ Never shown, counted or summarised | ❌ Never |
| Untriaged (no board) | Only from the domain's **workflow** project (`type: workflow`) | That project files them, into its own domain only |

**The `write:` line narrows the writes.** With one, a write (a new card, a move, a field, a comment, a sub-task, a tag) goes only to a board it names, and on a board named with a column only to a card in that column: a new card lands in it, and no card is moved into or out of it from another column. Any other write in the domain is refused before the call and said in one line, naming the line; the reads above are unchanged.

Board rules still hold on every board: a locked Spec changes only through `Spec change needed:` or
`spec reconcile` (`references/dev.md`), deletes are confirmed (`references/board.md` → Safety).

## 🔎 Resolving it

1. `get_context` once. Its `boards` carry each board's folder, and its `folders` are the
   top-level folders with their child folders. **The domain's boards** = every board whose
   folder is the domain's folder or any folder under it, at any depth. A path is followed from the top-level folder down, each
   name a child of the one before. No folder of that name, or a path that leads nowhere → stop and say so; never guess
   the nearest match.
2. **The home board** = the `board:` name. It must be one of the domain's boards; a home board
   outside its domain folder → stop and say so (bandit:audit S4).
3. **The writable part** = the `write:` line's boards and columns, each one of the domain's boards and that board's column; one
   that isn't → stop and say so. No `write:` line → the whole domain.
4. Keep these sets for the turn. 🔴 **No hardcoded IDs, ever**: a stored ID is a stale ID.

## 🧹 Filtering the household-wide views

`list_tasks` with `view: "inbox"`, `"execution"`, `"week"` or `"workload"`, and `list_tasks`
without a `boardId`, return **every board in the household**. Before a result is shown, counted or used:

- **Keep** the domain's cards; **drop** the rest, then re-count. Report the home board first, then
  the rest of the domain grouped by board
- **Keep** a card outside the domain only when it blocks, or is blocked by, a kept card: title,
  board and state, marked `outside the domain`
- **Untriaged** stays only for the workflow project; every other project drops the column
- **Inbox groups** go with their column, kept or dropped with it; they are the signed-in member's own, so another member's never show
- A **recurring projection** (no task row) is kept by its series' project
- The five-item cap and every count in a report are counted **after** the filter

## 🚦 The `board:` values

| `board:` | Behaviour |
|---|---|
| `project "{name}"` | The rule above |
| `none` | Not board-backed. Read the domain, **write nothing**. Say the project has no board |
| `pending` | The board isn't designed yet. Read the domain, **write nothing**, except `/bandit:tasks load` (the design step for a WBS-backed project) and `/bandit:tasks onboard` (sets the scope). Otherwise say: design the board, then update the `board:` line |
| `folder "…"` · `global` | **Retired (2026-10-14):** the domain replaces them. Stop and say: run `/bandit:project update` to set `board: project "{name}"` |
| No Project Context (a plain chat, no project) | No domain: ask which domain before any read of a household-wide view |

`domain: none` → no domain: the home board alone, read and write. A legacy
`## 🗺️ Task Board Scope` section with a `scope: …` line is read exactly like a `board:` line.
