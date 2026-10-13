# 🦝 bandit-brain-marketplace

Claude skills, agents and hooks for working with **Bandit Brain**: the task board, the notes vault, project setup and the delivery pipeline from an idea in the inbox to a release. One marketplace, `bandit-brain`, for Claude.ai and Claude Code.

## 🧩 The three plugins

| Plugin | For | Contents | Surfaces |
|---|---|---|---|
| `bandit` | Everyone | Skills: `tasks`, `notes`, `project`, `audit`, `clarify`, `rewrite`, `plan`, `minutes` | Claude.ai + Claude Code |
| `bandit-dev` | Developers | Skill `sprint`, agent `plan-reviewer`, sprint hooks. Depends on `bandit` | Claude Code |
| `bandit-maker` | Building this marketplace | Skill `skill` (author and lint skills) | Claude Code, Bandit Port |

Skills are called by plugin and area, with the verb as argument: `/bandit:tasks triage`, `/bandit:notes file`, `/bandit-dev:sprint run`.

## 🚀 Install

Claude Code:

```
/plugin marketplace add l3ocho/bandit-brain-marketplace
/plugin install bandit@bandit-brain
/plugin install bandit-dev@bandit-brain        (developers)
/plugin install bandit-maker@bandit-brain      (Bandit Port only)
```

Claude.ai: Customize → Plugins → Add marketplace → `l3ocho/bandit-brain-marketplace` → install `bandit`.

Full deploy steps: `docs/install.md`.

## 🔧 Develop

`python3 scripts/check_repo.py` is the gate: it runs as a git pre-commit hook and must be green. Conventions for working here are in `CLAUDE.md`; decisions in `docs/decisions.md`; the pipeline in `docs/pipeline.md`.

## 📄 License

MIT. `plugins/bandit-maker/skills/skill/` carries its upstream Apache 2.0 `LICENSE.txt`.
