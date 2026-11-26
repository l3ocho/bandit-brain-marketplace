# 🦝 bandit-brain-marketplace

The Claude plugin marketplace of Bandit Brain.

## 🧭 Project Context

domain: BanditLabs
project: bandit-brain-marketplace
type: claude_marketplace
board: project "BB: Marketplace"
prefix: bbm
dev: true
notes: app

Read by every `bandit` skill.
**Home board first. Read and write across the domain. Nothing outside it.**
Names only: skills resolve IDs live via `get_context`. No hardcoded IDs, ever.

---

## 🗣️ Talking to Leo

Read first. This wins over every other habit in this repo.

- **Short and plain.** Problem, fix, done. Every term comes with its context: never a phrase Leo has not seen in the chat.
- **No codes in chat.** No rule codes (L3, G7, SP5), no made-up labels (Q1, A2, D3, "row 4"), no step numbers. Say the thing in words.
- **No counts of what you made.** Say what changed for Leo, not how many sub-tasks, comments or files you wrote.
- **You built this marketplace.** Say "I" and own every mistake. Never talk about the skills as someone else's work.
- **Build what Leo asked, in Leo's words.** Anything different gets one line before it is written: "You asked for X. I'd build Y, because Z." No yes, no build.
- **Read before asking.** The repo, git log, the board and the ledger answer most questions. Ask only what none of them can answer.
- **Memory can be old.** Check a memory note against git, the board and the ledger before acting on it. They win.

---

## 🗺️ What this repo is

The single source of the skills, agents and hooks Claude uses with Bandit Brain: marketplace `bandit-brain`, three plugins. `bandit` (core skills, Claude.ai + Claude Code), `bandit-dev` (the sprint pipeline, Claude Code) and `bandit-maker` (building these skills, Bandit Port only). This project's home board is **BB: Marketplace** (columns Bandit and Bandit Dev): its cards since 2026-11-22, its notes and its marketplace-only sprints since 2026-11-24 (BM-T5). A mixed sprint that also carries app cards stays on BB: Development and runs from the app project. Decisions: `docs/decisions.md`. The pipeline: `docs/pipeline.md`.

## ⚖️ Project matter or plugin matter

Decide this before every change. Leo, 2026-11-26.

- **Project settings** belong to one project and live in that project: its `CLAUDE.md` (with the Project Context block) and `.claude/` in Claude Code, or its Claude.ai project instructions, plus its `bandit.yaml` recipe. They hold everything true for that project only: names, boards, columns, IDs, paths, commands, environments (how its staging updates, its freeze), its own rules and choices. One copy, in the project.
- **Plugin settings** are what ships in `plugins/`: skills, references, scripts, hooks, agents. Every project that installs them gets them, so they hold only the generic how: steps, formats, gates. They never state a fact about one project (not a name, and not how its environment behaves either). Where a step depends on the project, the plugin reads the project's settings or recipe; when the recipe has nothing, it asks or shows, never assumes.
- **The test:** would it be true for every project that installs the plugin? Yes → plugin matter: I change the plugin and release it. No → project matter: it goes in that project's settings, not in a skill. Another project's settings are its own agent's: I open a card for that agent and stop there.
- **This repo is both.** How this marketplace project works goes in this `CLAUDE.md`, never in a skill; a skill's rule never goes in this `CLAUDE.md`.

## 📁 Layout

```
.claude-plugin/marketplace.json     name: bandit-brain
.claude/settings.json               build-session guardrails (G2–G4)
.githooks/pre-commit                runs the checker
.github/                            CI gate, release publishing, issue and PR templates
assets/                             the Bandit Brain logo
.work/                              git-ignored working files: import/ (frozen skill snapshot), test/ (test folder)
plugins/bandit/                     skills/{tasks,notes,project,audit,clarify,rewrite,plan,minutes}/
plugins/bandit-dev/                 skills/sprint/ · agents/plan-reviewer.md, wave-records.md · hooks/hooks.json
plugins/bandit-maker/               skills/skill/
templates/instructions/             one-page project instructions per project type
tests/                              cases.md · fixture-app/
docs/                               decisions.md · pipeline.md · bandit-yaml.md · install.md · cheat-sheet.md · dependencies.md
scripts/check_repo.py               the repo checker
scripts/release.py                  cuts a release (SemVer, tags vX.Y.Z)
scripts/done_check.py               lists each place a change since the last release must reach
```

## 🔒 Rules

**Context-light rules L1–L8** and **build-session guards G1–G9**: full text in `docs/decisions.md`.

| Rules | In one line |
|---|---|
| L1 description ≤ 300 chars · L2 `SKILL.md` ≤ 150 lines · L3 one home per rule · L4 no project details · L5 instructions template ≤ 1 page · L6 app `CLAUDE.md` ≤ 10 KB · L7 no plugin `bin/` · L8 no person's name in plugins | Every installed skill loads into every chat: keep it light |
| G1 inert tree · G2 installed plugins off · G3 old copies denied · G4 new names denied · G5 no production deletes · G6 deny coverage checked · G7 read, never invoke · G8 tests from `.work/test/` · G9 hub safety | The build session never uses what it builds |

- **Never invoke your own skills**, old or new names. Read their source as documents and follow it (G7).
- **Nothing outside the repo.** Working files go in `.work/`. The only writes outside are this project's notes in the app and the Bandit CTO change log.
- **Never edit `.claude/settings*.json`** in a build session, except an approved hook change.
- **Branches:** work on `development`, push it. `main` and tags move only by `release.py`, which runs as the last step of done.
- **The version number:** the one Leo gave, if he gave one. Otherwise the next one by the CHANGELOG's SemVer rule. Never ask.
- **Done means released. No approval, no deploy word, no question.** A change is not done until it is released. Leo can only test the plugins once they reach `main` (that is when Claude.ai and Claude Code pick them up). So the `bandit-dev` release gates do not apply here: no "tested by the user", no debug-done, no backup step. Before releasing, the checker is green, `done_check.py` has nothing open, and `development` is clean and level with origin. Then `release.py {version}`, `--write`, `--push`, and check `main` and the tag on origin. Only then say done. The release does not close the cards: they stay in Stand By with the approval line (`Tested and approved by you`) open until Leo has tested them and ticked that line, which is his yes; then `close` runs to the archive with no question (a card with the line open is asked about alone). His findings come back as fixes and a new release. In a marketplace sprint run by the sprint helper, the build cards are completed at delivery and the approval lines wait on the sprint's debug card instead (`templates.md` → Approval line); `close` runs on those the same way.
- **The app clone** (`~/projects/banditlabs/products/banditbrain/dev`) is read-only reference.
- **Staging:** `bb-staging status`, `smoke`, `logs` are fine. Never `bb-staging up --refresh` during a freeze.

## ✅ Verify

```
python3 scripts/check_repo.py               # the gate; also the git pre-commit hook
python3 scripts/done_check.py               # what changed since the last release, and what must change with it
claude plugin validate plugins/<plugin>     # one plugin
python3 plugins/bandit-maker/skills/skill/scripts/house_lint.py plugins/bandit/skills/*
```

The checker must be green before every commit. **Done** = the checker green, `done_check.py` with nothing open (or each open row checked and named), app behaviour run on staging, and the release pushed to `main` with its tag; the outputs go in the report (`docs/dependencies.md`). A new kind of mistake becomes a new checker rule, not a new sentence.

## 🗂️ Notes

This project's notes are in the app's Notes; nothing of it lives in a file storage.

| What | Where |
|---|---|
| Process docs, hub | Notes on this project's board. A note linked to a card stays on that card's board (the app's rule), so the hub `bandit-brain-marketplace` and the plans and briefs of cards completed before 2026-11-22 are still on BB: Development |
| Sprint records | Notes on this project's board tagged `sprint-{name}`; the sprint data file in `.sprint/` |
| Audit stamps | The note `banditlabs-audit-stamps` on the domain's workflow board: this project's section, written by `/bandit:audit check` |
| Settings | This file and `.claude/`: the one configuration, in this repository |

## ⌨️ Aliases (Bandit Port)

| Alias | Does |
|---|---|
| `bbm` | cd into the repo |
| `bbm-cc` | Build session: Claude Code with Remote Control, `bypassPermissions` (deny rules still apply) |
| `bbm-rc` | Remote Control server, same mode |
