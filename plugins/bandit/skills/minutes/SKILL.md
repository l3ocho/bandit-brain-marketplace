---
name: "minutes"
description: "Turns a meeting audio or video recording into professional minutes (a two-column Subject Item / Summary table, full and/or short), saved by default to the MyNotes vault inbox and filed to Meetings/. Use when a recording comes with a request for minutes, action items or decisions."
---

# 🎙️ Minutes

Turns a meeting recording into professional, human-sounding minutes in markdown. Vault conventions
are bandit:notes' (conventions §4 filenames, §5 frontmatter, §12 body): this skill adds only what is
specific to minutes.

## 🧭 Router

`/bandit:minutes`, with the recording attached. One flow:

| Step | Does | Reference |
|---|---|---|
| Setup | Resolve the domain, ask version (full, short, both), location and meeting type in one question set | `references/workflow.md` |
| Transcribe | Prepare the audio, transcribe in the background, optional speaker separation | `references/workflow.md` · `references/scripts.md` |
| Write | Read the whole transcript, write the chosen versions | `references/formats.md` |
| Verify and save | Re-check every number, date, name, owner; scrub customer data; save | `references/workflow.md` · `references/vault.md` |

## ⛔ Hard limits (verified, don't re-test)

- **The BanditCloud MCP can't carry audio**: `nc_webdav_read_file` returns empty content over 5 MB
  (hard-coded in the server); downloads over 100 MB fail. **The Google Drive MCP** caps at 10 MB.
  So the audio comes in as a chat attachment; BanditCloud finds the folder and takes the result
- Workspace: 2 CPU cores, no GPU. Transcription ~0.27× real time; diarization ~0.3× and unreliable
  on single-mic room recordings

## 🔒 Hard rules

1. **Ask the setup questions once, before processing**; with nobody to answer: both versions, the
   vault when the domain is known, the meeting type inferred and said at the top
2. **Meeting types are exactly three:** supervisors, department, project (bandit:notes conventions §5)
3. **Verify before saving:** every figure against the transcript; shaky items marked *(to confirm)*
4. **No customer data, ever,** even when spoken: describe the case or use a placeholder
5. **Vault writes follow bandit:notes write safety:** new files in `_inbox/`, then filed (`references/vault.md`)

## ⚠️ Gotchas

None logged yet.

## 🚫 Never

- Put customer data in the minutes (names, account numbers, addresses, call contents)
- Attribute statements from speaker labels on a single-mic room recording
- Invent attendees, owners or deadlines, or a meeting type beyond the three
- Overwrite an existing file without asking, or pass `if_match: "*"`
- Create a `Meetings/` folder, or move minutes out of `_inbox` in a regular project's scope
- Clean up a text transcript or notes (bandit:rewrite), or file existing notes (bandit:notes)
