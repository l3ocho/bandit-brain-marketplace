# 🗺️ Scope — resolve before every write

Read the `board:` line of the `## 🧭 Project Context` section — in the Claude.ai project
instructions, or in the repo's `CLAUDE.md` on Claude Code. The block's format is owned by
bandit:project.

```
board: project "Household"
board: folder "Bandit Labs"
board: global
board: none
board: pending
```

| `board:` | Behaviour |
|---|---|
| `project` / `folder` / `global` | Call `list_projects` to resolve that **name** to an ID, then read anywhere, write inside it |
| `none` | Not board-backed. Read anywhere, **write nothing**. Say the project has no board |
| `pending` | The board isn't designed yet. Read anywhere, **write nothing** — except `/bandit:tasks load`, which *is* the design step for a WBS-backed project, and `/bandit:tasks onboard`, which sets the scope. Otherwise say: design the board, then update the `board:` line |
| Neither a Project Context nor a legacy scope section (a plain chat, no project) | Unchanged: behave as before this section existed |

**Legacy fallback:** no Project Context but a `## 🗺️ Task Board Scope` section with a
`scope: …` line → read that line exactly as if it were the `board:` line.

🔴 **No hardcoded IDs, ever.** `list_projects` returns every folder, project and column with IDs
in one call — that *is* the scope table. Discovery is correct here. A stored ID is a stale ID.

**Read anywhere. Write inside declared scope only.** Asymmetric on purpose: planning needs
cross-board reads, but work from one project must never land on another's board.

If the declared name no longer resolves, **stop and say so.** Never guess at the nearest match.
