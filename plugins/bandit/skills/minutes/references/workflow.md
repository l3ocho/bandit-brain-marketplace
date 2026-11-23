# 🔄 Workflow

> Read before processing a meeting: finding the transcript, the setup questions, the fallback transcription, verification and saving.

## 🔄 Workflow

1. **Find the transcript.** In this order:
   - a transcript named in the command or attached: a text file of `[mm:ss] text` lines, with or
     without speaker labels, or the segments JSON `transcribe.py` writes (`references/scripts.md`)
   - with nothing named: the newest transcript waiting in the folder the project's instructions
     name for them (their `## 🖥️ Environment`). Several waiting → one run each, oldest first
   - none, and a recording was given (attached, or a file in the folder Claude Code runs from) →
     **the fallback**: steps 5 to 7 transcribe it here. Say first, in one line, how long that takes
     and that a transcript made where the recording is kept avoids it. A recording named by a
     cloud path: ask the user to attach it (`SKILL.md` → Hard limits)
   - neither → ask for the transcript, and stop

   The meeting date comes from the transcript's file name when it carries one (`YYYY-MM-DD`),
   otherwise from what is said in it, otherwise it is asked (unattended: the file's date, marked
   *(to confirm)*).
2. **Resolve the domain** before asking anything: read `domain:` (and `project:`) from
   the `## 🧭 Project Context` section of the project instructions (or the repo's `CLAUDE.md`
   on Claude Code). None, or `domain: none` → the domain is unknown and Q2 asks for it. `domain:`
   names the board folder of that name; where the minutes go is bandit:notes'
   (`references/other-skills.md` there → Who writes what), never this skill's. `notes: none` in
   the Project Context → no note is written: Q2 is skipped and the minutes are handed over in the
   chat.
3. **Ask the setup questions** in a single `AskUserQuestion` call, before any processing:
   - **Q1 — "Which version of the minutes?"** (header: `Version`, single select)
     - `Both (Recommended)` — full minutes plus a short version at about a third the length. Two files.
     - `Full only` — every topic in detail, one row per subject with the whole discussion.
     - `Short only` — condensed rows, decisions and figures kept. One file.
   - **Q2 — "Where should the files be saved?"** (header: `Location`, single select)
     - `{Domain} notes (Recommended)` — two minutes notes written through bandit:notes as drafts,
       then filed to the domain's meetings place once confirmed (`references/notes.md`). With no
       known domain in the Project Context, offer one option per live domain instead (the
       top-level board folders of `get_context`).
     - `In the chat only` — the files are handed over and nothing is saved.
   - **Q3 — "Which meeting was this?"** (header: `Meeting`, single select) — only when saving
     as notes. Skip it if the filename or the transcript's opening makes it unambiguous.
     - `Supervisors` — supervisors and analysts, one per internal department
     - `Department` — the longer one with the manager and director
     - `Project` — a project meeting; then ask which project (the domain's projects, as bandit:notes lists them) unless the Project Context `project:` or the audio name makes it clear
     These are the only three: they mirror the Source picker in the user's meeting template, which is
     the standard. **No Ad-hoc, no Outstanding, no "other" option — never add one.** If the
     meeting doesn't clearly fit, ask the user which of the three it is.
   - If `AskUserQuestion` is unavailable or the user isn't there to answer, default to **both versions** saved **as notes** when the domain is known (otherwise **in the chat only**), infer the meeting type from the transcript, and say so at the top of the work.
4. **Set up a task list** (the fallback's steps only when it runs: transcribe → speakers, if used; then write → save and verify).
5. **Fallback only. Prepare the audio:** `ffmpeg -i <in> -ac 1 -ar 16000 audio.wav`, then `ffprobe` for the duration. Tell the user the expected processing time (duration × ~0.2).
6. **Fallback only. Transcribe** with `transcribe.py` (`references/scripts.md`) in the background (`nohup ... &`), polling the log. Default model `small`, English. For non-English meetings, drop `language="en"`.
7. **Fallback only. Speaker separation: optional, off by default.** A transcript that arrives with speaker labels is read as it is, under the same two cautions below (labels from a single-mic room recording are not attribution; names come from context).
   - Run it only if the user asks, or if the recording is a Teams/Zoom export or has clear, separate voices.
   - Uses `diarize.py` plus `merge.py` (`references/scripts.md`).
   - Room recordings with one mic produce many fragment clusters and mid-sentence speaker switches. In the Sept 17 test: 18 clusters, 3 real ones. When that happens, **do not attribute statements from the labels.**
   - **Names always come from context:** people addressing each other, "I'll take that", sign-offs. List them as "Names mentioned in discussion", not as confirmed attendees.
8. **Read the full transcript** before writing. It's usually 25–35k tokens for an hour, so read it in pages.
9. **Write the minutes** in the version(s) chosen in Q1 (`references/formats.md`). When both are wanted, write the full version first and condense from it, so the two can't disagree.
10. **Verify.** Re-check every number, date, name, decision and owner against the transcript. Downgrade anything shaky to *(to confirm)*. Remove anything the transcript doesn't support. With both versions, check the figures and dates match between them. Last pass: scan both versions for customer data (account numbers, customer names, addresses) and replace any with a description or placeholder.
11. **Save** to the place from Q2:
    - **Notes:** follow `references/notes.md`. bandit:notes writes them.
    - **In the chat only:** nothing is written anywhere; the files of step 12 are the delivery.
12. **Report** in 2–3 lines: which versions were written and where, how many items and actions, anything marked *(to confirm)*. Send each .md with SendUserFile. A transcript taken from the waiting folder then moves into that folder's `done/`, so the next run does not pick it again; it is never deleted here.

## 🧩 Edge cases

- **Project meeting for a project with no hub note:** still name the project the user gave (the link resolves once the hub exists), and mention that the project's hub note doesn't exist yet.
- **The minutes already exist:** ask before replacing them (`references/notes.md`).
- **User asks later for the other version:** build it from the minutes that already exist, not from the transcript again, and save it as a note related to the first.
- **A poor transcript** (long garbled stretches): say so in the report and mark what it touches *(to confirm)*. In the fallback, consider re-running with the `medium` model, which takes about 3x longer; for a transcript made elsewhere, say that the recording could be transcribed again with a larger model there.
- **Sensitive content** (legal matters, HR, individual performance): summarize at a business level only and leave out personal details.
