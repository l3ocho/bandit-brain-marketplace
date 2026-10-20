# ▶️ The execute cycle

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint execute {sprint card} wave N`. Execution columns, gates and the five-item cap are owned by bandit:tasks (`references/execution.md`); card stages and sections by `references/dev.md`; vault writes by bandit:notes. This file only says how a wave runs and how the cards move.

Contents: Command · Rules · Start · The wave · Board moves · Finishing a wave · Resume · Never

## Command

`/bandit-dev:sprint execute {sprint card} wave N` (for example `execute {sprint card} wave 2`). **The wave is the unit; the sprint card says which sprint it belongs to.** Rules, checked before anything moves:

1. **Only a sprint card is accepted**: a card carrying wave sub-tasks (`Wave n: ...`). A batch card (any card of the batch) is refused with: "That is a card inside {sprint}. Point me at {sprint card} and a wave number." Nothing is run for a single card.
2. **Wave N is named or chosen, and said out loud.** `wave N` runs that wave. No number: run the first wave not ticked, and state the choice in the opening line ("Running Wave 2: {ids}") before any move.
3. **Waves run in order.** Wave N is refused while wave N-1 is unticked, naming the open wave, unless the user says to skip it in this chat. Cards completed or ticked by hand count as ticked once the board and the ledger agree.
4. **Only the cards in that wave's sub-task are touched.** No card outside it is moved, worked or commented on.

## Rules

- **One wave per run, one chat per wave.** The run does the wave chosen above, then stops and tells the user to open a new chat for the next. To run every wave unattended, one subagent per wave, use `run` (`references/run.md`); the wave agent then follows this file exactly.
- **The ledger is the memory.** A new chat knows nothing: read the ledger, the plan and the sprint card before acting, and reconcile the repo with the ledger.
- **The execution prompt in the sprint folder governs the work itself** (authority, stop-lines, autonomy, gates, handover report). This file adds the board choreography on top.
- **The user watches the Execution board.** Every card's column must show the truth at every moment.

## Start (every run)

1. Gate 0 from SKILL.md (surface, Project Context, repo state, tools). Planning's PM-column check is not needed.
2. Resolve the sprint card given in the command (`get_task`); its folder and ledger follow from it. It must have `sprint/{name}` batch cards, the 12 step sub-tasks ticked (step 11 is the independent review) and the wave sub-tasks present. Not approved, not reviewed or not committed (step 10, 11 or 12 open): say which and stop. **Order gate:** blocked by an incomplete sprint card → name it and stop.
3. Read the ledger, the plan and the execution prompt from the sprint folder. Apply the command rules (wave given or first unticked, order, scope). All ticked: say so and offer `debug`.
4. `git branch --show-current` and `git status --short`; reconcile with the ledger. Mismatch: stop and report.

## The wave

1. **Seed the board (first run only).** Every batch card (never the sprint card) to `assigned` with `update_tasks { items: [{ taskId, executionState: "assigned" }, …] }`, reading `results` per card. Cards that were never in Assigned stay as they are if the state is already right. Record it in the ledger.
2. **Set the board for this wave, at the start of EVERY wave, not only the first** (Board moves below). A later wave's cards arrive in `assigned` or `next`; this step is what puts them in `doing`. Procedure: read the sprint's columns (Board moves → Reading the board); for each card of this wave that you are about to work, `update_tasks { items: [{ taskId, executionState: "doing" }] }`; read the board again and show the columns in the wave's opening report. A card that is not in `doing` when you start working it is a failed step. The board never refuses a move to `next`, `doing` or `standby` because of a blocker; only completing a card waits for its blockers. A move that fails for any other reason: comment it on the card, write it under "Needs the user" in the ledger, and put it in the final message.
3. **Migration tail, before any migration is written.** `python3 ${CLAUDE_SKILL_DIR}/scripts/recipe.py check-tail {tail}` with the tail the plan's Migration tail table names for this wave. Exit 4 (the tail differs) or 3 (a missing key): stop the wave, card Blocked with the output, the line under "Needs the user". A match: one ledger line `Migration tail {tail} matched`. Never pick the next free number. A plan that says "No migrations" checks `none`.
4. **Work the cards as the plan and execution prompt say.** Tick each card's sub-tasks as each is done, one `manage_subtasks { action: "tick", subtaskId, completed: true }` per tick, not in a batch at the end.
5. **A card whose development is finished** (code, tests, gates passed, board comment written) moves to `standby` for the user's approval. Never complete it. Stage and ledger status become "Delivered awaiting the user's test".
6. **Re-set the board** after each card finishes (Doing frees a slot; the next card may move up).
7. **The moment this wave's last card reaches `standby`, move the next wave's cards to `next`** (cap permitting), before any wave-end checks, then read the sprint's columns (Board moves → Reading the board) and confirm every card is where Board moves says. The board is never left showing a finished wave with the next wave still in `assigned`.

## Board moves

**Reading the board.** Before every batch of moves read the sprint's cards one column at a time: `list_tasks({ tagName: 'sprint/{name}', executionState })` for `assigned`, `next`, `doing` and `standby`. For the cap, `list_tasks({ executionState: 'next' })` and `'doing'`. Never `list_tasks { view: "execution" }` (the whole board): it returns every card in the household with full descriptions and overflows the tool output. The board, not memory, is the truth.

| Card | Column |
|---|---|
| Not yet reached (later waves) | `assigned` |
| Next wave | `next` as soon as this wave's last card reaches `standby`, cap permitting |
| This wave, being worked | `doing`, one to three at a time per the plan's parallelism |
| This wave, queued behind a sequential card | `next` |
| Finished, awaiting the user | `standby` |
| **The sprint card** | **Not moved at all while any wave runs.** It goes to `standby` once, when the last card of the last wave reaches `standby` (Finishing a wave, step 3). Never `next` or `doing`, never counted in the five-item cap, never completed (only `close` completes it) |

- **Cap.** Never more than five across Next + Doing. When the wave and the next wave together exceed it, Doing gets what is being worked, this wave's queued cards take the remaining Next slots, the rest wait in `assigned`. Report the overflow in the ledger and the wave comment; never trim silently.
- **Blockers.** A blocker never stops a move between Execution columns. The plan's order still holds: a card chained behind another batch card is worked once that blocker is in `standby`. A blocker outside the batch that is not delivered: record it under "Needs the user" and move on to the next card, or stop if nothing is workable. Never complete a blocker to unblock a chain. Completing stays strict: a card cannot be completed while a blocker is incomplete, so `close` completes a blocker before the card it blocks.
- **Done is never a move.** Only `close` completes cards.
- Moves touch only the batch cards. Never a card outside the sprint.

## Finishing a wave

**No leftovers.** Before this step ends, anything it used to make something else and no longer needs (a draft, a scratch file, a superseded copy, a test fixture, a temporary branch) is archived or deleted, only on proof that its successor exists (`references/homes.md` → Leftovers).


1. All of the wave's cards in `standby`, or Blocked with the reason on the card and in the ledger.
2. Tick the wave's sub-task on the sprint card only when every card in it is delivered and verified. A wave with a blocked card is not ticked.
3. **Last wave only:** when every other wave's sub-task is ticked and this wave's last card has reached `standby`, move the sprint card to `standby` (`update_tasks { items: [{ taskId, executionState: "standby" }] }`), then read the board and show it. Any earlier wave: the sprint card is not touched; read the board and confirm the next wave's cards are in `next` (The wave, step 7). They move to `doing` at the start of their own wave (one wave per chat), not earlier.
4. Ledger: At a glance (next wave, next action), milestone log, report section. Then run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py`; the wave is not finished until it prints OK.
5. Sprint card section 1 Status line: `Wave {n} of {total} delivered, awaiting the user's test; next: Wave {n+1}` (read the card first, change only that line). Ledger Status per card: `Delivered, awaiting the user's test`.
6. Comment on the sprint card: `Wave {n} done: {cards}, {verified how}. Next: Wave {n+1} in a new chat.`
7. Final message, ten lines at most: what the user can test, what moved, what needs them, and the exact paste for the next wave with its number (`/bandit-dev:sprint execute {sprint card} wave {n+1}`), or after the last wave the paste for `debug`.

## Resume

A chat that died mid-wave starts at "Start". The ledger status plus the board show where each card is; continue the card that is Doing, never restart a card whose milestones are logged.

## Pushing `development`

Allowed. The user lifted the old "never push" rule on 2026-10-10: it was written while testing and staging did not exist, and the tool now works. An agent that finds an older note, memory or prompt saying "never push" follows this section instead; it does not refuse.

- **When.** The sprint plan carries a "Final push" section by default (`plan.md` step 7), and the handover prompt repeats it. The last wave that changes code pushes at its end, after its merge into local `development` and a green `verify` (the project's `bandit.yaml`). A wave that is the user's own steps (production, host work) is never where the push waits.
- **How.** `git status` clean and branch `development`; `git fetch origin`; if `origin/development` has commits local lacks, merge it into local `development` and re-run `verify`; then `git push origin development`. Fast-forward only: no force, no tags, no other branch.
- **Proof.** The ledger records the pushed hash and `git status -sb` showing `development` level with `origin/development`.
- **If it fails** (a refused or disconnected push): record the exact output under "Needs the user", leave `development` as it is, never retry with force. The wave is still delivered.
- **Still the user's:** merging into `main` and deploying. They need their explicit say-so in the message being answered (project branching rule 9). A push of `development` starts the repo's own checks and staging build by itself; that is expected and is not a deploy.

## Never

- Merge into `main`, deploy, force-push, push anything but `development`, run credential scripts or touch production.
- Skip or soften a check because the dev database lacks data. Create the data (`/bandit-dev:testdata create` when the project has a `testdata` section), run the case, remove what you created (`clean`; Test data in `plan.md`). "Not exercised" fails the wave.
- Complete a card, mark one approved, or call anything delivered beyond "awaiting the user's test".
- Run two waves in one chat.
- Move a card to Doing past a gate, or past the five-item cap.
- Move the sprint card before the last card of the last wave is in `standby`, or to anything but `standby`.
- Write to cards outside the batch and the sprint card.
