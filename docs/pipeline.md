# 🔄 The delivery pipeline

> The canonical definition of the eleven stages from an idea to a closed release: surface, owning command, record and gate for each. Skills implement it; projects supply the recipe in `bandit.yaml`.

This file is the single definition (decision S1). Skills point here; app repos hold only their `bandit.yaml` and their own hooks.

## 🗺️ Stages

| # | Stage | Surface | Owner command | Record | Gate (fails when skipped) |
|---|---|---|---|---|---|
| 1 | **Capture** an idea into the board inbox | Claude.ai, phone, Claude Code | `/bandit:tasks capture` | A parked or untriaged card | `/bandit:tasks audit` row for untriaged parked cards |
| 2 | **Clarify** the fuzzy ones | Claude.ai | `/bandit:clarify` | Clarified Specification | Hand-off row to `/bandit:tasks spec` |
| 3 | **Triage and specify**: leave the inbox, fields answered, date last; write the Spec | Claude.ai or Claude Code | `/bandit:tasks triage`, `/bandit:tasks spec` | Card fields, Spec, lane, `stage/spec` (a screen-changing card waits without it until Design), brief | The board's Spec lock; brief present |
| 4 | **Design** the cards that change a screen, after their Spec is written; the rest skip it | Claude Code, from the app repo | Claude Design inside Claude Code: `/design-sync` once per project and when the shared look changes (the session ends by asking you to run it, and the design card records `Design sync run {date}` or `Design sync not needed: {reason}`), `/design` per card (bandit:tasks `dev-workflow.md` → Design step) | The design page's full web address on the card (`Design:` beside `Brief:`) and where the handover files live (`Handover:`), checked against the project's recorded traps, and the person's approval as a card comment | `/bandit:tasks spec` and `stage` refuse `stage/spec` on a screen-changing card without both. With a `design:` line in the Project Context, the design is a card of its own, linked as the build card's blocker; its approved handover unblocks the build, and the design card carries the page link (`Design page:`) and the files' place (`Handover:`), the build card the same page link (`dev-workflow.md` → Design card); sprint planning flags a screen card whose design card is open or whose `Design:` line is missing or not a full web address |
| 5 | **Plan the sprint** | Claude Code | `/bandit-dev:sprint plan` | The sprint in the app (status, cards in run order), plan, WBS (sprint mode), execution prompt, ledger | The ledger's Plan steps; sprint checker (SP9, SP10, SP12); the sprint map drawn; sub-task gate: no Technical plan and no commit without build steps (SB1); description gate: no card description the app shows as raw tags (DF1); no plan item left for after debug (SP14) |
| 6 | **Independent plan review** | Claude Code (agent) | `/bandit-dev:sprint plan`, step 11 (`plan-reviewer` agent) | Review record in the sprint folder | `run` refuses a review not done; checker SP7 |
| 7 | **Run** the waves, push the trunk | Claude Code | `/bandit-dev:sprint run`; each live check's data from `/bandit-dev:testdata create`, removed by `clean` | Ledger lines and Waves rows, the sprint Executing then Debugging, cards in Stand By; the staging handover card filled by the final push; a screen card compared once with its design handover; the wave report and the sprint map rebuilt after each wave (Flow and Tokens from the chat logs, lessons the next plan reads) | Sprint-order gate; checker SP11; migration-tail stop; status line fresh; a check not run for lack of data fails the wave; per card review, one UI check, one full check only when code changed, then merge (GO1, FC1) |
| 8 | **Test** on staging | The person | The project's staging recipe (`bandit.yaml` `staging`); with Marketplace cards, the new helpers from the repo in a test session against staging, tested together with the app | Ledger "tested" lines | `release` precondition |
| 9 | **Debug** | Claude Code | `/bandit-dev:sprint debug` | Bug log of defects (against the card or the approved design); anything new becomes a card for a later sprint; each fix runs its targeted tests, one full check before each push; the shared debug card (moves to Doing when debug starts) holds every Expected, Found and Process line, each ticked with its outcome | DB1 · DK1 · FC1 (the full check before a push only when code changed) |
| 10 | **Release** on the person's word, optional | Claude Code | `/bandit-dev:sprint release` | The debug card to Stand By first; version, release line in the ledger naming every sprint it covers (this one and the deferred ones before it); plugin bump when Marketplace cards ship; one production handover card filled (`bandit.yaml` `handover`), or, when the recipe names no production card, the deploy run by the recipe's own steps | Nothing owed to the repository (SP14, precondition 8); the full check only when code changed (FC1); a sprint that changed the helpers is not closed before their release |
| 11 | **Close** | Claude Code | `/bandit-dev:sprint close` | Each approved card's approval sub-task ticked and the card complete (the debug card too), the sprint Closed, sprint folder archived; `Release: deferred` when it closes with no app release; an old-way sprint brought into the app first | Close makes no commit (the trunk level with the released branch); folder and WBS archived (SP15) |

## 🧭 Surfaces

- **Claude.ai** runs stages 1–3. Its agent is the project instructions (from `templates/instructions/`) plus the `bandit` skills. Hooks and agents don't run there, so only the board's own refusals enforce rules.
- **Claude Code** runs stages 3–11: stage 4 with Claude Design, stages 5–11 with `bandit-dev`: its hooks and the `plan-reviewer` agent run there.

## 📦 What a project supplies

The recipe for stages 7–10 (verify, branches, release steps, migration tail, staging, test data, deployment handover) is read from `bandit.yaml` at the app repo root.

**Test data** (`/bandit-dev:testdata`) runs at stage 5 (`make` names the data each live check needs), stage 7 and 9 (`create` before a check, `clean` after it) and on demand (`fill` puts a lasting made-up set in development, test or staging). Made-up data only; staging writes ask the person's yes on every run. A missing key refuses and names the key. Contract: `plugins/bandit-dev/skills/sprint/references/bandit-yaml.md`, shipped with the plugin.
