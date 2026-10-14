# 🏗️ Load

**Command:** `/bandit:tasks load`
**Owns:** turning a WBS into a Deliverable project — the project, its columns, tasks, subtasks and dependencies. **The only surface that creates projects and columns.**

---

## 🎯 The rule of load

**Build exactly what the WBS says. Nothing more.**

The WBS is the design; load only transcribes it. No dates, no tags, no priorities, no extra columns, no lanes. Scheduling is `/bandit:tasks week`, sizing and tagging is triage. If the user wants a shape the WBS doesn't describe, stop: that's the design conversation, not a load.

---

## 📥 Input

A WBS in the **bandit:plan** format. That format is fixed on purpose: this surface consumes it.

| Source | How |
|---|---|
| Attached or pasted in the chat | Use it as given |
| The project's vault folder | `MyNotes/{domain}/Projects/{project}/{project}-wbs.md`, `domain` and `project` from the Project Context. Read it with the WebDAV tools |
| Neither | Ask for it. Not a WBS at all → say so and offer bandit:plan |

What load reads from it:

| WBS element | Recognised by |
|---|---|
| Project name | `## 🎯 WBS-0: {name}` |
| Deliverables (L2) | `#### WBS-X.Y: {name}` headings |
| Work packages (L3) | Rows of the `\| ID \| Work Package \| Dependencies \| Blocks \|` tables |
| Sub-steps (L4) | IDs `WBS-X.Y.Z.W` under a package |
| Description, Done when | The package's **WBS Dictionary** entry, when it has one |

---

## 🗺️ Scope

Read the `board:` line as usual (`references/scope.md`). Load's own behaviour per value:

| `board:` | Load does |
|---|---|
| `pending` | Creates a **new** project inside the domain's folder (a subfolder of it when the user names one) |
| `project "X"` | Loads into existing project X. Its `type` must be `deliverable`; otherwise stop and ask |
| `none` | Refuse. The project isn't board-backed |
| `folder "…"` · `global` | Retired: stop as `references/scope.md` says |

🛠️ **Dev projects are never loaded.** Project Context `dev: true` → stop and say cards are created
one work package at a time through `/bandit:tasks spec` (`references/dev-workflow.md`, B4).

After a load that created a project, say: *set `board: project "{name}"` through bandit:project.* Load never edits project instructions.

---

## 🧩 Mapping

| WBS | Bandit Brain |
|---|---|
| WBS-0 | Project, `type: deliverable`, named after the WBS |
| L2 deliverable | A column, named `X.Y {deliverable}`, in WBS order after the protected Backlog |
| L3 work package | A task in its deliverable's column. Title = package name. Description = the WBS ID, its phase (`WBS-X {phase}`), plus Description and Done when from the dictionary if present |
| L4 sub-step | A subtask of its package, in order |
| Depends on | `dependencies.blockedBy` on create |
| L1 phase | Not a column. It lives in each task's description |

**Small WBS (no L3):** L1 phases become columns and L2 deliverables become tasks. Say so in the plan.

---

## ⚙️ Procedure

1. **Resolve scope.** `list_projects` once: target folder or project, its columns and type.
2. **Parse the WBS** into packages: ID, name, column, subtasks, blockers.
3. **Validate before any write:** every dependency ID exists in the WBS · no cycles · no task above **30** links (both directions together). A failure → report it and stop; the WBS needs fixing in bandit:plan.
4. **Match what already exists** (resume or load into an existing project): columns by exact name, tasks by exact title within that project (`list_tasks(projectId)`). Existing ones are reused, never duplicated or changed.
5. ✋ **Show the plan and wait:** project (new / existing), columns (new · existing), tasks (new · existing), dependency links. Counts first, then the column list.
6. **Create** on confirmation:
   - `create_project` if new, then `add_project_column` per missing column, in WBS order.
   - Tasks in **dependency order** — blockers before the tasks they block. Each `create_task` carries `projectId`, `projectColumnId`, `description`, `subtasks` and `dependencies.blockedBy` (the task ids already created or matched). Keep the WBS-ID → task-id map in this session only; never write it anywhere.
7. **A refused create** leaves nothing behind. Record the reason, skip every task that depends on it, carry on with the rest.
8. **Report:** created · reused · refused (task name + reason) · skipped because a blocker was refused. Then the `board:` reminder when it applies.

---

## 🚫 Never

- Set due dates, tags, priority, effort or complexity. That's `/bandit:tasks week` and triage
- Set `origin`. The user asked for this load; it isn't another system
- Add lanes, rename columns or touch the protected Backlog
- Delete or rewrite anything that already exists — a mismatch is reported, not fixed
- Store task or project ids outside the session
