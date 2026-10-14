# 🔄 Workflow

> Read before processing a recording: the setup questions, transcription, verification and saving.

## 🔄 Workflow

1. **Get the audio.** If the user names a BanditCloud file, ask them to attach it to the chat as well (explain the 5 MB limit in one line). If it's already attached, continue.
2. **Resolve the vault domain** before asking anything: read `domain:` (and `project:`) from
   the `## 🧭 Project Context` section of the project instructions (or the repo's `CLAUDE.md`
   on Claude Code). Legacy fallback: `vault_domain` and `vault_project` in the
   line-1 metadata comment (any label: bandit:project `references/reference-template.md` → Marker). Neither, or `domain: none` → the domain is
   unknown and Q2 asks for it.
3. **Ask the setup questions** in a single `AskUserQuestion` call, before any processing:
   - **Q1 — "Which version of the minutes?"** (header: `Version`, single select)
     - `Both (Recommended)` — full minutes plus a short version at about a third the length. Two files.
     - `Full only` — every topic in detail, one row per subject with the whole discussion.
     - `Short only` — condensed rows, decisions and figures kept. One file.
   - **Q2 — "Where should the files be saved?"** (header: `Location`, single select)
     - `{Domain} vault (Recommended)` — written to `MyNotes/{Domain}/_inbox/`, then filed to
       `Meetings/` once confirmed (`references/vault.md`). With no known domain in the
       Project Context, offer one option per live domain instead (folders of `MyNotes` not starting
       with `_` or `.`).
     - `Same folder as the audio` — found with `nc_webdav_find_by_name` on the attachment's file name. One match: use it. Several: ask which.
     - `Another BanditCloud folder` — the user gives the path. Confirm it exists with `nc_webdav_list_directory` before writing; if it doesn't, offer to create it with `nc_webdav_create_directory`.
   - **Q3 — "Which meeting was this?"** (header: `Meeting`, single select) — only when saving
     to the vault. Skip it if the filename or the transcript's opening makes it unambiguous.
     - `Supervisors` — supervisors and analysts, one per internal department
     - `Department` — the longer one with the manager and director
     - `Project` — a project meeting; then ask which project (list `Projects/` in the domain) unless the Project Context `project:` or the audio name makes it clear
     These are the only three: they mirror the Source picker in the user's meeting template, which is
     the standard. **No Ad-hoc, no Outstanding, no "other" option — never add one.** If the
     meeting doesn't clearly fit, ask the user which of the three it is.
   - If `AskUserQuestion` is unavailable or the user isn't there to answer, default to **both versions** in the **vault** when the domain is known (otherwise the **same folder as the audio**), infer the meeting type from the transcript, and say so at the top of the work.
   - If the audio isn't in BanditCloud at all, the `Same folder as the audio` option has nothing to resolve to: drop it.
4. **Set up a task list** (transcribe → speakers, if used → write → save and verify).
5. **Prepare the audio:** `ffmpeg -i <in> -ac 1 -ar 16000 audio.wav`, then `ffprobe` for the duration. Tell the user the expected processing time (duration × ~0.2).
6. **Transcribe** with `transcribe.py` (`references/scripts.md`) in the background (`nohup ... &`), polling the log. Default model `small`, English. For non-English meetings, drop `language="en"`.
7. **Speaker separation: optional, off by default.**
   - Run it only if the user asks, or if the recording is a Teams/Zoom export or has clear, separate voices.
   - Uses `diarize.py` plus `merge.py` (`references/scripts.md`).
   - Room recordings with one mic produce many fragment clusters and mid-sentence speaker switches. In the Sept 17 test: 18 clusters, 3 real ones. When that happens, **do not attribute statements from the labels.**
   - **Names always come from context:** people addressing each other, "I'll take that", sign-offs. List them as "Names mentioned in discussion", not as confirmed attendees.
8. **Read the full transcript** before writing. It's usually 25–35k tokens for an hour, so read it in pages.
9. **Write the minutes** in the version(s) chosen in Q1 (`references/formats.md`). When both are wanted, write the full version first and condense from it, so the two can't disagree.
10. **Verify.** Re-check every number, date, name, decision and owner against the transcript. Downgrade anything shaky to *(to confirm)*. Remove anything the transcript doesn't support. With both versions, check the figures and dates match between them. Last pass: scan both versions for customer data (account numbers, customer names, addresses) and replace any with a description or placeholder.
11. **Save** with `nc_webdav_write_file` (`content_type: text/markdown`, no `if_match` for a new file) to the folder from Q2:
    - **Vault:** follow `references/vault.md`.
    - **Other folders:** Full `<audio-stem> - Minutes.md`, Short `<audio-stem> - Minutes (Short).md`.
    - If a file already exists, ask before overwriting (read it first for its etag, strip `W/` and quotes to bare hex, then write with that `if_match`). Confirm the returned size matches the local file.
12. **Report** in 2–3 lines: which versions were written and where, how many items and actions, anything marked *(to confirm)*. Send each .md with SendUserFile.

## 🧩 Edge cases

- **Audio arrives but no BanditCloud match:** save to the vault if the domain is known; otherwise ask for the folder. Don't guess.
- **Project meeting for a project with no `Projects/{slug}/` folder or hub note:** still use the slug the user gave (`project: "[[{slug}]]"` will resolve once the hub exists), and mention that the project folder or hub doesn't exist yet.
- **Target folder doesn't exist:** offer to create it rather than writing to a parent folder.
- **Output file already exists:** read it for its etag and ask before overwriting with `if_match`.
- **User asks later for the other version:** build it from the minutes file that already exists, not from the transcript again, and save it beside the first.
- **Very poor audio** (long garbled stretches): say so in the report, and consider re-running with the `medium` model, which takes about 3x longer.
- **Sensitive content** (legal matters, HR, individual performance): summarize at a business level only and leave out personal details.
