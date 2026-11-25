# 🤖 The run cycle: every wave, one agent each

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint run {sprint} [{sprint} …]`. It runs every open wave of one or more sprints, each wave in its own subagent, from one orchestrator chat. A subagent is the "new chat" of `execute`: a fresh context that reads the documents and nothing else. Board moves, gates and the wave cycle are `references/execute.md`'s; this file only says how the orchestrator drives them.

Contents: Command · Rules · Before the first wave · The loop · Side by side · Paced mode · Gates the wave agent cannot run · Stop and resume · Notifications · Final report · Never

## Command

`/bandit-dev:sprint run {sprint}` runs every wave not done in its ledger, in plan order, each once the cards it depends on are delivered (`execute.md` → Command, rule 3). `/bandit-dev:sprint run {sprint A} {sprint B}` runs the sprints in the order given, all of the first before any of the second.

1. **Only sprints are accepted.** A batch card is refused, as in `execute`.
2. **Each sprint must be committed**: its ledger's 12 Plan steps done. A sprint still in planning is named and skipped; the others still run.
   - **Review gate.** Step 11 (Independent plan review) not done → that sprint is refused, naming the step.
   - **Order gate.** The sprint is blocked by an open sprint or card (`get_sprints { sprintId }` → `blockedBy`, `completed: false`) → refused, naming it. A blocking sprint named earlier in the same `run` command counts once its last wave is checked.
3. **`--paced [minutes]`** turns on paced mode (below). Without it, waves run back to back.
4. **Running `run` is the approval to execute every wave of the named sprints**, the same approval the execution prompt carries for one wave. It is not the approval to test, debug or close.

## Rules

- **One wave, one agent.** Each wave is executed by one new subagent, except the cards the plan marks side by side, one agent each (Side by side). The orchestrator never implements, never edits code and never reads diffs. It reads the board, the ledgers and the agents' reports; in a side-by-side wave it also makes the working copies and merges the ready branches, nothing else.
- **One wave at a time.** Waves in plan order, sprints in the order given; a wave whose dependencies are delivered runs even while an earlier wave holds a paused or blocked card. Never two waves at once. What this protects: two agents never share a working copy, the trunk or a migration number. Inside one wave, the cards on the plan's `Side by side:` line are built at the same time, each in its own working copy (Side by side).
- **The orchestrator checks every wave before the next starts.** No wave starts on a report alone.
- **The wave agent follows `execute` exactly.** Same rules, same board choreography, same ledger, same stop-lines. Nothing is relaxed because there is no human in the chat.
- **Context stays small.** Agent reports have a fixed short shape (below). Ask for nothing longer.

## Before the first wave

1. Gate 0 from SKILL.md, once.
2. For every sprint: `get_sprints { sprintId }` (each card's `wave`, the `runState`), read the ledger's "At a glance" and its Waves table, which must match the app's waves (a difference is named and stops that sprint). List the waves to run (not done, in order; the debug card's own last wave is not one). A paused sprint whose answer is not in this chat, or a replanning one, is named and skipped (`references/execute.md` → Run state).
3. **Cross-sprint check (only with two or more sprints).** Read each plan's migration numbers and the files each sprint's cards edit. Each sprint was planned alone, so two can claim the same migration number or the same file. Record the clash in each later sprint's ledger under "Plan deviations". The later sprint's waves stop at their migration-tail check until the user approves a corrected Migration tail row in its ledger; nothing renumbers on its own.
4. Opening line: the sprints and waves that will run, in order, and anything skipped with the reason. Then start; do not wait for an answer.

## The loop

For each wave, in order:

1. **Launch one subagent** (the Agent tool, type `general-purpose`) and wait for its result before doing anything else. Its prompt, filled in:

   > You are the execution chat for Wave {n} of Sprint {name} on the {board} board. Working directory: {repo path}. Run `/bandit-dev:sprint execute {name} wave {n}`: read `${CLAUDE_SKILL_DIR}/SKILL.md` and `${CLAUDE_SKILL_DIR}/references/execute.md`, then what `execute.md` → Start lists for a wave and nothing beyond it: the sprint's execution prompt and your wave note `{project}-sprint-{name}-wave-{n}` (through bandit:notes: {where its papers are}), never the whole plan or ledger to begin; follow them exactly for this one wave only. Send every search across several files to a search agent on Haiku at low effort and read directly only the files you are about to change (`execute.md` → The wave, step 4c). Move the cards on the Execution board exactly as `execute.md` → Board moves says: your wave's cards to `doing` while you work them, every later card whose dependencies are all delivered to `next` the moment a card reaches `standby`, cards that depend on an undelivered card left in `assigned`, each finished card to `standby`, and tick each card's build steps as you go (the approval line is never ticked here). Leave no leftovers: archive or delete what you used and no longer need, on proof only. You run unattended: what the Spec, the plan, its Gaps answered by convention block and the project's rules answer, do; a question none of them answers is never decided by you: pause that card as `execute.md` → The wave, step 4a says, and report `NEEDS DECISION` with the question in the user's terms and your recommendation. If you cannot launch the code-reviewer or ui-verifier agents yourself, stop before merging, keep the branch, and report `GATES NEEDED` with the branch name. After your last merge take at most five steps (`execute.md` → Finishing a wave) and do not write the wave's records or launch the records agent: the orchestrator launches it with your WAVE SUMMARY. Report in at most 15 lines, then the WAVE SUMMARY block, in this shape: BOARD at start (the Execution columns of your wave's cards right after you set the board); STATUS (DONE / GATES NEEDED / NEEDS DECISION / BLOCKED); WAVE; CARDS with their column now; BRANCHES and merge commits; VERIFY result on `development`; GATES (review verdict, UI verdict); CONVENTIONS applied from the plan's Gaps answered by convention block (one line each); QUESTION for the user (with NEEDS DECISION); BLOCKER (if any, and what only the user can supply); OPEN CALLS, verbatim; then the WAVE SUMMARY (`execute.md` → Finishing a wave, step 2).

2. **Set the board first, whatever the wave reported** (DONE, BLOCKED, GATES NEEDED, NEEDS DECISION, or no report at all, as when the wave agent was cut off by a usage limit): read the sprint's columns (`execute.md` → Board moves → Reading the board), move every batch card (the debug card is not one: a wave and `run` never move it) to the column `execute.md` → Board moves requires (this wave's delivered cards in `standby`, a paused card left in `doing`, every later card whose dependencies are all delivered in `next`, the rest in `assigned`), read the board back and note any move in the ledger's Milestone log. A move the board refuses, a wave agent cut off and any other step of the run that stalls or fails gets a Process line on the debug card (`references/templates.md` → Debug card, Process lines). Then **launch the records agent** with the wave agent's WAVE SUMMARY, as `execute.md` → Finishing a wave, step 3 says, and wait for its report (a wave agent cut off before its summary: write the summary from the board, `git log` and the cards' Delivered comments, say so in it, and launch it the same way). Only then check the rest.
3. **Check the wave** against live state, not the report:
   - the ledger's Waves row for wave n is done, with its evidence, and every merged card of the wave has its ledger line with its merge commit and its Delivered comment on the card (`execute.md` → The wave, step 5);
   - the sprint's status (`get_sprints { sprintId }`) is `executing` while waves remain (never move it yourself), and `debugging` after the last wave;
   - a paused card (NEEDS DECISION) is not a failed check: put its question to the user; the run goes on with a wave that does not depend on the paused card, and stops when no wave is workable, pausing the sprint in the app with that question as the reason (`references/execute.md` → Run state);
   - the cards the wave worked are in `standby` now, and during the wave they were in `doing`: read the wave agent's report line "BOARD at start" (the columns it showed after setting the board). A card that was worked from `assigned` or `next` is a failed wave: stop;
   - the sprint's columns (`execute.md` → Reading the board) show exactly what `execute.md` → Board moves requires: this wave's cards in `standby` (or Blocked with the reason on the card), every later card whose dependencies are delivered in `next` where the sprint's five-card cap allows, every card that depends on an undelivered card in `assigned` (step 2 already corrected any card in the wrong column);
   - every card of the wave has its build steps ticked, and its approval line still open (the approval line is never ticked here);
   - the ledger's "At a glance" names the next wave, and the wave's migration-tail line (`execute.md` → The wave, step 3) shows the tail matched;
   - the ledger's Status line reads `Wave {n} of {total} delivered…` for this wave: a stale line fails the wave;
   - `git status --short` is clean and `git branch --show-current` is `development`;
   - if the wave carries the final push (`execute.md` → Pushing `development`): the ledger records the pushed hash and `git status -sb` shows `development` level with `origin/development`. A recorded push failure is a "Needs the user" item, not a failed wave.
   - `python3 ${CLAUDE_SKILL_DIR}/scripts/check_sprint.py` prints OK on a notes file built for this check (`references/templates.md` → Notes file).
   Any mismatch: treat the wave as not done and stop (see below).
4. **Add one line to the ledger's Milestone log**: `Run: Wave {n} done by agent, checked ({what was checked}). Next: Wave {n+1}` or the next sprint.
5. Next workable wave. After a sprint's last wave, move on to the next sprint's first open wave.

## Side by side

For a wave whose wave note carries a `Side by side:` line (`references/plan.md` step 6), in place of loop step 1 for those cards; the wave's other cards run as the loop says, after them.

1. **Working copies.** For each card on the line: `git worktree add .claude/worktrees/{card} -b {its branch} {trunk}` in the main checkout, the branch the plan names, cut from the trunk as it is now. The files the project's rules say a working copy needs (its local settings) are copied in; a service the project already runs (a database, a dev server) is shared, never started a second time. Each card to `doing`.
2. **One card agent per card, at the same time** (the Agent tool, type `general-purpose`, in the background). Its prompt is loop step 1's for this one card, plus: "Work only in {working copy}. Never touch the main checkout, the trunk, another card's working copy, the ledger, or a migration number the plan did not give this card. Run the gates in the Gate order; your full check runs once, last, behind the project's one-at-a-time lock, and you write down how long it waited for the lock (the full check's own output). Then report `READY TO MERGE {branch}` with your card's line of the WAVE SUMMARY (`execute.md` → Finishing a wave, step 2, the lock wait added after the full check) and wait for the orchestrator's message." The orchestrator never ends its turn while a card agent runs: it waits for each one's notification.
3. **Merges, one at a time, in the wave's order** (its row in the ledger's Waves table): a card ready before an earlier one waits. The orchestrator merges its branch into the trunk in the main checkout (`git merge --no-ff`, the project's branching rules), writes the card's ledger row right after (the merge commit), and sends the commit to that card agent (SendMessage), which writes its Delivered comment, moves its card to `standby` and ends. A conflict is not fixed by the orchestrator: it tells the card agent to merge the trunk into its branch, run its tests and its full check again, and report ready again; the conflict and its cause go in the ledger's Plan deviations. A merged card's working copy is removed (No leftovers).
4. **Migrations stay one at a time:** the plan puts on the line at most one card that adds a migration, so no number is taken twice. A number taken twice anyway stops the wave: the card is Blocked with the output, and the line goes under Needs the user.
5. **After the last card,** the orchestrator writes the WAVE SUMMARY from the card agents' lines and launches the records agent with it (`execute.md` → Finishing a wave, step 3), then runs loop steps 2 and 3.
6. **The trial.** The first wave run this way is a trial, read in its wave report: `wave_flow.py`'s `Side by side` line (the wave's clock time beside the sum of its cards' times), minutes per card beside the comparison the project's brief names, full checks per card, each card's wait for the full-check lock, and any merge conflict or migration number taken twice, with its cause; the defects the user finds come from the debug card. Side by side is kept only if the wave's clock time is clearly under its cards' sum and the user's test finds no more defects than that comparison; the wave report names the result as an Open call either way, and a plan marks no card side by side again until the user says to keep it.

## Paced mode

For unattended runs (the user asleep). Started as `/loop /bandit-dev:sprint run {sprint} [more] --paced [minutes]`; the gap defaults to 45 minutes. It spreads the work over several plan usage windows instead of spending one in a burst.

- **One wave per wake-up.** Each loop turn runs exactly one wave (the loop above, steps 1 to 4), then calls `ScheduleWakeup` with the gap in seconds (clamped to 60 to 3600) and this same `/loop` prompt, `noop: false`. The next turn re-reads the board and the ledger and runs the next open wave.
- **Nothing left, or a stop condition:** call `ScheduleWakeup` with `stop: true`, send the final notification, write the final report.
- **No usage reading.** Claude Code gives the model no way to read the plan's remaining usage (`/usage` is for the user only), so pacing is by time, not by a token count. Keep each wave lean: run the UI check only when the wave changes something visible, and keep agent reports to their fixed shape.
- **Before starting, tell the user in the opening line** what must be true for an unattended night: the terminal and this session stay open, the computer does not sleep, and "Continue automatically at usage limit" is on in `/config` (otherwise a usage limit stops the run until they act). Do not change their settings; say it and start.
- **A usage limit mid-wave** is survivable: with auto-continue on, the session resumes when the window resets; without it, the user re-runs the same command and `run` resumes from the ledger.

## Gates the wave agent cannot run

Nested agents are documented to work (a subagent can launch its own, up to three layers by default), so the wave agent normally runs code-reviewer and ui-verifier itself. This fallback is only for the case where it reports the Agent tool missing. When a wave agent reports `GATES NEEDED`:

The order is the execution prompt's Gate order (`templates.md`): review and its fixes, then one UI check, then one full check (only when `code_changed.py` says needed), then merge.

1. The orchestrator runs the `code-reviewer` agent on that branch's diff against `development` and sends its blockers to **the same wave agent** (SendMessage to that agent, not a new one), which fixes them. Only once review is closed does it run the `ui-verifier` agent, once, if the wave changed anything visible, briefed with the cards' Acceptance (and, for a card with a `Design:` line, its design handover, found through the `Handover:` line (the design card's, or the build card's own Source without a design card), for one comparison in the same launch, `templates.md` → Execution prompt) and told to write only test data it creates and to remove it: through `/bandit-dev:testdata create` and `clean` when the project has a `testdata` section (Test data in `plan.md`). It keeps only their verdicts and blocker lists, never the full reports.
2. It sends the UI verdict back to the same wave agent, which fixes any UI blocker, commits the cards' notes and status, runs `verify` (`bandit.yaml`) once, last, only when `code_changed.py` says needed, then merges, moves the cards and ticks the wave as `execute` says.
3. Then it sets the board and checks the wave (loop steps 2 and 3) as usual.

## Stop and resume

**Stop the whole run** on: a wave that fails the check, a red `verify` on `development`, or a gate the agent cannot pass after one fix round; and on a `BLOCKED` or `NEEDS DECISION` report once no wave is workable (put the question to the user as it came, in their terms). The current wave stays as it is. A later wave that depends on the held card does not start; one that does not depend on it still runs. Later sprints do not start while any wave of the sprint is open. Report what stopped it and what only the user can supply.

**Resume** is the same command: `run` starts from the first wave not done in each sprint's ledger and skips what is done. After a NEEDS DECISION stop, the user's answer goes into the ledger's Decisions log first (the orchestrator writes it, quoted); the new wave agent reads it at Start and resumes the paused card.

## Notifications

Use `PushNotification` (it reaches the user's phone when Remote Control is connected), one line, under 200 characters, leading with what they would act on. Send one only when: a wave finishes in paced mode (`Sprint w41: wave 1 done, {ids} in Stand By. Next wave in 45 min.`), the run stops (`Sprint w41 stopped at wave 2: migration 0068 clash, needs you.`), or the run ends (`Sprint w41: all waves done, 3 cards await your test.`). Never for routine steps inside a wave.

## No leftovers

**No leftovers.** Before this step ends, anything it used to make something else and no longer needs (a draft, a scratch file, a superseded copy, a test fixture, a temporary branch) is archived or deleted, only on proof that its successor exists (`references/homes.md` → Leftovers). Each wave agent is told this in its prompt; the orchestrator checks it with the checker before the next wave.

## Final report

Ten lines at most per sprint: waves run, cards now in Stand By awaiting the user's test, any question waiting for them (a paused card), every open call of every wave's report in one list, the debug card and how many lines it holds, anything else that needs them, and the paste for the next step: `/bandit-dev:sprint debug {sprint}` once they have tested. `run` never starts `debug` or `close`: both wait for the user's own test.

## Never

- Run two waves at once, two agents in one working copy, on the trunk or on one migration number, or a wave before the previous one is checked, or a wave before the cards it depends on are delivered.
- Implement, review or read diffs in the orchestrator.
- Start `debug` or `close`, complete a card, merge into `main`, deploy or force-push. The orchestrator itself never pushes; the wave agent pushes `development` as `execute.md` says.
- Continue past a stop condition, or tick a wave the check did not confirm.
