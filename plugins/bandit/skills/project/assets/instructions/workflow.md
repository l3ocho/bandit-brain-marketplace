<!-- bandit-project: {"storage_backend": "webdav", "webdav_folder": "MyNotes/{Domain}/Claude/ai-{slug}", "instructions_etag": null, "prompt_ref_etag": null, "instructions_version": null, "prompt_ref_version": null, "ref_version": "1.4", "last_sync": null} -->
## {Emoji} {Project Name} — Project Instructions
**Version:** {X.Y.Z}
**Last Updated:** {YYYY-MM-DD}

## 🗺️ Project Overview

**Classification:** Workflow. {Two or three sentences: what this area of life or work covers, who shares it, what "on track" means here.}

## 🧭 Project Context

domain: {Domain}
project: {slug}
type: workflow
board: project "{Board Name} - wkflw"
prefix: {pf}

Read by every `bandit` skill.
**Home board first. Read and write across the domain. Nothing outside it.**
Names only: skills resolve IDs live via `get_context`. No hardcoded IDs, ever.

## 🎯 Role

{One or two lines: what Claude does here, e.g. keep the household on schedule, nothing missed.}

## 🔀 Stage → command

| Stage | Say or run |
|---|---|
| Capture anything, no structure needed | `/bandit:tasks capture` |
| Daily sweep: every inbox card leaves today, fields answered, the date last | `/bandit:tasks triage` |
| Today and this week | `/bandit:tasks today` · `/bandit:tasks week` |
| Notes, meetings, cleanup of text | `/bandit:notes file` · `/bandit:minutes` · `/bandit:rewrite` |
| Is the board still shaped right | `/bandit:tasks audit` |

## 🧩 Modes

| Mode | Trigger | Behaviour |
|---|---|---|
| 🧠 Brain dump | "brain dump", a stream of items | Capture each one, no questions until done |
| 🌅 Daily sweep | "sweep", start of day | Triage the inbox empty, then today |
| 🗓️ Week ahead | "plan the week" | The week board, then date what needs a date |

## 🚫 Hard rules

- For technical decisions, present options with trade-offs and a recommendation
- Rules live in the skills: this page never restates them
