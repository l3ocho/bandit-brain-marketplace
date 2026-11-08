# 🧾 Shapes and filenames

Part of `bandit-dev:sprint`. Frontmatter keys, values, filename rules, YAML style and inbox rules belong to bandit:notes; card sections belong to bandit:tasks. This file only fixes the sprint-specific shapes. A fixed shape is justified because other steps and chats read these records.

Contents: Filenames · The sprint in the app · Step comment · Plan note · Brief change log · Execution prompt · Ledger · Wave report · Sprint map · Debug card · Handover cards · Report

## Filenames

`{project}` is the project slug, `{name}` the sprint name in kebab-case. All live in `Projects/{slug}/sprint-{name}/`.

| Record | Filename |
|---|---|
| Plan | `{project}-sprint-{name}-plan.md` |
| Execution prompt | `{project}-sprint-{name}-handover-prompt.md` |
| Ledger | `{project}-sprint-{name}-progress.md` |
| Handover report | `{project}-sprint-{name}-handover-report.md` (created by the execution chat) |
| Wave report | `{project}-sprint-{name}-wave-report.md` (rebuilt at the end of every wave, Wave report below) |
| Sprint map | `{project}-sprint-{name}-map.html` (drawn at plan step 12, redrawn at the end of every wave, Sprint map below) |
| Review record | `{project}-review-sprint-{name}-YYYY-MM-DD.md` (`type: log`, written at step 11 from the `plan-reviewer` agent's report) |
| Briefs | one per card, bandit:notes brief naming, filed into the folder |

## The sprint in the app

One sprint on the home board (`manage_sprints`, bandit:tasks `references/board.md` → Tags): `name` =
`{name}`, `expectedDate` = the sprint date, `papersUrl` = the sprint folder's path
(`MyNotes/{D}/Projects/{slug}/sprint-{name}/`), its cards = the batch in run order (wave order, then
the plan's order inside a wave). Status: Planning at step 1, Ready to execute at step 12, then
`references/execute.md` → Sprint status. Nothing else is stored in the app: goal, batch table, order,
cross-card notes, risks and decisions live in the plan and the ledger. An old-way sprint's sprint card:
`references/old-way.md`.

## Step comment

The step's row in the ledger's **Plan steps** table: the done date and the evidence, `{what was found and decided, with ids}. {Fix rows applied or open.}` A few lines' worth in one cell; longer findings go in the Milestone log, and the cell names them. Step 9's cell also holds each Batch card's build-step count, `{card id}: {n} steps` (planning's sub-tasks; `Gate:` lines and the approval line not counted); the checker's SP13 reads it.

## Plan note

`type: plan`, `status: active`, `sprint` = the sprint's name (bandit:notes conventions, sprint records), `related` = every brief. Body: H1 title; summary line; **Summary** (counts, wave table with reasons); **WBS** (a link to the batch's work breakdown in `planning/` and the wave split it supports); **How every card is executed** (branches, working loop, never-in-parallel, migrations, regenerated artefacts, credentials, live checks create and remove their own test data and never alter existing records, through `/bandit-dev:testdata` when the project has a `testdata` section (Test data in `plan.md`), hard rules, design rules); one section per card (Approach, Tests, Docs, Verify first, Verification table of acceptance against proof; a card with a `Design:` line adds the row "matches the design handover", naming the screen sizes to compare); **Migration tail** (the tail the sprint starts from, then one row per wave: the tail it must start from and the numbers it adds; `execute` checks it); **Final push** and **Deployment handover** (`plan.md` step 7); **Cross-card items**; **Gaps answered by convention** (one line per gap: card, gap, the convention that answered it); **Items to register**; **Risks and rollback**; **Related**. After approval the plan stays stable; changing facts go in the ledger.

## Brief change log

Each brief ends, before Related, with `## Change log`: one dated entry per planning pass, saying what changed and why (requirements added or removed and the finding behind it, decisions, answered questions, a split). Keep the old wording out of the body; keep the reason in the log.

## Execution prompt

Model: the latest sprint's handover prompt in the project's sprint folder (or its `_archive` mirror once closed), adjusted to the shape below. Copy its structure and replace the sprint content. Required sections: how the user starts or resumes a chat (one paste per wave, `/bandit-dev:sprint execute {sprint} wave {n}`); context (project, folder contents); goal; **read first every session**; authority and stop-lines (including the Test data rule from `plan.md`: live checks and tests create and remove their own data, through `/bandit-dev:testdata create` and `clean` when the project has a `testdata` section, never alter existing records, and a case skipped for lack of data is a failed check; explicit approval to implement; the authorised push of `development` (a reinforced line saying an older "never push" note or memory is superseded), followed by filling the staging handover card (`execute.md` → Pushing `development`), the one card outside the sprint the execution writes; never touch the main branch, deploy, force-push, run credential scripts, touch production, edit the user's verbatim documents or rules, override the Spec lock, write to cards outside the sprint, mark anything complete or approved); autonomy (no questions about what the Spec, the plan, its Gaps answered by convention block or the project's rules already answer; a gap none of them answers stops that card: `Paused: {reason}` in the ledger's Status line and Needs the user, and one plain question to the user with a recommendation (`execute.md` → Needs a decision); hard blockers stop the wave as before); the wave cycle (branch, verify-first, implement with tests, gates in order, report section, merge into local development, board comment, ledger; at wave end, mark that wave done in the ledger's Waves table with its evidence); the ledger rules (update after every milestone, etag discipline, resume reconciles repo and ledger); the handover report (per card: what you get, how to test it, how we tested it, limits and the conventions applied, where it lives, if it breaks; then regression list, needs-the-user list, bug log); the final message (ten lines at most, one wave per run); a debug and close section that only points to `references/debug.md` and `references/close.md` (no procedure copied); a wave and card reference table.

The execution prompt must carry the No leftovers rule (`references/homes.md` → Leftovers) in its wave cycle, and in it the design comparison: for a card with a `Design:` line, the UI check's brief names the design handover and asks for one comparison inside the same UI-check launch, after the screen passes its working checks (layout, the handover's maps and recorded decisions, at the screen sizes the handover covers); the result goes in the card's report section as "matches the design handover" or one line per difference with the handover line it breaks, and a difference left in is Different in the wave report; a card with no `Design:` line gets no comparison. The wave cycle also carries two marks the wave report counts on: each card starts with the shell command `echo CARD-START {card}`, and a code review run in the background is briefed with the commit to read and reads that commit's files (`git show {commit}:{path}`), never the working copy.

**Gate order.** The wave cycle's gates section carries these lines word for word, so each card goes through each gate once:

> Per card, in this order: code review and every fix first; then one browser check (when UI changed); then one full check, last, after the card's notes and status are committed; then merge. A browser check never starts while code review is still open.
> After the merge, the trunk check counts as done when the project's full check prints "already passed": no second full run when only notes changed.

## Ledger

Sections: At a glance (sprint, `Sprint record: {name} on {board}` written at step 1 (the line the checker's SP9 and SP10 key on), `Status: {line}`, current wave, next action, last update, report, trunk verified, `Committed: {date}` written at step 12, `Released: {version} · {date} · {commit} · covers {sprints}` written by `release`, or `Release: deferred` written by `close` when it closes with no app release); **Plan steps** (one row per step, the twelve in order: `| {n} | {step} | {done date} | {evidence} |`, the step names exactly as SKILL.md's table, empty date and evidence until done; the date as `YYYY-MM-DD`, the evidence one line with no `|`); **Waves** (from step 12, one row per wave in order: `| Wave {n} | {card ids} | {done date} | {evidence} |`); Gates (one line per thing that blocks the sprint: `Gate: {blocker} delivered ({what it hands over}) before closing the sprint`, written when the link is made, the dependency gate's notice); Batch (selection rule, a table of card, title, lane, effort, complexity, order, blocked by; total effort) and Out of this sprint; Decisions log (dated, the user's decisions, the approval quoted); Waves and cards (wave, card, branch, status, last milestone, commit, review, verify, UI, merged, report section); Milestone log; Verify-first results; Conventions applied (each gap execution met that the plan's Gaps answered by convention block covered, with the block's line; never a decision of the executor's own); Plan deviations; Needs the user (backup before deploy, production audits, rule corrections awaiting approval, push and deploy decisions, unresolved references); Follow-ups noticed; Bug log. Status values: Not started, In progress (step), Paused ({reason}, awaiting the user's decision), Blocked (reason), Delivered awaiting the user's test, Tested by the user. At a glance also carries `Debug card: {short id}` (written at step 12), `Staging handover: {short id}`, and `Production handover: {short id}` when the recipe names a production card, written at step 12.

## Wave report

One note per sprint, written for the user, rebuilt by the wave agent at the end of every wave (`execute.md` → Finishing a wave): what each card delivered, what came out different and why, the calls waiting for the user, how the work flowed and where the tokens went, all measured from the chat logs, and the lessons later plans read. Read through WebDAV with its etag, rebuilt, written back with `if_match`; never the local synced copy. Frontmatter: `type: reference`, `sprint`, `related` = the ledger and the handover report.

Shape, in this order (an empty section is left out, Open calls says "None."):

- `# Sprint {name} — wave report (after wave {n})`
- `## 🙋 Open calls`: `- {card}: {the question, in app terms}. Recommend: {choice}, because {reason}. (wave {n})`. A workflow or settings lesson that reaches seen 2× is listed here too as a proposed change: Today · What changes for you · What working part it touches · Recommend.
- `## ✔️ Decided`: `- {card}: {the question} → {the user's answer, quoted}, {date}.`
- `## ⏱️ Flow trend`: `| Wave | Cards | Time | Full checks | Test runs | Gate rounds | Repeat runs | Tokens | Peak context |`, one row per wave.
- `## 📚 Lessons`: `### {short name} · seen {k}× · waves {list}`, then `- When:` (a trigger a future card can be matched on: area, kind of change) · `- Risk:` · `- Do:` (a line a plan or brief can carry; for workflow or settings, the helper rule, project rule or setting to change) · `- Use at:` (plan, brief, execution, review, workflow or settings).
- `## 🌊 Wave {n} — {date}`, then per card `### {card} {title} — ✅ As specified | ⚠️ Different | ⏸ Paused`, with only the lines that apply: `- Different: {what} — Why: {reason}` · `- Issue: {what} — Cause: {cause} — Decision: {decision} — You'll see: {impact, or "nothing"}` · `- Your call: {question}` (also in Open calls). Then `#### ⏱️ Flow` and `#### 🪙 Tokens`, pasted from `python3 ${CLAUDE_SKILL_DIR}/scripts/wave_flow.py --since {the wave's first step} --test {the project's test command}` (the script names what it counts and prints "not measured" for what the logs cannot show).

Rules:

1. Rebuild only Open calls, Decided, Flow trend, Lessons and, once debug ends, Debug. Earlier wave sections are copied as they are, never reworded; this wave's section goes at the bottom; a rerun for the same wave replaces only its own section. An earlier section missing its Flow or Tokens block gets it, measured from that wave's logs, and its trend row completed: the only change allowed there.
2. A card delivered as specified with no issue is its heading line alone.
3. Different = anything not as its Spec and Acceptance say, a default applied by convention that changes what the user sees included. Issue = only what cost a fix, a retry, a decision or a deviation. Your call = only a choice the user could reasonably want the other way and that is still reversible, never what the Spec decided.
4. Lesson = only what can happen again on another card; a one-off bug stays an issue. Same lesson again: merge it, bump seen, add the wave. A Flow number showing avoidable time (repeat runs, a full check where a targeted test was enough, extra gate rounds) is a workflow lesson; a Tokens number showing avoidable use (a chat grown far past its start, repeated large outputs, extra UI rounds, a large start context) is a workflow or settings lesson.
5. Open calls the user answered, in chat or on a card, move to Decided with their words and date.
6. Facts only, from this chat, the ledger, each card's Spec and comments, the gate verdicts, the wave's commits and the script's output. App terms, one idea per line, no preamble, no filler. Numbers never from memory; a number not measured is written "not measured", never estimated.
7. Touch nothing else while writing it: no code, ledger, cards or other notes.

## Sprint map

Temporary (decisions RS16): one HTML page per sprint, a live picture of the sprint for the user. `python3 ${CLAUDE_SKILL_DIR}/scripts/sprint_map.py {data.json} --out {page}` draws it; the page goes to the sprint folder through WebDAV (a new file, then the etag on each redraw). The data file is built fresh each time and never stored: `sprint`, `project`, `due` (the sprint date), `effort`, optional `headline` and `lede`; `cards` from the sprint's run order, each with `id`, `title`, `area` (its board column), `wave` (from the ledger's Waves table; a card in no wave is left out), `step` (its run number), `size` (effort and complexity), `state` (delivered when in Stand By or Done, doing, paused, or waiting), `db` (the card adds a migration, from the plan's Migration tail) and `gets` (the first sentence of its Outcome); `links` = the blocker links between sprint cards (`get_task` → `blockedBy`); `after` = the plan's "lands after" pairs from Cross-card items, empty when it names none. The road after the last wave comes from the recipe. Nothing is placed by hand: the script routes the arrows.

## Debug card

One card per sprint, the single shared list of what to fix in debug, assigned to the user, in the sprint and in no wave. Title `Debug: sprint {name}`. Description: one `<p>` saying "One line per issue. Claude adds what a wave could not solve; add what you find, or tell Claude and it adds it." and the two line shapes below.

- **Line shapes** (checklist lines, one idea each, no codes, details in a comment): `Expected: {screen} › {part} — {what is wrong, in app terms} ({card})` for one Claude raises; `Found: {screen} › {part} — {what is wrong} ({card})` for one the user finds. `{screen} › {part}` is the area as the user sees it; `{card}` is the sprint card it belongs to, or `new`.
- **Outcomes:** a fixed line is ticked; a declined one ends `(declined: {reason})` and is ticked; one that is new work ends `(new card {id})` and is ticked.
- **Wave report, Debug section** (written when debug ends, after Lessons; rebuilt like Open calls and Lessons, rule 1; SP11 does not read it): `## 🐞 Debug`, then `| Card | Expected | Found | Fixed | Declined | New card |`, one row per card and a total row, counted from the card's lines. A card kind that keeps producing Found lines is a lesson.

## Approval line

The one home of this rule. Every batch card of a sprint planned with this rule ends with one sub-task titled exactly `Tested and approved by you`, **last**, after the build steps and any `Gate:` lines, open. It shows that a card whose build steps are all ticked still waits for the user. Only `close` ticks it, once per card the user approved in that chat, with the approval quoted in the ledger (`close.md` → Steps); a wave, `run` and `debug` never do. `close` completes no card whose approval line is open. Not a tag, not a feature of the app: the app lets a card be completed with open sub-tasks, so the helpers hold the line. The debug card has none. A card from a sprint planned before this rule has no such line and closes as before; an old-way sprint keeps its own flow (`old-way.md`).

## Handover cards

Up to two cards per sprint on the `handover.board` board: **staging** in `handover.staging.column`, filled by the Final push (`execute.md` → Pushing `development`), and **production** in `handover.production.column`, filled by `release`, only when the recipe names `handover.production` (without it, `release` runs the deploy itself through the recipe's steps). A card hook fires each and the agent reads the prompt from the description, so the shape is fixed: three parts, in this order, nothing else.

1. `<h2>Prompt for the CTO agent</h2>`, then one `<p>` line: "Paste the block below into the CTO chat, or fire the card's hook."
2. One `<pre>` holding the whole prompt. Ready form, in this order: the role line ("Put {app} {version} on production and confirm it is running", or for staging "Put {app} development at {hash} on staging and confirm it is running"); **Facts** (production: tag, commit on `branches.deploy`, build state, image, the migration tail before and after, the backup the user confirmed with its date; staging: the pushed hash on `branches.trunk`, the migration tail, the build it waits for; both: the runbook path and section); **Steps**, one at a time showing each result: read the running version first (already the new one → skip to the checks), then the runbook's deploy, watch and confirm commands copied word for word with the runbook's own never-lines; never print or copy a password, token or env value; **If any step fails**, stop, retry nothing with force, improvise no fix, report the failing command, its output and the old state; **Report** in 8 lines at most: version before and after, commands run, log result, each confirmation, what needs the user.
3. `<h2>Source</h2>`, then one `<p>`: project, sprint name, and the release version and date (production) or the pushed hash and date (staging).

Titles: ready `Deploy {app} {version} (prompt for the CTO agent)` and `Deploy {app} to staging, sprint {name} at {hash} (prompt for the CTO agent)`; not ready `Deploy {app}, sprint {name} (prompt for the CTO agent)` and `Deploy {app} to staging, sprint {name} (prompt for the CTO agent)`. The not-ready `<pre>` holds only: "NOT READY: sprint {name} has not reached this step yet. Run nothing. Report that the card fired before it was filled." Filling replaces the title and the `<pre>`, never the headings.

## Report

Created by the execution chat in the first wave, marked draft, finished after the last wave. Per-card structure in the execution prompt.
