# 🦝 bandit-brain-marketplace

The Claude plugin marketplace of Bandit Brain.

## 🧭 Project Context

domain: BanditLabs
project: bandit-brain-marketplace
type: claude_marketplace
board: project "BB: Development"
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

The single source of the skills, agents and hooks Claude uses with Bandit Brain: marketplace `bandit-brain`, three plugins. `bandit` (core skills, Claude.ai + Claude Code), `bandit-dev` (the sprint pipeline, Claude Code) and `bandit-maker` (building these skills, Bandit Port only). Marketplace cards live on the board **BB: Marketplace** (columns Bandit and Bandit Dev) since 2026-11-22; sprints and this project's notes are still on BB: Development until the skills and this Project Context are repointed (card BM-T5). Decisions: `docs/decisions.md`. The pipeline: `docs/pipeline.md`.

## 📁 Layout

```
.claude-plugin/marketplace.json     name: bandit-brain
.claude/settings.json               build-session guardrails (G2–G4) + dev-mirror Stop hook
.claude/hooks/mirror-check.py       dev mirror script
.githooks/pre-commit                runs the checker
.github/                            CI gate, release publishing, issue and PR templates
assets/                             the Bandit Brain logo
.work/                              git-ignored working files: import/ (frozen skill snapshot), test/ (test folder)
plugins/bandit/                     skills/{tasks,notes,project,audit,clarify,rewrite,plan,minutes}/
plugins/bandit-dev/                 skills/sprint/ · agents/plan-reviewer.md · hooks/hooks.json
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
- **Nothing outside the repo.** Working files go in `.work/`. The only writes outside are this project's notes in the app, its settings rows in the vault, and the Bandit CTO change log.
- **Never edit `.claude/settings*.json`** in a build session, except an approved hook change.
- **Branches:** work on `development`, push it. `main` and tags move only by `release.py`, which runs as the last step of done.
- **The version number:** the one Leo gave, if he gave one. Otherwise the next one by the CHANGELOG's SemVer rule. Never ask.
- **Done means released. No approval, no deploy word, no question.** A change is not done until it is released. Leo can only test the plugins once they reach `main` (that is when Claude.ai and Claude Code pick them up). So the `bandit-dev` release gates do not apply here: no "tested by the user", no debug-done, no backup step. Before releasing, the checker is green, `done_check.py` has nothing open, and `development` is clean and level with origin. Then `release.py {version}`, `--write`, `--push`, and check `main` and the tag on origin. Only then say done. The release does not close the cards: they stay in Stand By with the approval line (`Tested and approved by you`) open until Leo has tested them and ticked that line, which is his yes; then `close` runs to the archive with no question (a card with the line open is asked about alone). His findings come back as fixes and a new release.
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

## 🗂️ Notes and vault

Notes are in the app's Notes (`notes: app`, since 1.0.0); this project's vault notes are frozen, read-only.

| What | Where |
|---|---|
| Process docs, hub | Notes on the BanditBrain board (hub `bandit-brain-marketplace`) |
| Sprint records | Notes on the BanditBrain board tagged `sprint-{name}`; map and data files in `.sprint/` |
| Audit stamp ledger | Vault: `MyNotes/BanditLabs/Projects/bandit-brain-marketplace/.audit/stamps.json` |
| Dev mirror | Vault: `MyNotes/BanditLabs/Claude/code-bandit-brain-marketplace/` (written by the Stop hook through a synced folder) |
| Claude.ai settings | Vault: `MyNotes/BanditLabs/Claude/ai-bandit-brain-marketplace/` |

## ⌨️ Aliases (Bandit Port)

| Alias | Does |
|---|---|
| `bbm` | cd into the repo |
| `bbm-cc` | Build session: Claude Code with Remote Control, `bypassPermissions` (deny rules still apply) |
| `bbm-rc` | Remote Control server, same mode |
