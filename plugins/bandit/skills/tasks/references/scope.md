# 🗺️ Scope — the home board and the domain

Read the `## 🧭 Project Context` section before every read or write: in the Claude.ai project
instructions, or in the repo's `CLAUDE.md` on Claude Code. The block's format is owned by
bandit:project. Two keys set the scope:

| Key | Gives | Example |
|---|---|---|
| `board:` | The **home board**: the project's own board, the default for new cards, shown first | `board: project "Home Reno"` |
| `domain:` | The **domain**: the board's top-level folder with that name, **with every subfolder in it** (structure rule S1 makes the names match) | `domain: Acme` → folder `Acme` + its subfolder `Clients` |

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
| Untriaged (no project) | Only from the domain's **workflow** project (`type: workflow`) | That project files them, into its own domain only |

Board rules still hold on every board: a locked Spec changes only through `Spec change needed:` or
`spec reconcile` (`references/dev.md`), deletes are confirmed (`references/board.md` → Safety).

## 🔎 Resolving it

1. `list_projects` once. It returns every project with its folder and that folder's
   `parentFolderId`. **The domain's projects** = every project whose folder is the top-level folder
   named exactly `domain:`, or a child of it. No folder of that name → stop and say so; never guess
   the nearest match.
2. **The home board** = the `board:` name. It must be one of the domain's projects; a home board
   outside its domain folder → stop and say so (bandit:audit S4).
3. Keep both sets for the turn. 🔴 **No hardcoded IDs, ever**: a stored ID is a stale ID.

## 🧹 Filtering the household-wide views

`get_execution_board`, `get_week_board`, `get_inbox_board`, `get_workload` and `list_tasks` without
a `projectId` return **every project in the household**. Before a result is shown, counted or used:

- **Keep** the domain's cards; **drop** the rest, then re-count. Report the home board first, then
  the rest of the domain grouped by board
- **Keep** a card outside the domain only when it blocks, or is blocked by, a kept card: title,
  board and state, marked `outside the domain`
- **Untriaged** stays only for the workflow project; every other project drops the column
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
