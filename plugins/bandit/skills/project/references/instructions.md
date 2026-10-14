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

1. **Pick the template** by the table. Read the current instructions (this chat's own, or the vault
   production file for another project, `references/update.md`).
2. **Fill it:** `{Project Name}`, `{Emoji}`, the overview sentences, the Project Context values (from
   the current block, `references/project-context.md`), the role line, and the metadata line
   (`references/output.md`). `**Version:**` is the next major of the current one; `instructions_version`
   the next `v{N}` of the vault folder (`references/vault-storage.md`).
3. **Carry over what the project needs and the template lacks** (a project-specific hard rule, a mode
   the project uses) as rows in the matching table: at most a few lines. Anything longer belongs in the
   reference doc, not here.
4. **Length gate:** count the words without the metadata line; the result stays within one page and
   the tier's budget (`references/reference-template.md`).
5. **One proposal:** the new version file as a row (with a fix row for anything dropped from the old
   version, recommended: move it to the reference doc). Nothing is written before the user's answer.
6. **Hand over** the full text to paste into Claude.ai, then `/bandit:audit check` in that project.
   On a `dev: true` project, add the line: *the repo `CLAUDE.md` Project Context needs the same block.*

## 🚫 Never

- Write instructions freehand when a template fits, or restate a skill's rules in them
- Let the Claude.ai agent of a `dev: true` project plan, run or release a sprint: it stops at spec
