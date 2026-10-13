# 🗃️ Saving to the vault

> Read when the files go to a MyNotes domain: filenames, frontmatter, write then file.


Applies when Q2 resolved to a MyNotes domain.

**Filenames:** the minutes pattern and the uniqueness check in `bandit:notes` §4. The date in the
name is the **meeting date**, and the full and short versions are written as a pair.

**Frontmatter** goes above the `# … Minutes` title of both versions. The keys, their order and
the YAML style are `bandit:notes` §5; this is the filled shape for minutes (keys that don't
apply are left out). `bandit:notes home` reads it to list the minutes on the domain home page:

```yaml
---
type: minutes
status: triaged
domain: {Domain}
project: "[[{slug}]]"      # project meetings only — links the project hub note
summary: {one sentence, ≤ 25 words: the meeting and its main decisions}
created: {today}
updated: {today}
meeting: {supervisors | department | project}
meeting-date: {YYYY-MM-DD}
participants:
  - {name mentioned in discussion}
  - {…}
room: {where it was held}  # only if stated
source: meeting
related:
  - "[[{the other version's filename}]]"   # full ↔ short link each other
file-to: Meetings/
tags:
  - doc-minutes
---
```

- `summary` is **required**: the domain home page lists it next to the link, and it's what an
  agent reads to decide whether to open the minutes. The short version uses the same sentence.
- `meeting` is lowercase in the key, whatever the picker says.
- Both versions link each other in `related` (and in a `## Related` line, see the formats), so
  neither is an orphan. With only one version, leave `related` out unless the meeting links a
  project hub.
- Don't add keys `bandit:notes` §5 doesn't define.

**Write, then file:**
1. Write both files to `MyNotes/{Domain}/_inbox/` as new files (`if_match` omitted). New notes
   always land in the inbox first; that's the vault rule.
2. **Workflow project or no project metadata** (the `bandit:notes` domain scope): ask once "File them
   to `Meetings/` now?" On yes, for each file: remove `file-to` in place (read → bare-hex
   `if_match` → write), then move with `nc_webdav_move_resource(overwrite=false)` to
   `MyNotes/{Domain}/Meetings/{same name}`. On no, or with nobody there to answer, leave them in
   `_inbox` with `file-to` so `/bandit:notes file` can finish the job later.
   **Regular project** (the `bandit:notes` project scope, which can't write to `Meetings/`): don't
   offer the move. Leave both files in `_inbox` with `file-to: Meetings/` and say the workflow
   project will file them. Default the meeting type to `project` with
   `project: "[[{project}]]"` (the Project Context slug) unless the transcript clearly says otherwise.
3. A 412 on the move means that name already exists in `Meetings/`: stop and report. Don't
   overwrite, and don't rename on your own.

If the domain has no `Meetings/` folder, don't create one. Leave the files in `_inbox` and say
that the `meetings` module isn't set up in this domain (`/bandit:notes onboard` handles it).
