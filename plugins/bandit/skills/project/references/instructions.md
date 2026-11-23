# 🧾 Instructions from the one-page templates

> Read for `/bandit:project instructions`, and whenever `onboard` or `audit` writes a new instructions version: the instructions are generated from the template for the project's type, never written freehand.

## 🗂️ The templates

`assets/instructions/` in this skill (the marketplace repo keeps the same files in `templates/instructions/`):

| Project | Template |
|---|---|
| `type: workflow` | `workflow.md` |
| `type: product_service` (or `claude_marketplace`) without `dev: true` | `product_service.md` |
| any type with `dev: true` | `dev.md` (keep the project's own `type:` value in its Project Context) |

Each is one page: the header, the overview, the **Project Context**, a **stage → command** map and the
**modes**, plus the two default rules. The pipeline stages are `docs/pipeline.md` in the marketplace
repo; skill rules are never restated here.

## ⚙️ Procedure

1. **Pick the template** by the table. Read the current instructions (this chat's own:
   `references/surfaces.md`).
2. **Fill it:** `{Project Name}`, `{Emoji}`, the overview sentences, the Project Context values (from
   the current block, `references/project-context.md`; the template's `{notes: none …}` line becomes
   `notes: none` when the helpers keep no notes for the project and is removed otherwise) and the
   role line. `**Version:**` is the next major of the current one.
3. **Carry over what the project needs and the template lacks** (a project-specific hard rule, a mode
   the project uses) as rows in the matching table: at most a few lines. Anything longer belongs in the
   reference doc, not here.
4. **Length gate:** count the words; the result stays within one page and
   the tier's budget (`references/reference-template.md`).
5. **One proposal:** the new version as a row (with a fix row for anything dropped from the old
   version, recommended: move it to the reference doc). Nothing is written before the user's answer.
6. **Deliver** as the surface says (`references/output.md`): the approved row writes `CLAUDE.md`
   in Claude Code; on Claude.ai the full text is handed over to paste. Then `/bandit:audit check`
   in that project.

## 🚫 Never

- Write instructions freehand when a template fits, or restate a skill's rules in them
- Give the `dev` template to a project that does not run in Claude Code: sprints run there
