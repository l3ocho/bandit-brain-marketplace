# 🧭 The vault model, domain and scope

> Read before any command: what a domain is, how this project's scope is resolved, and why the inbox is Leo's.

## 🧭 Model in one screen

```
MyNotes/                         ← BanditCloud root of all domains
├── _{name}/                     ← any root "_" folder: NOT a domain, ignored by every scan
├── .templates/                  ← any dot folder: ignored
└── {Domain}/                    ← one domain = one Obsidian vault (has its own .obsidian/)
    ├── README.md                ← generated home page; frontmatter = domain config
    ├── _inbox/                  ← Leo's working space: no rules, no edits until he asks for review
    ├── _templates/              ← input structures
    ├── _archive/                ← done notes and old settings versions, original path mirrored
    ├── _attachments/            ← every image, PDF, audio file embedded by a note
    ├── Claude/                  ← SETTINGS ONLY (instructions + reference doc; no logs/notes/journals): {ai|code|design}-{slug}/
    ├── Projects/{slug}/         ← hub note {slug}.md; the rest of the layout belongs to the project
    ├── Meetings/                ← module
    └── Requests/                ← module
```

- **Domain** = a top-level folder of `MyNotes` whose name doesn't start with `_` or `.`.
- **`_` at root** means "not a domain". **`_` inside a domain** means "system folder this skill
  knows by name". Same prefix, different level — never confuse the two.
- **Each domain is its own Obsidian vault.** Wikilinks resolve inside the domain only, so never
  link across domains with `[[…]]`.

---

## 📍 Resolve the domain before anything else

1. **Project Context first.** Read the `## 🧭 Project Context` section: in the Claude.ai
   project instructions, or in the repo's `CLAUDE.md` on Claude Code. `domain:` names the
   domain and `project:` the project slug. The block's format is owned by bandit:project.
   - `domain: none` → this project has no vault. Say so and stop.
   - **Legacy fallback:** no Project Context section → read `vault_domain` and `vault_project`
     from the line-1 metadata comment (any label: bandit:project `references/reference-template.md` → Marker) instead.
2. **Run by bandit:project (onboarding).** The project's instructions aren't pasted yet, so take
   `domain`, `project` and `type` from bandit:project instead. See *Onboarding* below.
3. **Explicit argument.** `/bandit:notes home Acme` — the scheduled home refresh always passes it.
4. **Otherwise ask**, listing the live domains from `nc_webdav_list_directory("MyNotes")`.

Never guess the nearest match. If the named domain isn't in the listing, stop and say so.

---

## 🎯 Scope — what this project may see and change

**One project, one slug.** `project:` is the project's own name as a slug (`home-reno`), not
the Claude.ai project's display name. The same slug names every folder of that project:

```
Projects/home-reno/        ← the shared docs: one source, one set of rules, for both surfaces
Claude/ai-home-reno/       ← Claude.ai settings (higher-level implementation discussion)
Claude/code-home-reno/     ← Claude Code settings: the repo mirror (CLAUDE.md + claude/)
```

The Claude Code side reaches `Projects/{slug}/` through the same `## 🧭 Project Context` section,
placed in the repo's `CLAUDE.md`: with it, `/bandit:notes` gets the same project scope in Claude Code
as in Claude.ai. That file is configured in the repo, not by this skill.

**Scope comes from the Project Context `type:`** (legacy fallback: `project_type` in the
metadata), resolved together with the domain:

| Situation | Scope |
|---|---|
| `type: workflow` (e.g. Acme Workflow) | **Domain**: the whole domain. Oversees every project, and like every project has its own `Claude/ai-{slug}/` and `Projects/{slug}/` with its hub note |
| `type: product_service` or `type: claude_marketplace`, with `project:` | **Project**: the table below |
| No Project Context and no project metadata (e.g. the scheduled `/bandit:notes home Acme`) | **Domain** |

**Project scope:**

| Area | Read | Change (on approval) |
|---|---|---|
| `_inbox/` | All of it (Leo's inputs) | Create new notes; review (`file`) notes **only** into `Projects/{slug}/`, and only the ones Leo puts up for review |
| `Projects/{slug}/` | ✓ | ✓ |
| `Claude/ai-{slug}/`, `Claude/code-{slug}/` | ✓ | Create the folder only; the twin belongs to bandit:project, the mirror to the repo's Stop hook |
| `_templates/` | ✓ | ✓ Edit templates directly, no need to switch to the workflow project |
| `_archive/Projects/{slug}/` | ✓ | Archive and restore its own notes |
| `Meetings/`, `Requests/` | Only notes with `project: "[[{slug}]]"` | ✗ read-only |
| Missing core structure of the domain | ✓ | **Onboarding only:** create the missing core folders, `_templates/new-note.md` and the README, as approved rows |
| Everything else | ✗ | ✗ |

Anything outside the scope (another project's folder, a domain-level rename, `init`, `home`,
`settings`) that Leo asks for: stop and say it's a domain-level action to run from the workflow
project. Never widen scope on your own. Two exceptions: onboarding's approved rows may create the
domain's missing core structure (and `home` then builds the README), and a **`domain` fix row**
(below) runs when Leo approves that row by number. His yes is the widening, for that row only.

---

## 📥 The inbox is Leo's

`_inbox/` is where Leo writes, pastes and thinks. **While a note is in `_inbox/`, no convention
applies to it** — any filename, any frontmatter or none, any structure, any date format. And **no
skill or chat edits, renames, reformats or moves a note there** unless Leo puts that note up for
review in the current conversation. Not `lint`, not `onboard`, not another skill tidying up, not
a chat that is using the note as input. Reading is always fine. Leo's yes to a row that archives
or deletes a consumed draft by name (*Other skills* → Leftovers) is putting that note up.

**Exception: a skill-written draft, changed on Leo's request.** A note in `_inbox/` with
`status: triaged` that was written by a skill **in the current conversation** may be edited in
place when Leo explicitly asks for that change. Conditions: etag-guarded write, `updated` bumped,
`status` and `file-to` unchanged, and the change summarised back to him. Leo's own notes (`inbox`
or no status) stay untouchable, and so does any skill-written note from an earlier conversation.

**The rules apply at review.** Review is `/bandit:notes file`: Leo runs it (for the whole inbox or for
named notes) when he wants a note processed. That is the only moment the conventions touch it,
and the note leaves the inbox in the same step. The status says which side of that line a note
is on:

| Status | Whose | Rules |
|---|---|---|
| `inbox` (or no status at all) | Leo's, in progress | None. Untouchable |
| `triaged` + `file-to`, in `_inbox/` | Written by a skill, waiting for Leo's review | The skill wrote it compliant; not edited again until review, except on Leo's explicit request in the conversation that wrote it (the exception above) |
| anything, outside `_inbox/` | Reviewed | All of Part 2 |

**Review is all or nothing per note.** Every question a note needs answered (which project,
which meeting type, what an ambiguous date means) is asked before its row is final. A row with
an open question is not executed, and **a note is never left half-edited in the inbox**: it is
either still exactly as Leo left it, or reviewed and in its home folder.

**Leo's words stay Leo's.** At review, the frontmatter is the skill's job. The body is not: any
body change (removing a duplicated block, rewriting a date, fixing structure) is its own row
showing before → after, and happens only if Leo approves that row.
