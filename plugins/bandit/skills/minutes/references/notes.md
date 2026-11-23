# 🗃️ Saving the minutes as notes

> Read when the minutes are saved as notes: names, fields, write then file.


Applies when Q2 resolved to a domain's notes. Where a draft waits and every write step are
bandit:notes' (`references/other-skills.md` there → Who writes what).
This file says only what the minutes hold and when they are filed.

**Names:** the minutes naming rule in bandit:notes conventions §4: that name is the note's title. The date in the name is the **meeting date**, and the full and short
versions are written as a pair.

**Fields** (bandit:notes conventions §5; how the app holds them is bandit:notes'). Fields that
don't apply are left out. Both versions carry the same ones:

| Field | Value |
|---|---|
| Kind | `minutes` |
| Summary | **Required.** One sentence, ≤ 25 words: the meeting and its main decisions. The short version uses the same sentence |
| Meeting | `supervisors` · `department` · `project`, lowercase whatever the picker says |
| Meeting date | `YYYY-MM-DD` |
| Participants | The names mentioned in discussion |
| Room | Where it was held, only if stated |
| Project | Project meetings only: the project (its hub note) |
| Source | `meeting` |
| Related notes | The other version (full ↔ short), and the project hub on a project meeting |
| Tags | `doc-minutes` |

- `summary` is what a list shows next to the minutes, and what an agent reads to decide whether
  to open them.
- Both versions name each other in their related notes and in a `## Related` line (see the
  formats), so neither is an orphan. With only one version, it has related notes only when the
  meeting is a project's.
- There is no Source field, and minutes sit on the workflow board, so a
  project meeting names its project through the related hub note (bandit:notes'
  `references/storage-app.md` → Fields).
- Don't add fields bandit:notes conventions §5 doesn't define.

**Write, then file** (each write through bandit:notes):
1. **Look first.** bandit:notes looks for minutes of the same name before it creates any (its
   create without a duplicate). One found → show it and ask before replacing it; never write a
   second pair. Found minutes in the inbox that are not this conversation's own drafts are left
   alone and named (bandit:notes' inbox rule).
2. **Write both as drafts** that wait for review. Read each back and report its kind, summary and
   place.
3. **Workflow project or no project metadata** (the bandit:notes domain scope): ask once "File them
   to the domain's meetings place now?" On yes, bandit:notes files both, as rows of its `file` for
   these two notes only. On no, or with nobody there to answer, they wait for review and
   `/bandit:notes file` finishes the job later.
   **Regular project** (the bandit:notes project scope, which can't file into the meetings place):
   don't offer it. Both wait for review; say the workflow project will file them. Default the
   meeting type to `project` with the project set (the Project Context slug) unless the transcript
   clearly says otherwise.
4. Minutes of that name already in the meetings place when filing: stop and report. Don't replace
   them, and don't rename on your own.
5. **Too large.** The app refuses a note over 200 KB. Then propose a split by section: the
   Discussion table in two parts, the Action Items with the second, each part its own minutes note
   related to the others. Nothing is cut or saved shorter.

If the domain has no meetings place (bandit:notes says where it is), don't create one. Leave the
minutes waiting for review and say the domain has no workflow board to file them on yet.
