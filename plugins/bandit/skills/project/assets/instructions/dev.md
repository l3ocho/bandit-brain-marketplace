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
{notes: none — this line only when the helpers keep no notes for this project}

Read by every `bandit` skill.
**Home board first. Read and write across the domain. Nothing outside it.**
Names only: skills resolve IDs live via `get_context`. No hardcoded IDs, ever.

## 🎯 Role

This project runs in Claude Code, from its repository: capture, clarify, triage and spec with the
core skills, then plan, build, test, release and close with `bandit-dev`.

## 🔀 Stage → command (the pipeline)

| # | Stage | Command |
|---|---|---|
| 1 | Capture an idea: the board is the idea list | `/bandit:tasks capture` |
| 2 | Clarify a fuzzy one | `/bandit:clarify` |
| 3 | Triage, then specify | `/bandit:tasks triage` → `/bandit:tasks spec` |
| 4–5 | Plan the sprint, independent review | `/bandit-dev:sprint plan` |
| 6 | Run the waves | `/bandit-dev:sprint run` |
| 7–8 | Test on staging (the owner), debug | `/bandit-dev:sprint debug` |
| 9–10 | Release, close | `/bandit-dev:sprint release` → `close` |

## 🧩 Modes

| Mode | Trigger | Behaviour |
|---|---|---|
| 🧠 Brain dump | "brain dump" | Capture verbatim, structure only when told done |
| 📝 Spec | "write the card" | `/bandit:tasks spec`, one card, its brief alongside |
| 🔭 Overview | "where are we" | Sprints and stages from the board, nothing written |

## 🚫 Hard rules

- For technical decisions, present options with trade-offs and a recommendation
- Rules live in the skills: this page never restates them
