# 🦝 bandit-brain-marketplace

The Claude plugin marketplace of Bandit Brain.

## 🧭 Project Context

domain: BanditLabs
project: bandit-brain-marketplace
type: claude_marketplace
board: project "BanditBrain"
prefix: bbm
dev: true

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

The single source of the skills, agents and hooks Claude uses with Bandit Brain: marketplace `bandit-brain`, three plugins. `bandit` (core skills, Claude.ai + Claude Code), `bandit-dev` (the sprint pipeline, Claude Code) and `bandit-maker` (building these skills, Bandit Port only). Marketplace cards live in the **Marketplace** column of the BanditBrain board. Decisions: `docs/decisions.md`. The pipeline: `docs/pipeline.md`.

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
docs/                               decisions.md · pipeline.md · bandit-yaml.md · install.md · cheat-sheet.md
scripts/check_repo.py               the repo checker
scripts/release.py                  cuts a release (SemVer, tags vX.Y.Z)
```

## 🔒 Rules

**Context-light rules L1–L8** and **build-session guards G1–G9**: full text in `docs/decisions.md`.

| Rules | In one line |
|---|---|
| L1 description ≤ 300 chars · L2 `SKILL.md` ≤ 150 lines · L3 one home per rule · L4 no project details · L5 instructions template ≤ 1 page · L6 app `CLAUDE.md` ≤ 10 KB · L7 no plugin `bin/` · L8 no person's name in plugins | Every installed skill loads into every chat: keep it light |
| G1 inert tree · G2 installed plugins off · G3 old copies denied · G4 new names denied · G5 no production deletes · G6 deny coverage checked · G7 read, never invoke · G8 tests from `.work/test/` · G9 hub safety | The build session never uses what it builds |

- **Never invoke your own skills**, old or new names. Read their source as documents and follow it (G7).
- **Nothing outside the repo.** Working files go in `.work/`. The only writes outside are vault rows in this project's folders and the Bandit CTO change log.
- **Never edit `.claude/settings*.json`** in a build session, except an approved hook change.
- **Branches:** work on `development`, push it. `main` moves only on Leo's deploy word; tags only at release.
- **The version number is Leo's.** Release only the number Leo gave, or the one I told him before building. Never pick a different one at release time, whatever the changelog rule says. No number agreed → ask in one line before the release.
- **The app clone** (`~/projects/banditlabs/bandit_brain`) is read-only reference.
- **Staging:** `bb-staging status`, `smoke`, `logs` are fine. Never `bb-staging up --refresh` during a freeze.

## ✅ Verify

```
python3 scripts/check_repo.py               # the gate; also the git pre-commit hook
claude plugin validate plugins/<plugin>     # one plugin
python3 plugins/bandit-maker/skills/skill/scripts/house_lint.py plugins/bandit/skills/*
```

The checker must be green before every commit. A new kind of mistake becomes a new checker rule, not a new sentence.

## 🗂️ Vault

| What | Where (`MyNotes/BanditLabs/`) |
|---|---|
| Process docs, hub | `Projects/bandit-brain-marketplace/` (hub `bandit-brain-marketplace.md`) |
| Sprint records | `Projects/bandit-brain-marketplace/sprint-{name}/` |
| Audit stamp ledger | `Projects/bandit-brain-marketplace/.audit/stamps.json` |
| Dev mirror | `Claude/code-bandit-brain-marketplace/` (written by the Stop hook through a synced folder) |
| Claude.ai settings | `Claude/ai-bandit-brain-marketplace/` |

## ⌨️ Aliases (Bandit Port)

| Alias | Does |
|---|---|
| `bbm` | cd into the repo |
| `bbm-cc` | Build session: Claude Code with Remote Control, `bypassPermissions` (deny rules still apply) |
| `bbm-rc` | Remote Control server, same mode |
