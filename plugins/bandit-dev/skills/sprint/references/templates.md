# 🧾 Shapes and filenames

Part of `bandit-dev:sprint`. Frontmatter keys, values, filename rules, YAML style and inbox rules belong to bandit:notes; card sections belong to bandit:tasks. This file only fixes the sprint-specific shapes. A fixed shape is justified because other steps and chats read these records.

Contents: Filenames · The sprint in the app · Step comment · Plan note · Brief change log · Execution prompt · Ledger · Handover cards · Report

## Filenames

`{project}` is the project slug, `{name}` the sprint name in kebab-case. All live in `Projects/{slug}/sprint-{name}/`.

| Record | Filename |
|---|---|
| Plan | `{project}-sprint-{name}-plan.md` |
| Execution prompt | `{project}-sprint-{name}-handover-prompt.md` |
| Ledger | `{project}-sprint-{name}-progress.md` |
| Handover report | `{project}-sprint-{name}-handover-report.md` (created by the execution chat) |
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

The step's row in the ledger's **Plan steps** table: the done date and the evidence, `{what was found and decided, with ids}. {Fix rows applied or open.}` A few lines' worth in one cell; longer findings go in the Milestone log, and the cell names them.

## Plan note

`type: plan`, `status: active`, `sprint` = the sprint's name (bandit:notes conventions, sprint records), `related` = every brief. Body: H1 title; summary line; **Summary** (counts, wave table with reasons); **WBS** (a link to the batch's work breakdown in `planning/` and the wave split it supports); **How every card is executed** (branches, working loop, never-in-parallel, migrations, regenerated artefacts, credentials, live checks create and remove their own test data and never alter existing records, through `/bandit-dev:testdata` when the project has a `testdata` section (Test data in `plan.md`), hard rules, design rules); one section per card (Approach, Tests, Docs, Verify first, Verification table of acceptance against proof); **Migration tail** (the tail the sprint starts from, then one row per wave: the tail it must start from and the numbers it adds; `execute` checks it); **Final push** and **Deployment handover** (`plan.md` step 7); **Cross-card items**; **Items to register**; **Risks and rollback**; **Related**. After approval the plan stays stable; changing facts go in the ledger.

## Brief change log

Each brief ends, before Related, with `## Change log`: one dated entry per planning pass, saying what changed and why (requirements added or removed and the finding behind it, decisions, answered questions, a split). Keep the old wording out of the body; keep the reason in the log.

## Execution prompt

Model: the latest sprint's handover prompt in the project's sprint folder (or its `_archive` mirror once closed), adjusted to the shape below. Copy its structure and replace the sprint content. Required sections: how the user starts or resumes a chat (one paste per wave, `/bandit-dev:sprint execute {sprint} wave {n}`); context (project, folder contents); goal; **read first every session**; authority and stop-lines (including the Test data rule from `plan.md`: live checks and tests create and remove their own data, through `/bandit-dev:testdata create` and `clean` when the project has a `testdata` section, never alter existing records, and a case skipped for lack of data is a failed check; explicit approval to implement; the authorised push of `development` (a reinforced line saying an older "never push" note or memory is superseded), followed by filling the staging handover card (`execute.md` → Pushing `development`), the one card outside the sprint the execution writes; never touch the main branch, deploy, force-push, run credential scripts, touch production, edit the user's verbatim documents or rules, override the Spec lock, write to cards outside the sprint, mark anything complete or approved); autonomy (no questions, conservative reading recorded in the ledger, stop only at a real blocker); the wave cycle (branch, verify-first, implement with tests, gates in order, report section, merge into local development, board comment, ledger; at wave end, mark that wave done in the ledger's Waves table with its evidence); the ledger rules (update after every milestone, etag discipline, resume reconciles repo and ledger); the handover report (per card: what you get, how to test it, how we tested it, limits and decisions, where it lives, if it breaks; then regression list, needs-the-user list, bug log); the final message (ten lines at most, one wave per run); a debug and close section that only points to `references/debug.md` and `references/close.md` (no procedure copied); a wave and card reference table.

The execution prompt must carry the No leftovers rule (`references/homes.md` → Leftovers) in its wave cycle.

## Ledger

Sections: At a glance (sprint, `Sprint record: {name} on {board}` written at step 1 (the line the checker's SP9 and SP10 key on), `Status: {line}`, current wave, next action, last update, report, trunk verified, `Committed: {date}` written at step 12, `Released: {version} · {date} · {commit} · covers {sprints}` written by `release`, or `Release: deferred` written by `close` when it closes with no app release); **Plan steps** (one row per step, the twelve in order: `| {n} | {step} | {done date} | {evidence} |`, the step names exactly as SKILL.md's table, empty date and evidence until done; the date as `YYYY-MM-DD`, the evidence one line with no `|`); **Waves** (from step 12, one row per wave in order: `| Wave {n} | {card ids} | {done date} | {evidence} |`); Gates (one line per thing that blocks the sprint: `Gate: {blocker} delivered ({what it hands over}) before closing the sprint`, written when the link is made, the dependency gate's notice); Batch (selection rule, a table of card, title, lane, effort, complexity, order, blocked by; total effort) and Out of this sprint; Decisions log (dated, the user's decisions, the approval quoted); Waves and cards (wave, card, branch, status, last milestone, commit, review, verify, UI, merged, report section); Milestone log; Verify-first results; Decisions taken without the user; Plan deviations; Needs the user (backup before deploy, production audits, rule corrections awaiting approval, push and deploy decisions, unresolved references); Follow-ups noticed; Bug log. Status values: Not started, In progress (step), Blocked (reason), Delivered awaiting the user's test, Tested by the user. At a glance also carries `Staging handover: {short id}` and `Production handover: {short id}`, written at step 12.

## Handover cards

Two cards per sprint on the `handover.board` board: **staging** in `handover.staging.column`, filled by the Final push (`execute.md` → Pushing `development`), and **production** in `handover.production.column`, filled by `release`. A card hook fires each and the agent reads the prompt from the description, so the shape is fixed: three parts, in this order, nothing else.

1. `<h2>Prompt for the CTO agent</h2>`, then one `<p>` line: "Paste the block below into the CTO chat, or fire the card's hook."
2. One `<pre>` holding the whole prompt. Ready form, in this order: the role line ("Put {app} {version} on production and confirm it is running", or for staging "Put {app} development at {hash} on staging and confirm it is running"); **Facts** (production: tag, commit on `branches.deploy`, build state, image, the migration tail before and after, the backup the user confirmed with its date; staging: the pushed hash on `branches.trunk`, the migration tail, the build it waits for; both: the runbook path and section); **Steps**, one at a time showing each result: read the running version first (already the new one → skip to the checks), then the runbook's deploy, watch and confirm commands copied word for word with the runbook's own never-lines; never print or copy a password, token or env value; **If any step fails**, stop, retry nothing with force, improvise no fix, report the failing command, its output and the old state; **Report** in 8 lines at most: version before and after, commands run, log result, each confirmation, what needs the user.
3. `<h2>Source</h2>`, then one `<p>`: project, sprint name, and the release version and date (production) or the pushed hash and date (staging).

Titles: ready `Deploy {app} {version} (prompt for the CTO agent)` and `Deploy {app} to staging, sprint {name} at {hash} (prompt for the CTO agent)`; not ready `Deploy {app}, sprint {name} (prompt for the CTO agent)` and `Deploy {app} to staging, sprint {name} (prompt for the CTO agent)`. The not-ready `<pre>` holds only: "NOT READY: sprint {name} has not reached this step yet. Run nothing. Report that the card fired before it was filled." Filling replaces the title and the `<pre>`, never the headings.

## Report

Created by the execution chat in the first wave, marked draft, finished after the last wave. Per-card structure in the execution prompt.
