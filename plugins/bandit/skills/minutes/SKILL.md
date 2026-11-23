---
name: "minutes"
description: "Turns a meeting transcript, or a recording when there is none, into professional minutes (a two-column Subject Item / Summary table, full and/or short), saved as two minutes notes through bandit:notes. Use when a transcript or a recording comes with a request for minutes, action items or decisions."
---

# 🎙️ Minutes

Turns a meeting into professional, human-sounding minutes in markdown. **It starts from a
transcript.** A recording is transcribed where recordings are kept, by whatever does that there,
and the transcript is what reaches this skill; transcribing in the chat is the fallback for a
recording that has no transcript yet. Note conventions are bandit:notes' (conventions §4 names,
§5 fields, §12 body), and so is every write: this skill adds only what is specific to minutes.

## 🧭 Router

`/bandit:minutes [transcript]`. One flow, and it runs unattended (rule 1):

| Step | Does | Reference |
|---|---|---|
| Input | Find the transcript: named, attached, or waiting in the folder the project's instructions name. None, and a recording given → the fallback | `references/workflow.md` |
| Setup | Resolve the domain, ask version (full, short, both), location and meeting type in one question set | `references/workflow.md` |
| Transcribe (fallback only) | Prepare the audio, transcribe in the background, optional speaker separation | `references/workflow.md` · `references/scripts.md` |
| Write | Read the whole transcript, write the chosen versions | `references/formats.md` |
| Verify and save | Re-check every number, date, name, owner; scrub customer data; save | `references/workflow.md` · `references/notes.md` |

## ⛔ Hard limits (verified, don't re-test)

- **Connectors can't carry audio**: a file-storage connector returns empty content for a large
  file (5 MB on the one tested), and the Google Drive connector caps at 10 MB. A transcript is
  text and has no such limit
- The fallback is slow: on a 2-core workspace with no GPU, transcription runs at ~0.27× real time
  and diarization at ~0.3×, unreliable on single-mic room recordings. Say the expected time before
  starting it, and that a transcript made where the recording is kept avoids it

## 🔒 Hard rules

1. **Ask the setup questions once, before processing**; with nobody to answer (an unattended
   run started by a transcript's arrival): both versions, saved as notes when the domain is known,
   the meeting type inferred and said at the top. No question is ever a reason to stop such a run
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
