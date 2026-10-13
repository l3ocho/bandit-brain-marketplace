# 🔄 The delivery pipeline

> The canonical definition of the ten stages from an idea to a closed release: surface, owning command, record and gate for each. Skills implement it; projects supply the recipe in `bandit.yaml`.

This file is the single definition (decision S1). Skills point here; app repos hold only their `bandit.yaml` and their own hooks.

## 🗺️ Stages

| # | Stage | Surface | Owner command | Record | Gate (fails when skipped) |
|---|---|---|---|---|---|
| 1 | **Capture** an idea into the board inbox | Claude.ai, phone, Claude Code | `/bandit:tasks capture` | A parked or untriaged card | `/bandit:tasks audit` row for untriaged parked cards |
| 2 | **Clarify** the fuzzy ones | Claude.ai | `/bandit:clarify` | Clarified Specification | Hand-off row to `/bandit:tasks spec` |
| 3 | **Triage and specify**: leave the inbox, fields answered, date last; write the Spec | Claude.ai or Claude Code | `/bandit:tasks triage`, `/bandit:tasks spec` | Card fields, Spec, lane, `stage/spec`, brief | The board's Spec lock; brief present |
| 4 | **Plan the sprint** | Claude Code | `/bandit-dev:sprint plan` | Sprint card, plan, WBS (sprint mode), execution prompt, ledger | Plan step sub-tasks; sprint checker |
| 5 | **Independent plan review** | Claude Code (agent) | `/bandit-dev:sprint plan`, step 11 (`plan-reviewer` agent) | Review record in the sprint folder | `run` refuses an unticked review; checker SP7 |
| 6 | **Run** the waves, push the trunk | Claude Code | `/bandit-dev:sprint run` | Ledger lines, wave sub-tasks, cards in Stand By | Sprint-order gate; migration-tail stop; status line fresh |
| 7 | **Test** on staging | The person | The project's staging recipe (`bandit.yaml` `staging`) | Ledger "tested" lines | `release` precondition |
| 8 | **Debug** | Claude Code | `/bandit-dev:sprint debug` | Bug log, fixes | Existing checks |
| 9 | **Release** on the person's word | Claude Code | `/bandit-dev:sprint release` | Version, release line in ledger and sprint card; plugin bump when Marketplace cards ship | `close` refuses without a release line |
| 10 | **Close** | Claude Code | `/bandit-dev:sprint close` | Cards complete, sprint folder archived | Existing checks |

## 🧭 Surfaces

- **Claude.ai** runs stages 1–3. Its agent is the project instructions (from `templates/instructions/`) plus the `bandit` skills. Hooks and agents don't run there, so only the board's own refusals enforce rules.
- **Claude Code** runs stages 3–10 with `bandit-dev`: its hooks and the `plan-reviewer` agent run there.

## 📦 What a project supplies

The recipe for stages 6–9 (verify, branches, release steps, migration tail, staging) is read from `bandit.yaml` at the app repo root. A missing key refuses and names the key. Contract: `docs/bandit-yaml.md`.
