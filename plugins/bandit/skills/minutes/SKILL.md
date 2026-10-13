---
name: "minutes"
description: "Turn a meeting audio recording (attached, or located in BanditCloud) into professional minutes: a two-column Subject Item / Summary table in .md, in full and/or short form, saved to BanditCloud, by default into the MyNotes vault (domain _inbox, filed to Meetings/) following the bandit:notes conventions. Use whenever the user attaches or names a meeting recording (audio or video: m4a, mp3, wav, mp4…) and asks for minutes, meeting notes, a summary of the meeting, action items, or \"what did we decide\" — including supervisors, department and project meetings. Do NOT use for text transcripts or notes that only need cleaning up (bandit:rewrite), or for filing existing notes (bandit:notes)."
---

# 🎙️ Meeting Minutes from Audio

Turns a meeting recording into professional, human-sounding minutes (Markdown), saved to BanditCloud.

**Vault conventions are owned by `bandit:notes`.** Before writing into the vault, read its
`references/conventions.md`: §4 (filenames, including the minutes slugs), §5 (frontmatter keys,
YAML style, key order) and §12 (note body shape). **Saving to the vault** below adds only what's
specific to minutes; it never restates those rules.

## ⛔ Hard limits (verified, don't re-test)

- **BanditCloud MCP can't carry audio.** `nc_webdav_read_file` returns empty content for any file over **5 MB**. That limit is hard-coded as `RAW_CONTENT_MAX_BYTES` in cbcoutinho/nextcloud-mcp-server and no setting changes it. Downloads over 100 MB also fail on the transfer ceiling.
- **Google Drive MCP** caps downloads at **10 MB** and can't create public links.
- **So the audio comes in as a chat attachment** (`/mnt/user-data/uploads/<file>`). BanditCloud is used to find the target folder and to write the result.
- Workspace: 2 CPU cores, no GPU. Transcription runs at ~0.27x real time (78 min of audio took ~13 min). Speaker diarization runs at ~0.3x real time and is unreliable on single-mic room recordings.

## 🔄 Workflow

1. **Get the audio.** If the user names a BanditCloud file, ask them to attach it to the chat as well (explain the 5 MB limit in one line). If it's already attached, continue.
2. **Resolve the vault domain** before asking anything: read `domain:` (and `project:`) from
   the `## 🧭 Project Context` section of the project instructions (or the repo's `CLAUDE.md`
   on Claude Code). Legacy fallback: `vault_domain` and `vault_project` in the
   `<!-- bandit-project: {...} -->` metadata. Neither, or `domain: none` → the domain is
   unknown and Q2 asks for it.
3. **Ask the setup questions** in a single `AskUserQuestion` call, before any processing:
   - **Q1 — "Which version of the minutes?"** (header: `Version`, single select)
     - `Both (Recommended)` — full minutes plus a short version at about a third the length. Two files.
     - `Full only` — every topic in detail, one row per subject with the whole discussion.
     - `Short only` — condensed rows, decisions and figures kept. One file.
   - **Q2 — "Where should the files be saved?"** (header: `Location`, single select)
     - `{Domain} vault (Recommended)` — written to `MyNotes/{Domain}/_inbox/`, then filed to
       `Meetings/` once confirmed (see **Saving to the vault**). With no known domain in the
       Project Context, offer one option per live domain instead (folders of `MyNotes` not starting
       with `_` or `.`).
     - `Same folder as the audio` — found with `nc_webdav_find_by_name` on the attachment's file name. One match: use it. Several: ask which.
     - `Another BanditCloud folder` — the user gives the path. Confirm it exists with `nc_webdav_list_directory` before writing; if it doesn't, offer to create it with `nc_webdav_create_directory`.
   - **Q3 — "Which meeting was this?"** (header: `Meeting`, single select) — only when saving
     to the vault. Skip it if the filename or the transcript's opening makes it unambiguous.
     - `Supervisors` — supervisors and analysts, one per internal department
     - `Department` — the longer one with the manager and director
     - `Project` — a project meeting; then ask which project (list `Projects/` in the domain) unless the Project Context `project:` or the audio name makes it clear
     These are the only three: they mirror the Source picker in Leo's meeting template, which is
     the standard. **No Ad-hoc, no Outstanding, no "other" option — never add one.** If the
     meeting doesn't clearly fit, ask Leo which of the three it is.
   - If `AskUserQuestion` is unavailable or the user isn't there to answer, default to **both versions** in the **vault** when the domain is known (otherwise the **same folder as the audio**), infer the meeting type from the transcript, and say so at the top of the work.
   - If the audio isn't in BanditCloud at all, the `Same folder as the audio` option has nothing to resolve to: drop it.
4. **Set up a task list** (transcribe → speakers, if used → write → save and verify).
5. **Prepare the audio:** `ffmpeg -i <in> -ac 1 -ar 16000 audio.wav`, then `ffprobe` for the duration. Tell the user the expected processing time (duration × ~0.2).
6. **Transcribe** with `transcribe.py` (below) in the background (`nohup ... &`), polling the log. Default model `small`, English. For non-English meetings, drop `language="en"`.
7. **Speaker separation: optional, off by default.**
   - Run it only if the user asks, or if the recording is a Teams/Zoom export or has clear, separate voices.
   - Uses `diarize.py` plus `merge.py` (below).
   - Room recordings with one mic produce many fragment clusters and mid-sentence speaker switches. In the Sept 17 test: 18 clusters, 3 real ones. When that happens, **do not attribute statements from the labels.**
   - **Names always come from context:** people addressing each other, "I'll take that", sign-offs. List them as "Names mentioned in discussion", not as confirmed attendees.
8. **Read the full transcript** before writing. It's usually 25–35k tokens for an hour, so read it in pages.
9. **Write the minutes** in the version(s) chosen in Q1 (formats below). When both are wanted, write the full version first and condense from it, so the two can't disagree.
10. **Verify.** Re-check every number, date, name, decision and owner against the transcript. Downgrade anything shaky to *(to confirm)*. Remove anything the transcript doesn't support. With both versions, check the figures and dates match between them. Last pass: scan both versions for customer data (account numbers, customer names, addresses) and replace any with a description or placeholder.
11. **Save** with `nc_webdav_write_file` (`content_type: text/markdown`, no `if_match` for a new file) to the folder from Q2:
    - **Vault:** follow **Saving to the vault** below.
    - **Other folders:** Full `<audio-stem> - Minutes.md`, Short `<audio-stem> - Minutes (Short).md`.
    - If a file already exists, ask before overwriting (read it first for its etag, strip `W/` and quotes to bare hex, then write with that `if_match`). Confirm the returned size matches the local file.
12. **Report** in 2–3 lines: which versions were written and where, how many items and actions, anything marked *(to confirm)*. Send each .md with SendUserFile.

## 🗃️ Saving to the vault

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

## 📝 Minutes format — full

```
# <Meeting type> — Minutes

> <the frontmatter summary sentence>

| | |
|---|---|
| **Date** | <from filename or transcript> |
| **Duration** | <n> minutes |
| **Source** | `<audio file>` |
| **Names mentioned in discussion** | <comma list> |
| **Next checkpoint** | <if stated> |

> Prepared from an automated transcript ... Anything marked *(to confirm)* was unclear in the recording.

## Discussion

| Subject Item | Summary (Notes) |
|---|---|
| **1. <Topic>** | <prose summary> |

## Action Items

| # | Action | Owner | Due |

## Related

- [[<short-version filename>]] — condensed version
- [[<project slug>]] — project hub   (project meetings only)
```

The two-column Discussion table is the core deliverable. The header block and Action Items table are supporting sections.

## ✂️ Minutes format — short

Same subjects, same numbering, same action items, about a third of the words (roughly 600 words for a 78-minute meeting).

```
# <Meeting type> — Minutes (Short)

> <the frontmatter summary sentence>

**<Date> · <n> minutes · Source: `<audio file>`**
Next checkpoint: <if stated>

## Discussion

| Subject Item | Summary (Notes) |
|---|---|
| **1. <Topic>** | <1–3 sentences> |

## Action Items

| # | Action | Owner | Due |

## Related

- [[<full-version filename>]] — full minutes
- [[<project slug>]] — project hub   (project meetings only)
```

The `## Related` section appears only when writing to the vault; other folders don't use
wikilinks.

Condensing rules: keep every subject (never merge topics), every decision, and every figure, date, name and amount. Cut the background, the path the discussion took, and anything the decision already implies. Rows carrying several decisions (schedules, policy changes) stay longer than the rest — that's correct, not a failure to condense. The header block collapses to one line and the caveat note is dropped; keep the *(to confirm)* markers.

## ✍️ Writing rules (professional and human)

- Write like an experienced executive assistant, not an AI. Use plain, confident sentences, active voice and past or present tense. Avoid filler ("it was noted that", "a robust discussion") and inflated verbs.
- One row per real topic, in meeting order, with a numbered, specific subject ("Texas commercial cancellation fees", not "Fees").
- Each summary covers context → what was discussed → **Decision:** / **Going forward:** in bold where one was made. Keep the numbers, dates, amounts and IDs exactly as spoken — system, user and document IDs, never customer account numbers (see below).
- Leave out banter, jokes, personal chatter, profanity, private matters about individuals (e.g. someone's leave balance or personal life) and one-sided phone calls, except where the call produced an action.
- Don't invent attendees, owners or deadlines. If no owner was stated, write "Owner not stated".
- Fix obvious transcription errors only when the context makes them certain ("Leon Iyer" → "Leo and I", "Genesis" → "Genesys"). Otherwise mark them *(to confirm)*.
- Keep company and system names as used in the meeting.
- **No customer data, ever** — even when it's spoken in the meeting: no customer names, account
  numbers or references, addresses, phone numbers or call contents. Describe the case instead
  ("a PA residential account", "a customer whose name was stored with a typo") or use a
  placeholder (`[account]`, `[customer]`). Colleagues' names are fine. The verify step (10)
  re-checks for this.
- **Dates unambiguous:** written month ("October 1") or `YYYY-MM-DD`, never `10/01`.

## 🐍 Scripts

The three scripts live in this skill's `scripts/` folder. Copy them into the working directory
before running; don't run them in place (they'd leave cache files in the skill folder).

Install once per session: `pip install --break-system-packages -q faster-whisper sherpa-onnx soundfile`.

| Script | Run | Does |
|---|---|---|
| `scripts/transcribe.py` | `python transcribe.py audio.wav transcript.json [small\|medium]` | Timestamped segments (JSON). Afterwards write a readable `plain.txt` (`[mm:ss] text` per segment) for reading |
| `scripts/diarize.py` (optional) | `python diarize.py audio.wav turns.json [threshold] [num_speakers]` | Who spoke when. Pass the headcount as `num_speakers` if the user knows it — much better than auto. Always run in the background: it exceeds the 10-minute shell timeout on long recordings |
| `scripts/merge.py` (optional) | `python merge.py transcript.json turns.json labelled.txt` | Labels each segment with the speaker of max overlap, merges consecutive lines |

`transcribe.py` defaults to English (`language="en"`); for non-English meetings, edit that line
in your working copy.

Diarization models (only if step 7 runs) come from GitHub releases; the pyannote models on
Hugging Face need a login, so they aren't used. Download them into the working directory:
`diarize.py` expects `sherpa-onnx-pyannote-segmentation-3-0/model.onnx` and `emb_en.onnx` there.
- `https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-segmentation-models/sherpa-onnx-pyannote-segmentation-3-0.tar.bz2`
- `https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/wespeaker_en_voxceleb_resnet34_LM.onnx` (English embeddings, saved as `emb_en.onnx`; the zh-cn default is worse for English)

## 🧩 Edge cases

- **Audio arrives but no BanditCloud match:** save to the vault if the domain is known; otherwise ask for the folder. Don't guess.
- **Project meeting for a project with no `Projects/{slug}/` folder or hub note:** still use the slug the user gave (`project: "[[{slug}]]"` will resolve once the hub exists), and mention that the project folder or hub doesn't exist yet.
- **Target folder doesn't exist:** offer to create it rather than writing to a parent folder.
- **Output file already exists:** read it for its etag and ask before overwriting with `if_match`.
- **User asks later for the other version:** build it from the minutes file that already exists, not from the transcript again, and save it beside the first.
- **Very poor audio** (long garbled stretches): say so in the report, and consider re-running with the `medium` model, which takes about 3x longer.
- **Sensitive content** (legal matters, HR, individual performance): summarize at a business level only and leave out personal details.

## ⚠️ Gotchas

None logged yet.

## 🚫 Never

- Put customer data in the minutes (names, account numbers, addresses, call contents), even when spoken
- Attribute statements from speaker labels on a single-mic room recording
- Invent attendees, owners or deadlines, or a meeting type beyond supervisors · department · project
- Overwrite an existing file without asking, or pass `if_match: "*"`
- Create a `Meetings/` folder, or move minutes out of `_inbox` in a regular project's scope