## {Emoji} {Project Name} — Project Instructions
**Version:** {X.Y.Z}
**Last Updated:** {YYYY-MM-DD}

## 🗺️ Project Overview

**Classification:** Product / Service. {Two or three sentences: what it delivers, for whom, and where it stands today.}

## 🧭 Project Context

domain: {Domain}
project: {slug}
type: product_service
board: project "{Board Name}"
prefix: {pf}
{notes: none — this line only when the helpers keep no notes for this project}

Read by every `bandit` skill.
**Home board first. Read and write across the domain. Nothing outside it.**
Names only: skills resolve IDs live via `get_context`. No hardcoded IDs, ever.

## 🎯 Role

{One or two lines: what Claude does here, and what stays the owner's call.}

## 🔀 Stage → command

| Stage | Say or run |
|---|---|
| 1 · Capture an idea | `/bandit:tasks capture`: parked in this project's inbox, the idea list |
| 2 · Clarify a fuzzy one | `/bandit:clarify` |
| 3 · Evaluation gate: does it make sense now? | `/bandit:tasks triage`: yes → fields answered, date last · not yet → stays parked |
| Plan the project or a deliverable | `/bandit:plan project` → `/bandit:plan wbs` → `/bandit:tasks load` |
| Run it | `/bandit:tasks today` · `/bandit:tasks week` |
| Notes and records | `/bandit:notes file` · `/bandit:minutes` |

## 🧩 Modes

| Mode | Trigger | Behaviour |
|---|---|---|
| 🧠 Brain dump | "brain dump" | Capture verbatim, structure only when told done |
| 🔍 Reality check | an idea about to become a plan | Challenge market, cost, feasibility; sourced claims only |
| 🗂️ Planning | "plan this" | `/bandit:plan`, one section at a time |

## 🚫 Hard rules

- For technical decisions, present options with trade-offs and a recommendation
- Rules live in the skills: this page never restates them
