# 🤖 The run cycle: every wave, one agent each

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint run {sprint card} [{sprint card} …]`. It runs every open wave of one or more sprints, each wave in its own subagent, from one orchestrator chat. A subagent is the "new chat" of `execute`: a fresh context that reads the documents and nothing else. Board moves, gates and the wave cycle are `references/execute.md`'s; this file only says how the orchestrator drives them.

Contents: Command · Rules · Before the first wave · The loop · Paced mode · Gates the wave agent cannot run · Stop and resume · Notifications · Final report · Never

## Command

`/bandit-dev:sprint run {sprint card}` runs every unticked wave of that sprint, in order. `/bandit-dev:sprint run {card A} {card B}` runs the sprints in the order given, all of the first before any of the second.

1. **Only sprint cards are accepted** (cards carrying `Wave n:` sub-tasks). A batch card is refused, as in `execute`.
2. **Each sprint must be committed**: its 11 step sub-tasks ticked. A sprint still in planning is named and skipped; the others still run.
3. **`--paced [minutes]`** turns on paced mode (below). Without it, waves run back to back.
4. **Running `run` is the approval to execute every wave of the named sprints**, the same approval the execution prompt carries for one wave. It is not the approval to test, debug or close.

## Rules

- **One wave, one agent.** Each wave is executed by one new subagent. The orchestrator never implements, never edits code and never reads diffs. It reads the board, the ledgers and the agents' reports.
- **Strictly in sequence.** One wave at a time, waves in order, sprints in the order given. Never two wave agents at once: they share one working tree, the local `development` branch and the migration numbers, so parallel waves would collide.
- **The orchestrator checks every wave before the next starts.** No wave starts on a report alone.
- **The wave agent follows `execute` exactly.** Same rules, same board choreography, same ledger, same stop-lines. Nothing is relaxed because there is no human in the chat.
- **Context stays small.** Agent reports have a fixed short shape (below). Ask for nothing longer.

## Before the first wave

1. Gate 0 from SKILL.md, once.
2. For every sprint: `get_task` on the sprint card, read the ledger's "At a glance" and the wave sub-tasks. List the waves to run (unticked ones, in order).
3. **Cross-sprint check (only with two or more sprints).** Read each plan's migration numbers and the files each sprint's cards edit. Each sprint was planned alone, so two can claim the same migration number or the same file. Record the clash in each later sprint's ledger under "Plan deviations": the later sprint takes the next free migration number at build time and builds on what the earlier one merged.
4. Opening line: the sprints and waves that will run, in order, and anything skipped with the reason. Then start; do not wait for an answer.

## The loop

For each wave, in order:

1. **Launch one subagent** (the Agent tool, type `general-purpose`) and wait for its result before doing anything else. Its prompt, filled in:

   > You are the execution chat for Wave {n} of Sprint {name}, sprint card {card}, on the {project} board. Working directory: {repo path}. Run `/bandit-dev:sprint execute {card} wave {n}`: read `${CLAUDE_SKILL_DIR}/SKILL.md` and `${CLAUDE_SKILL_DIR}/references/execute.md`, then the handover prompt in the sprint folder ({folder}), and follow them exactly for this one wave only. Move the cards on the Execution board exactly as `execute.md` → Board moves says: your wave's cards to `doing` while you work them, the next wave's to `next`, later waves left in `assigned`, each finished card to `standby`, and tick each card's sub-tasks as you go. Leave no leftovers: archive or delete what you used and no longer need, on proof only. You run unattended: do not ask questions; take the conservative reading and record it in the ledger, as the handover prompt says. If you cannot launch the code-reviewer or ui-verifier agents yourself, stop before merging, keep the branch, and report `GATES NEEDED` with the branch name. Report in at most 15 lines, in this shape: BOARD at start (the Execution columns of your wave's cards right after you set the board, and any refused move to Doing with the blocker); STATUS (DONE / GATES NEEDED / BLOCKED); WAVE; CARDS with their column now; BRANCHES and merge commits; VERIFY result on `development`; GATES (review verdict, UI verdict); DECISIONS taken without the user (one line each); BLOCKER (if any, and what only the user can supply).

2. **Check the wave** against live state, not the report:
   - the sprint card's `Wave n` sub-task is ticked;
   - the sprint card has not moved while waves remain (never move it yourself before then), and after the last wave it is in `standby`;
   - the cards the wave worked are in `standby` now, and during the wave they were in `doing`: read the wave agent's report line "BOARD at start" (the columns it showed after setting the board). A card that was worked from `assigned` or `next` without a recorded refusal (`Could not move to Doing:` comment on the card) is a failed wave: stop. A recorded refusal is not a failure;
   - the Execution board (`get_execution_board`) shows exactly what `execute.md` → Board moves requires: this wave's cards in `standby` (or Blocked with the reason on the card), the next wave's cards in `next` where the gates and the five-card cap allow (a card chained behind a batch card in `standby` is refused `doing` by the board until the app lets `standby` count, so it may legitimately still be in `next` with its recorded refusal comment), every later wave's cards in `assigned`. A card in the wrong column is moved to the right one by the orchestrator (the only board write it makes) and noted in the sprint card comment;
   - every card of the wave has its sub-tasks ticked;
   - the ledger's "At a glance" names the next wave;
   - `git status --short` is clean and `git branch --show-current` is `development`;
   - if the wave carries the final push (`execute.md` → Pushing `development`): the ledger records the pushed hash and `git status -sb` shows `development` level with `origin/development`. A recorded push failure is a "Needs the user" item, not a failed wave.
   - `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` prints OK.
   Any mismatch: treat the wave as not done and stop (see below).
3. **Post one comment on the sprint card**: `Run: Wave {n} done by agent, checked ({what was checked}). Next: Wave {n+1}` or the next sprint.
4. Next wave. After a sprint's last wave, move on to the next sprint's first open wave.

## Paced mode

For unattended runs (Leo asleep). Started as `/loop /bandit-dev:sprint run {sprint card} [more] --paced [minutes]`; the gap defaults to 45 minutes. It spreads the work over several plan usage windows instead of spending one in a burst.

- **One wave per wake-up.** Each loop turn runs exactly one wave (the loop above, steps 1 to 3), then calls `ScheduleWakeup` with the gap in seconds (clamped to 60 to 3600) and this same `/loop` prompt, `noop: false`. The next turn re-reads the board and the ledger and runs the next open wave.
- **Nothing left, or a stop condition:** call `ScheduleWakeup` with `stop: true`, send the final notification, write the final report.
- **No usage reading.** Claude Code gives the model no way to read the plan's remaining usage (`/usage` is for Leo only), so pacing is by time, not by a token count. Keep each wave lean: run the UI check only when the wave changes something visible, and keep agent reports to their fixed shape.
- **Before starting, tell Leo in the opening line** what must be true for an unattended night: the terminal and this session stay open, the computer does not sleep, and "Continue automatically at usage limit" is on in `/config` (otherwise a usage limit stops the run until he acts). Do not change his settings; say it and start.
- **A usage limit mid-wave** is survivable: with auto-continue on, the session resumes when the window resets; without it, Leo re-runs the same command and `run` resumes from the ledger.

## Gates the wave agent cannot run

Nested agents are documented to work (a subagent can launch its own, up to three layers by default), so the wave agent normally runs code-reviewer and ui-verifier itself. This fallback is only for the case where it reports the Agent tool missing. When a wave agent reports `GATES NEEDED`:

1. The orchestrator runs the `code-reviewer` agent on that branch's diff against `development`, then the `ui-verifier` agent if the wave changed anything visible, briefed with the cards' Acceptance and told to write only test data it creates and to remove it. It keeps only their verdicts and blocker lists, never the full reports.
2. It sends the verdicts back to **the same wave agent** (SendMessage to that agent, not a new one), which fixes the blockers, re-runs `verify` (`bandit.yaml`), merges, moves the cards and ticks the wave as `execute` says.
3. Then it checks the wave (loop step 2) as usual.

## Stop and resume

**Stop the whole run** on: a `BLOCKED` report, a wave that fails the check, a red `verify` on `development`, or a gate the agent cannot pass after one fix round. The current wave stays as it is. Later waves and later sprints do not start. Report what stopped it and what only Leo can supply.

**Resume** is the same command: `run` starts from the first unticked wave of each sprint and skips what is done.

## Notifications

Use `PushNotification` (it reaches Leo's phone when Remote Control is connected), one line, under 200 characters, leading with what he would act on. Send one only when: a wave finishes in paced mode (`Sprint w41: wave 1 done, {ids} in Stand By. Next wave in 45 min.`), the run stops (`Sprint w41 stopped at wave 2: migration 0068 clash, needs you.`), or the run ends (`Sprint w41: all waves done, 3 cards await your test.`). Never for routine steps inside a wave.

## No leftovers

**No leftovers.** Before this step ends, anything it used to make something else and no longer needs (a draft, a scratch file, a superseded copy, a test fixture, a temporary branch) is archived or deleted, only on proof that its successor exists (SKILL.md, Leftovers). Each wave agent is told this in its prompt; the orchestrator checks it with the checker before the next wave.

## Final report

Ten lines at most per sprint: waves run, cards now in Stand By awaiting Leo's test, decisions taken without him (pointing to the ledger), anything that needs him, and the paste for the next step: `/bandit-dev:sprint debug {card}` once he has tested. `run` never starts `debug` or `close`: both wait for Leo's own test.

## Never

- Run two wave agents at once, or a wave before the previous one is checked.
- Implement, review or read diffs in the orchestrator.
- Start `debug` or `close`, complete a card, merge into `main`, deploy or force-push. The orchestrator itself never pushes; the wave agent pushes `development` as `execute.md` says.
- Continue past a stop condition, or tick a wave the check did not confirm.
