---
name: "minutes"
description: "Turns a meeting audio or video recording into professional minutes (a two-column Subject Item / Summary table, full and/or short), saved by default as two minutes notes through bandit:notes. Use when a recording comes with a request for minutes, action items or decisions."
---

# 🎙️ Minutes

Turns a meeting recording into professional, human-sounding minutes in markdown. Note conventions
are bandit:notes' (conventions §4 names, §5 fields, §12 body), and so is every write, whichever
storage holds the domain's notes: this skill adds only what is specific to minutes.

## 🧭 Router

`/bandit:minutes`, with the recording attached. One flow:

| Step | Does | Reference |
|---|---|---|
| Setup | Resolve the domain, ask version (full, short, both), location and meeting type in one question set | `references/workflow.md` |
| Transcribe | Prepare the audio, transcribe in the background, optional speaker separation | `references/workflow.md` · `references/scripts.md` |
| Write | Read the whole transcript, write the chosen versions | `references/formats.md` |
| Verify and save | Re-check every number, date, name, owner; scrub customer data; save | `references/workflow.md` · `references/notes.md` |

## ⛔ Hard limits (verified, don't re-test)

- **Connectors can't carry audio**: a file-storage connector returns empty content for a large
  file (5 MB on the one tested), and the Google Drive connector caps at 10 MB. So the audio comes
  in as a chat attachment, or as a file in the folder Claude Code runs from
- Workspace: 2 CPU cores, no GPU. Transcription ~0.27× real time; diarization ~0.3× and unreliable
  on single-mic room recordings

## 🔒 Hard rules

1. **Ask the setup questions once, before processing**; with nobody to answer: both versions, saved
   as notes when the domain is known, the meeting type inferred and said at the top
2. **Meeting types are exactly three:** supervisors, department, project (bandit:notes conventions §5)
3. **Verify before saving:** every figure against the transcript; shaky items marked *(to confirm)*
4. **No customer data, ever,** even when spoken: describe the case or use a placeholder
5. **Notes are written through bandit:notes:** two drafts that wait for review, then filed (`references/notes.md`)

## ⚠️ Gotchas

None logged yet.

## 🚫 Never

- Put customer data in the minutes (names, account numbers, addresses, call contents)
- Attribute statements from speaker labels on a single-mic room recording
- Invent attendees, owners or deadlines, or a meeting type beyond the three
- Replace an existing note or file without asking
- Create a meetings place, or file minutes from a regular project's scope
- Clean up a text transcript or notes (bandit:rewrite), or file existing notes (bandit:notes)
