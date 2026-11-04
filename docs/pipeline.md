# 🔄 The delivery pipeline

> The canonical definition of the eleven stages from an idea to a closed release: surface, owning command, record and gate for each. Skills implement it; projects supply the recipe in `bandit.yaml`.

This file is the single definition (decision S1). Skills point here; app repos hold only their `bandit.yaml` and their own hooks.

## 🗺️ Stages

| # | Stage | Surface | Owner command | Record | Gate (fails when skipped) |
|---|---|---|---|---|---|
| 1 | **Capture** an idea into the board inbox | Claude.ai, phone, Claude Code | `/bandit:tasks capture` | A parked or untriaged card | `/bandit:tasks audit` row for untriaged parked cards |
| 2 | **Clarify** the fuzzy ones | Claude.ai | `/bandit:clarify` | Clarified Specification | Hand-off row to `/bandit:tasks spec` |
| 3 | **Triage and specify**: leave the inbox, fields answered, date last; write the Spec | Claude.ai or Claude Code | `/bandit:tasks triage`, `/bandit:tasks spec` | Card fields, Spec, lane, `stage/spec` (a screen-changing card waits without it until Design), brief | The board's Spec lock; brief present |
| 4 | **Design** the cards that change a screen, after their Spec is written; the rest skip it | Claude Code, from the app repo | Claude Design inside Claude Code: `/design-sync` once per project, `/design` per card (bandit:tasks `dev-workflow.md` → Design step) | The design's link on the card (`Design:` beside `Brief:`), checked against the project's recorded traps, and the person's approval as a card comment | `/bandit:tasks spec` and `stage` refuse `stage/spec` on a screen-changing card without both |
| 5 | **Plan the sprint** | Claude Code | `/bandit-dev:sprint plan` | The sprint in the app (status, cards in run order), plan, WBS (sprint mode), execution prompt, ledger | The ledger's Plan steps; sprint checker (SP9, SP10) |
| 6 | **Independent plan review** | Claude Code (agent) | `/bandit-dev:sprint plan`, step 11 (`plan-reviewer` agent) | Review record in the sprint folder | `run` refuses a review not done; checker SP7 |
| 7 | **Run** the waves, push the trunk | Claude Code | `/bandit-dev:sprint run`; each live check's data from `/bandit-dev:testdata create`, removed by `clean` | Ledger lines and Waves rows, the sprint Executing then Debugging, cards in Stand By; the staging handover card filled by the final push | Sprint-order gate; migration-tail stop; status line fresh; a check not run for lack of data fails the wave |
| 8 | **Test** on staging | The person | The project's staging recipe (`bandit.yaml` `staging`); with Marketplace cards, the new helpers from the repo in a test session against staging, tested together with the app | Ledger "tested" lines | `release` precondition |
| 9 | **Debug** | Claude Code | `/bandit-dev:sprint debug` | Bug log of defects (against the card or the approved design); anything new becomes a card for a later sprint | Existing checks |
| 10 | **Release** on the person's word, optional | Claude Code | `/bandit-dev:sprint release` | Version, release line in the ledger naming every sprint it covers (this one and the deferred ones before it); plugin bump when Marketplace cards ship; one production handover card filled (`bandit.yaml` `handover`), or, when the recipe names no production card, the deploy run by the recipe's own steps | Release gates unchanged; a sprint that changed the helpers is not closed before their release |
| 11 | **Close** | Claude Code | `/bandit-dev:sprint close` | Cards complete, the sprint Closed, sprint folder archived; `Release: deferred` when it closes with no app release; an old-way sprint brought into the app first | Existing checks |

## 🧭 Surfaces

- **Claude.ai** runs stages 1–3. Its agent is the project instructions (from `templates/instructions/`) plus the `bandit` skills. Hooks and agents don't run there, so only the board's own refusals enforce rules.
- **Claude Code** runs stages 3–11: stage 4 with Claude Design, stages 5–11 with `bandit-dev`: its hooks and the `plan-reviewer` agent run there.

## 📦 What a project supplies

The recipe for stages 7–10 (verify, branches, release steps, migration tail, staging, test data, deployment handover) is read from `bandit.yaml` at the app repo root.

**Test data** (`/bandit-dev:testdata`) runs at stage 5 (`make` names the data each live check needs), stage 7 and 9 (`create` before a check, `clean` after it) and on demand (`fill` puts a lasting made-up set in development, test or staging). Made-up data only; staging writes ask the person's yes on every run. A missing key refuses and names the key. Contract: `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md`, shipped with the plugin.
