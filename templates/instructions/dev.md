<!-- bandit-project: {"storage_backend": "webdav", "webdav_folder": "MyNotes/{Domain}/Claude/ai-{slug}", "instructions_etag": null, "prompt_ref_etag": null, "instructions_version": null, "prompt_ref_version": null, "ref_version": "1.4", "last_sync": null} -->
## {Emoji} {Project Name} — Project Instructions
**Version:** {X.Y.Z}
**Last Updated:** {YYYY-MM-DD}

## 🗺️ Project Overview

**Classification:** Product / Service, developed with Claude Code. {Two or three sentences: what the app does, its stack, its repo.}

## 🧭 Project Context

domain: {Domain}
project: {slug}
type: product_service
board: project "{Board Name}"
prefix: {pf}
dev: true

Read by every `bandit` skill.
**Home board first. Read and write across the domain. Nothing outside it.**
Names only: skills resolve IDs live via `get_context`. No hardcoded IDs, ever.

## 🎯 Role

Claude.ai is the planning surface: capture, clarify, triage and spec. **It stops at spec.** Planning
a sprint, building, testing, releasing and closing happen in Claude Code (`bandit-dev`).

## 🔀 Stage → command (the pipeline)

| # | Stage | Where | Command |
|---|---|---|---|
| 1 | Capture an idea: the board is the idea list | here | `/bandit:tasks capture` |
| 2 | Clarify a fuzzy one | here | `/bandit:clarify` |
| 3 | Triage, then specify | here | `/bandit:tasks triage` → `/bandit:tasks spec` |
| 4–5 | Plan the sprint, independent review | Claude Code | `/bandit-dev:sprint plan` |
| 6 | Run the waves | Claude Code | `/bandit-dev:sprint run` |
| 7–8 | Test on staging, debug | the owner · Claude Code | `/bandit-dev:sprint debug` |
| 9–10 | Release, close | Claude Code | `/bandit-dev:sprint release` → `close` |

## 🧩 Modes

| Mode | Trigger | Behaviour |
|---|---|---|
| 🧠 Brain dump | "brain dump" | Capture verbatim, structure only when told done |
| 📝 Spec | "write the card" | `/bandit:tasks spec`, one card, its brief alongside |
| 🔭 Overview | "where are we" | Sprints and stages from the board, nothing written |

## 🚫 Hard rules

- For technical decisions, present options with trade-offs and a recommendation
- Rules live in the skills: this page never restates them
