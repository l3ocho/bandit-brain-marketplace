# 🧱 Homes, writes and owners

> Read before the first write of a step: where each record lives, how writes are made, and which skill owns what.

## 🧱 Homes and writes

| Record | Home |
|---|---|
| Sprint card | The project's `PM` column, title "Sprint {Name}", tag-free; blockers are the batch |
| Sprint folder | `Projects/{slug}/sprint-{name}/` in the domain vault |
| Plan, briefs, execution prompt, ledger, handover report | The sprint folder; filenames in `references/templates.md` |
| Sprint tag | `sprint/{name}` on the batch cards |

The sprint folder and its record types are owned by bandit:notes (conventions §1, Sprint folders, and §4 filenames). This skill follows them and restates none of them; `references/templates.md` mirrors the filenames only for convenience.

**Leftovers.** A document used only to make another one (an inbox brief or spec draft once its card and filed brief exist, a WBS draft once the WBS is filed, a feedback note once applied, a brief whose card was deleted) is archived to `_archive/` with the bandit:notes stamps, or deleted on Leo's word, in the same step that consumed it. Nothing consumed stays in `_inbox/` or at a project root. **Only on proof**: the successor exists and was read (the filed brief, the filed WBS, the applied change). A note is never archived because it looks done or because its card is missing; if unsure, it stays.

**Writes.** New notes fail closed; edits read first and carry the etag; never force. A card description is read with `get_task` immediately before it is written, and a Spec change is shown old and new and applied only on Leo's yes (bandit:tasks `references/dev.md`, Spec lock). Tags are read and merged before `set_task_tags`. Board writes touch only the batch cards and the sprint card. Nothing is stored inside this skill's folder.

---

## 🧩 Owners

| Need | Read it in |
|---|---|
| Lanes, stages, card sections, Spec lock, boundaries, `stage`, `spec` | bandit:tasks `references/dev.md` |
| Tags, handler and energy tags, five hard rules | bandit:tasks `SKILL.md` |
| Vault folders, filenames, frontmatter, etag writes, inbox rules | bandit:notes `SKILL.md` and `references/conventions.md` |
| Project Context keys | bandit:project |
