# 🧱 Homes, writes and owners

> Read before the first write of a step: where each record lives, how writes are made, and which skill owns what.

## 🧱 Homes and writes

| Record | Home |
|---|---|
| The sprint | A real sprint on the home board: status and the batch in run order (`references/templates.md` → The sprint in the app) |
| Plan, briefs, execution prompt, wave notes, ledger (planning steps and wave progress), review record, wave report, handover report | The sprint's papers: notes on the project's board with the tag `sprint-{name}`, through bandit:notes. Titles and kinds in `references/templates.md` → Papers |
| What a card delivered | Its Delivered comment, one comment on the card written at its delivery (`references/templates.md` → Delivered comment); every paper names the card instead of retelling it |
| The project's targets note | A note in the project's place for planning documents (`references/templates.md` → Papers, Sprint targets) |
| The project's sprint data file (not text, so not a note) | A data file in `.sprint/` at the root of the repository the helper runs from (`references/templates.md` → Papers, Sprint data) |
| The project's notes file (what the sprint scripts read) | `.sprint/{project}-sprint-notes.json` at the root of the repository the helper runs from, rebuilt whole before each run of the scripts (`references/templates.md` → Notes file) |
| The sprint's papers link | Text naming where the papers are (`references/templates.md` → The sprint in the app) |

A sprint's records, their kinds and their places in each storage are owned by bandit:notes (conventions §13 and §4, `references/storage-app.md`). This skill follows them and restates none of them; `references/templates.md` mirrors the titles and kinds only for convenience.

**Leftovers.** A document used only to make another one (an inbox brief or spec draft once its card and filed brief exist, a WBS draft once the WBS is filed, a feedback note once applied, a brief whose card was deleted) is archived through bandit:notes (status `archived`), or deleted on the user's word, in the same step that consumed it. Nothing consumed stays in the Inbox or at a project root. **Only on proof**: the successor exists and was read (the filed brief, the filed WBS, the applied change). A note is never archived because it looks done or because its card is missing; if unsure, it stays.

**Writes.** Every paper is written through bandit:notes, which writes it safely in the project's storage (`references/write-safety.md` there): a new paper only after its look for a note of that title (create without a duplicate), an edit only right after reading the paper, one section at a time. The app takes no version on a write, so the read right before is the guard. A card description is read with `get_task` immediately before it is written, and a Spec change is shown old and new and applied only on the user's yes (bandit:tasks `references/dev.md`, Spec lock). Tags are read and merged before `update_tasks` with `tagIds` (it replaces the whole set). Board writes touch only the batch cards, the debug card and this sprint. Nothing is stored inside this skill's folder.

---

## 🧩 Owners

| Need | Read it in |
|---|---|
| Lanes, stages, card sections, Spec lock, boundaries, `stage`, `spec` | bandit:tasks `references/dev.md` |
| Tags, handler and energy tags, five hard rules | bandit:tasks `SKILL.md` |
| Creating a tag (the app's roles decide, no ban) | bandit:tasks `references/board.md` → Creating a tag |
| Note kinds, fields, places, storage, safe writes, inbox rules | bandit:notes `SKILL.md`, `references/conventions.md` and its storage references |
| Project Context keys | bandit:project |
| The project's rules, technical specs and guides for Claude | The project itself: its `CLAUDE.md`, its `.claude` folder (hooks, settings, agents) and its docs. The helpers read them and never copy or set them |
