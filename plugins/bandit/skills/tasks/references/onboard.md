# 🚀 Onboard — the board step of project onboarding

**Command:** `/bandit:tasks onboard`

**Run by bandit:project.** Onboarding is one command, owned by bandit:project: it interviews,
then loads this file for the board rows and bandit:notes for the vault rows, and puts all of
them in **one** proposal. This file only produces rows and executes the approved ones. It never
shows its own proposal or asks for its own approval when bandit:project runs it.

Run on its own (`/bandit:tasks onboard` typed directly), it produces the same rows as its own
proposal, then tells the user the `board:` line to set through bandit:project.

---

## Inputs (from bandit:project)

| Input | Example |
|---|---|
| Project name (as the board should show it) | `Bandit Labs` |
| Board answer from the interview | existing board · new board · none · decide later |
| Board type for a new board | `deliverable` · `workflow` · `hybrid` |
| Domain (the Project Context `domain:`) | `Acme` |
| `dev: true` (optional) | only for a technical development project |

---

## Procedure

1. **`get_context` once.** Its `folders` and `boards` give every folder, board, column and lane with IDs. Match
   names exactly; never guess the nearest one.
2. **Produce the rows:**

   | Board answer | Row | `board:` line |
   |---|---|---|
   | Existing board, found | none: nothing to create | `project "{name}"` |
   | New board | `create board` · name · type · inside the domain's folder (a subfolder of it when the user names one) | `project "{name}"` |
   | None | none | `none` |
   | Decide later | none | `pending` |
   | A name that doesn't resolve | none: stop and report it; bandit:project asks again | — |
   | An existing board outside the domain's folder | none: stop and report it (`references/scope.md`); offer a move row only when the user asks | — |

   A new board whose name matches an existing board is not created twice: report it and
   offer to use the existing one.

   **`dev: true`:** add the rows of the **dev board shape** procedure (`references/dev.md`) for the
   board, new or existing, to the same list: missing `lane/*` / `stage/*` tags, then its lanes,
   then the `PM` column when the board has none.
   It needs one board: with a `none` or `pending` answer, report that and add no dev rows.

   **A new board's name follows the structure rulebook**, S2 and S3 in
   bandit:audit `references/structure-rulebook.md`: read it before proposing the row. A name that breaks
   it is reported with the rule number and a compliant name, never created as given.
3. **Hand the rows and the `board:` line back** to bandit:project.
4. **Execute only an approved row:** `manage_boards { action: "create", name, type, folderId }`, the folder ID resolved
   live from step 1. The board starts with the protected Backlog column and nothing else. Dev
   board shape rows run after it, as `references/dev.md` says.
5. **Report per row:** created (with the name as the board shows it) or refused (with the reason).

---

## 🚫 Never

- Add columns, lanes, tasks or tags. The board's shape comes later: `/bandit:tasks load` from a
  WBS, or the design conversation. **Exception:** the dev board shape rows (tags, lanes and the
  `PM` column) for a `dev: true` project
- Create a folder on the board. If the domain's folder doesn't exist, report it (structure rule
  S1) and stop: a board outside its domain falls outside every domain's sight
- Store or show an ID in the `board:` line. Names only
- Create anything that isn't an approved row
