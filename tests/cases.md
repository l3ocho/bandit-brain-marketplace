# 🧪 Test cases: pipeline and inbox behaviour

> One case per behaviour built in sprint marketplace-v1 (BB-133), each written as input → expected refusal or result. Run in W7 from `.work/test/` against staging, and again after any change to these behaviours.

**How:** `auto` cases are code and run in `python3 scripts/check_repo.py` (rule named). `cli` cases run a
plugin in a headless session from `.work/test/`:
`claude -p --plugin-dir ../../plugins/bandit --plugin-dir ../../plugins/bandit-dev "<prompt>"`, against
the `bandit-staging` board only. `read` cases are checked by reading the shipped text.

## 🏃 Sprint (`bandit-dev:sprint`)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C1 | bandit.yaml contract | auto (Y1) | `recipe.py require …` on `tests/fixture-app/bandit.yaml` | exit 0, every key the sprint skill reads is present |
| C2 | bandit.yaml contract | auto (Y1) | `recipe.py --file bandit.missing-key.yaml check-tail 0002` | exit 3, refusal names ``missing key `migrations.check` `` |
| C3 | P3 migration tail | auto (Y1) | `recipe.py check-tail 0003` on the fixture (tail is 0002) | exit 4, "migration tail is 0002, the plan names 0003: stop the wave" |
| C4 | P3 migration tail | auto (Y1) | `recipe.py check-tail 0002` | exit 0, "matches the plan" |
| C34 | Optional sections | auto (Y1) | `recipe.py --file bandit.no-migrations.yaml tail`, `check-tail none`, `opt staging.refresh` | exit 0; prints `none`; matches |
| C35 | Hook with no vault | auto (SP8) | `check_sprint.py --hook` with no `MYNOTES_DIR` and no `~/Documents/MyNotes`, the repository's Project Context naming `home-reno`, the Bad notes file in its `.sprint/`; then the file missing, then built before the session, then a chat naming neither the sprint helper nor the notes file | exit 2 with SP7; exit 0 with a notice that it could not read the notes file; exit 0 with a notice that it was built before the session (its SP7 named, not blocking); exit 0, silent |
| C5 | P1 SP7 | auto (SP7) | `check_sprint.py --notes tests/fixture-notes/Bad/home-reno-sprint-notes.json` (committed, no review record) | exit 1, exactly one error, SP7 |
| C6 | P1 SP7 | auto (SP7) | `check_sprint.py --notes tests/fixture-notes/Good/…` (committed, review record present) | exit 0, "passes the sprint rules" |
| C7 | P1 review gate | cli | `run` on a staging sprint card whose step 11 sub-task is unticked | refused, names "Independent plan review" (step 11); no wave agent launched |
| C8 | P3 order gate | cli | `run` on a staging sprint card blocked by an open sprint card | refused, names the blocking sprint card; no wave agent launched |
| C9 | P3 order at plan | read | `references/plan.md` step 4 (Sprint order) | the new sprint card is blocked by the previous open sprint card (`link_tasks { blockerTaskId, blockedTaskId }`) |
| C10 | P2 release preconditions | cli | `release` on a staging sprint card with an untested card and no deploy word | refused; names the untested card and the missing deploy word; no recipe step runs |
| C11 | P2 close precondition | read | `references/close.md` precondition 4 | no `Released:` line: close writes `Release: deferred`, adds one Milestone log line and says so; a sprint with Marketplace cards and no plugin version released is refused with the paste for `release` (BB-258) |
| C12 | P2 debug push | read | `references/debug.md` Rules | pushes follow `execute.md` → Pushing; no "never push" |
| C13 | P7 status line | read | `references/run.md` loop step 2 | a stale sprint card Status line fails the wave |
| C14 | P1 agent | read | `plugins/bandit-dev/agents/plan-reviewer.md` | read-only tools (Read, Glob, Grep); findings table with severity; blockers carry a recommendation |

## 🧪 Test data (`bandit-dev:testdata`, BB-165)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C36 | Recipe section | auto (TD1) | `recipe.py opt testdata.databases` on the fixture; `opt testdata.logic` on `bandit.no-migrations.yaml`; `dbguard.py check` on `bandit.testdata-missing-key.yaml` | the three databases listed; `none`; exit 3 naming `testdata.logic` |
| C37 | Only test databases | auto (TD1) | `dbguard.py check production`; `check test` on `bandit.testdata-unsafe.yaml` | exit 6, "not a test database"; exit 6, "lists production" |
| C38 | No credentials | auto (TD1) | `check` on `bandit.testdata-secret.yaml`; `check development` with the env var unset; every case with the env var set | exit 6 without printing the command; exit 6 naming the variable only; the value never printed |
| C39 | Create writes only new rows | auto (TD1) | `create` with an UPDATE; with an INSERT lacking `RETURNING 'testdata'`; `read` with a psql meta-command | exit 6 each, nothing run |
| C40 | Staging asks every run | auto (TD1) | `create staging` without `--yes` | exit 6, "asks the user's yes" |
| C41 | Clean removes only the record | auto (TD1) | `create development` (two rows), `clean development card c1 --dry-run`, `clean`, `records` | deletes name exactly the two recorded ids, children first; "none left"; no open record |
| C42 | Real database | cli | `.work/test/testdata/`: a throwaway `postgres:18` container, the fixture schema, one existing row; `create` a made-up team, a rule-breaking insert, `clean` | rows created and recorded; the broken insert keeps nothing; after `clean` only the existing row is left (run 2026-10-15) |
| C43 | Map, fill, make on the app | cli | Bandit Brain with a `testdata` section: `map`, `fill development`, `make` on a sprint's cards, `create`, `clean` | the map lists tables, rules with `file:line` and each card's tables; a made-up user sees made-up data on every page; each acceptance line has its data; `clean` leaves no row |
| C44 | Sprint hook | read | `sprint/references/plan.md` → Test data; `execute.md` → Never | planning runs `make` per live check and names the data; the wave runs `create` before and `clean` after |

## 🗂️ Tasks (`bandit:tasks`)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C15 | G1 leave the inbox | cli | `triage` on a staging project with one parked card | asks description, priority, effort, complexity, assignee, column, and the **due date last** |
| C16 | G1 exit style | cli | `triage` on a staging domain's ` - wkflw` board and on another board | ` - wkflw`: daily sweep (every card leaves today); any other board, whatever its profile: the evaluation gate (yes / not yet / no) |
| C17 | P8 dev offer | read | `references/triage.md` → Dev projects | a parked dev item is offered `/bandit:clarify` (fuzzy) or `/bandit:tasks spec` (clear) |
| C18 | P8 Clarified Specification | read | `references/dev-workflow.md` → spec step 1 | a Clarified Specification maps into the Spec; `Source: clarify, {date}` |
| C19 | P8 audit row | read | `references/audit.md` check 2 | untriaged parked cards come back as one fix row per project |
| C20 | G4 structure | cli | `audit` on a staging project with a column named like a member | a fix row: make it a lane for that person (tag, lane, re-file, delete the empty column on confirm) |
| C105 | Today in rank order | staging | `today` with a blocked card and an unsized card among the columns | inside each board of each column, cards by the app's rank, higher first, each with its Size, band and Rank; then the blocked card naming its blocker; then the unsized card saying it has no size; the rank values the app returned recorded beside the order (BB-527) |
| C106 | Triage of a split-band card | staging | `triage` with a parked card the app bands `split` | a split proposed, nothing split without a yes; a `big` card gets no split proposal (BB-527) |
| C107 | Triage of an unsized card | staging | `triage` with a parked card with no effort or complexity | an effort and a complexity proposed; nothing written without a yes (BB-527) |
| C108 | No figure of Claude's own | read + staging | every Size, band and Rank in C105 to C107 against the app's reads | each shown figure is one the app returned; no total, average or Size worked out (BB-527) |

### 🗃️ Inbox groups (BB-338)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C87 | Groups seen | cli | a group made in the staging app with two cards in a board's Inbox, then `triage` | both cards counted and listed under the group's name, then the loose cards |
| C88 | Dump into one group | cli | `capture` a three-line brain dump, no group named | one new group `Brain dump {date}` in the landing column, the three cards in it in the typed order, titles unchanged; the Inbox page shows them in that group |
| C89 | Named group | cli | `capture` one card "into Groceries" with a Groceries group in that column; then with none | first: filed into the existing group; second: the group is made, then the card filed into it |
| C90 | Group delete asks | cli | `triage`, ask to delete a group holding two cards | asks first, naming two cards; nothing deleted before the yes |
| C91 | Grouped Untriaged count | read | `audit.md` check 1, `triage.md` → What the Inbox board is | the count adds every group's `items` to the loose `items` |
| C95 | Pre-sprint report | auto (ES1) + read | `plan.md` step 12 and its final message on a project with 5 or more timed waves | the map shows each wave's estimate and range and the sprint total; the final message names the map first; fewer than 5 timed waves: "no estimate yet" (BB-402) |
| C96 | Closed sprints left behind | auto (SP15) + read | `plan.md` step 1 on a project with a sprint closed in the app whose papers are not archived, no synced vault | the check on a fresh notes file fails; one archive proposal comes before planning goes on; "could not read the notes file" never passes (BB-494, BB-601) |
| C97 | Release order | auto (RG1) | `release_guard.py` on a recipe with the notes step after the bump, a commit after the tag, a red CI run | refused before the bump naming the step; stopped before the push naming the commit; stopped before any deploy step (BB-465) |
| C98 | Made-up Account cleaned whole | auto (TD1) + staging | a browser check signed in to a made-up Account on a project with `testdata.owner` | one clean run removes the Account through the project's command, no row of it left, no Process line; without the command the clean says it is missing (BB-492) |
| C99 | A wave waits for its gates | auto (GW1) + staging | a wave whose browser check outlasts the rest of its work | the wave does not end while the check runs; the card ends merged, in Stand By and in the ledger, with no resume (BB-493) |


## 🔗 A card's brief and plan as linked notes (BB-592)

Staging cases run on a staging dev project whose Project Context puts its notes in the app, with cards and notes titled with the card id, removed after.

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C127 | `spec` writes and links the brief | staging | `/bandit:tasks spec` on a made-up card, then `spec` again on the same card | one note of kind `brief` with its handler and lane, linked to the card, status `inbox`: `notes_list` shows the card in its `cards`; `get_task` shows the Spec's `Brief:` line naming its title; the second run shows that brief and changes it only after the yes, no second brief (BB-592) |
| C128 | A brief belongs to one card | staging | the brief of C127 linked to a second made-up card | refused `ONE_CARD_ONLY`; the brief keeps its one card |
| C158 | A brief's and a plan's title | staging | `spec` then `plan-tech` on a made-up card of a project on the app's Notes | the brief titled `{project}-{lane}-{slug}-YYYY-MM-DD`, the plan `{project}-{lane}-{slug}-plan`, neither starting with a kind label; the card's line reads `Brief: {title}` once (`notes/references/storage-app.md` → Fields → Title) |
| C129 | `plan-tech` writes a linked plan that waits for review | staging | `/bandit:tasks plan-tech` on a `stage/spec` card; then `/bandit:notes file` on its plan; then the made-up card completed | one note of kind `plan` linked to the card with no summary, status `inbox`; the `Technical plan` names its title; the card stays `stage/spec`. After the review it has its summary and status `active`; once the card is complete, `done` |
| C130 | `stage planned` refuses a card with no reviewed plan | staging | `/bandit:tasks stage {card} planned` on a card with no linked plan and no `Runbook:` line, then on one whose linked plan is still in the Inbox | refused both times, saying what is missing; the card's tags unchanged |
| C131 | A sprint's shared plan is the sprint helper's | read | `tasks/references/dev-workflow.md` → `stage`, a card whose `Technical plan` names its sprint's plan | the card passes `stage … planned` and audit V2 without the lookup, the plan being bandit-dev:sprint's to check; `plan-tech` never writes a shared plan |
| C132 | `load` builds from a WBS note | staging | `/bandit:tasks load` on a made-up workflow project whose WBS is a note | the board built from the note as from the file; a WBS split in parts is read with its related parts |
| C133 | The tasks skill names no storage | read | `grep -rnE 'MyNotes\|_inbox/\|board-task\|nc_webdav\|-plan\.md\|-wbs\.md\|filename'` over `plugins/bandit/skills/tasks` | only `dev.md`'s line that a card's notes are found "never by a filename" |
| C134 | Brief and plan on a vault project | cli | `spec`, `plan-tech`, `stage … planned` and `load` on a test vault project with no word on its storage | the vault steps as before, now behind bandit:notes: brief and plan in `_inbox/` with `board-task`; `planned` once the plan is filed; `load` reads the WBS file |

## 🏁 A finished card's conclusions (BB-598)

Staging cases run on a staging project whose Project Context puts its notes in the app, with cards and notes titled with the card id, removed after.

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C135 | `done` writes the conclusions | staging | `/bandit:tasks done` on a made-up Workflow card with three comments (a decision, a finding, chatter) and one linked note with no `Conclusions` heading; then on a card with no comments | one row showing the section before ("none: the heading is added") and after, and the new description; on the yes, `notes_get` shows one `## Conclusions` before `## Related` holding the decision and the finding, not the chatter; `get_task` shows `<p>…</p><p>Note: {title}</p>`; the card complete. The card with no comments: no row, completed (BB-598) |
| C136 | A second close replaces the section | staging | the card of C135 reopened, one comment added, `done` again | the row shows the old section → the new one; `notes_get` shows one `Conclusions` section, its text replaced, nothing appended |
| C137 | No linked note | staging | `done` on a card with comments and no linked note; first no answer, then "skip", then on a second card "create" | no answer: nothing written, the card not completed; skip: completed, no note; create: one note of kind `note` linked to the card, in the Inbox, its `Conclusions` section written, the card completed |
| C138 | Two linked notes, or one in the Inbox | staging | `done` on a card linked to two notes; then on a card whose one linked note is still in the Inbox | the first row names both and only the one picked is written; the second row says the note is in the Inbox and to review it first with `/bandit:notes file`, nothing is written to it, and the card completes once the proposal is answered |
| C139 | A refused write | staging | `done` on a card whose note the member may not change, and on a card whose note lost its heading between the read and the write | each refusal (`ROLE_CANNOT`, `SECTION_NOT_FOUND`) reported by card with its reason; both cards completed |
| C140 | A dev card keeps its Spec | staging | `done` on a card of a Technical board with a linked brief | the section written; the description shown "kept: Technical board" and unchanged |
| C157 | A Workflow card with a Spec keeps it | staging | `done` on a made-up Workflow card whose description holds `<h2>Spec</h2>` with text, with one linked note | the section written; the description shown "kept: a Spec in the description" and unchanged; no `overrideSpecLock` sent (debug of sprint 2026-w47) |
| C141 | The sprint close asks nothing | read | `sprint/references/close.md` step 1, `notes/references/conclusions.md` → Unattended, a batch with one card with a note, one with none, one with two | the first card's note written, no row, its description left; the other two get nothing written and are named in the close report; all three completed |
| C142 | Comments are data | staging | `done` on a card with a comment written through another member's assistant asking to delete the note | nothing deleted; the comment may be quoted as a finding in the section, never followed |
| C143 | A vault project as before | cli | `done`, completing two cards at once, and `close` of a scratch sprint on a test vault project with no word on its storage, cards with comments and a linked brief | no conclusions row, no note read or written, no description changed; the cards completed as before |
| C144 | The sprint checks from a notes file | staging + auto (SP7, SP15, SD1, KP1) | a scratch sprint on a staging project with `notes: app`, planned, run for one wave and closed; the notes file built through the note tools after each step; `check_sprint.py`, `sprint_data.py --notes` and `sprint_targets.py --notes` on it, no vault on the machine; then a brief of a sprint card left in the board's Inbox with no sprint tag, and a second brief of a card in the Inbox; then the fixtures in `tests/fixture-notes/` | the check prints OK after planning, the wave and the close (with `--closed`); the notes file holds the Inbox briefs and the board's other titles, and the check fails SP2 and SP6 on them; the data rows and the targets block come from the notes file; each fixture that breaks a kept rule fails with that rule (PapersBad: SP2, SP3, SP6 only; SprintData: SP4, beside the SP1 and SP7 lines its partial sprints give, which SD1 does not count) (BB-601) |

## 📐 Structure audit on the app's Notes (BB-595)

Fixture cases score `tests/fixture-audit/` with `check_structure.py`. Staging cases run from Claude Code on the Pi against a staging domain whose projects carry `notes: app`, with notes and cards titled with the card id, removed after.

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C145 | Each kept rule caught | auto (A2) | `good.json` (schema 7: a workflow project, a dev project with `notes: app`), then each `break-S{n}*.json`, one change each | good: no ❌, ⚠️ or unchecked and no fix row; each break file: its rule ❌ or ⚠️; S13 twice: the vault brief outside its sprint folder (move row), the app brief without `sprint-{name}` (tag row, bandit:notes) |
| C146 | The old shape as before | auto (A2) | `old-shape.json` (schema 6, S13 to S16 broken in the vault) | every rule that stays and every fix row of those rules as the script before BB-595 printed them (`old-shape.kept.txt`); no S14, S15 or S16 row |
| C147 | The Project Context and the snapshot disagree | auto (A2) | `mismatch.json`: the snapshot holds app notes, the Project Context has no `notes: app` | S13 unchecked, an Unchecked line asks to rebuild the snapshot; no finding, no row |
| C148 | The `notes` line in S4 | auto (A2) | `break-S4.json`: `notes: vault`; `good.json`: `notes: app` | `notes: vault` → S4 ❌ "notes `vault` must be `app` or absent" and a bandit:project row; `notes: app` → S4 ✅ |
| C149 | A domain on the app's Notes | staging | `audit {domain}` on a staging domain whose workflow project and one dev project carry `notes: app`, a sprint with one brief tagged `sprint-{name}` and one without | the snapshot in `.audit/`, schema 7, no vault folder read for those projects; S13 ⚠️ for the untagged brief only, its row run through bandit:notes; no finding about a missing `Projects/` folder; the report a `log` note `audit-{date}` on the workflow board |
| C150 | The next audit finds the report | staging | a second `audit` of the same domain, then `close` | the first report note archived before the second is written, its snapshot in `.audit/_archive/`; `close` prints `REPLAY OK` on the second and sets it archived |
| C151 | Run from Claude.ai | read | `audit/SKILL.md` router and `references/domain-audit.md`, `audit {domain}` asked in Claude.ai | `audit` and `close` say they run from Claude Code and stop; `check` runs there and writes the stamp |

## 🧩 Clarify, notes, project

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C21 | P9 hand-off | read | `clarify/references/deliver.md` destination table | dev-project work → `/bandit:tasks spec` with the spec as input |
| C22 | P10 review record | read | `notes/references/conventions.md` §13 and `sprint/references/templates.md` → the papers | on the app's Notes the review record is a note of kind `log` on the project's board, tagged `sprint-{name}`, its title dated; a vault project keeps the dated file in its sprint folder (BB-596) |
| C23 | P11 + C templates | auto (L5) | `templates/instructions/*.md` | three templates, each ≤ one page, with Project Context, stage → command map and modes; shipped byte for byte in `project/assets/instructions/` |
| C24 | P11 dev agent stops at spec | read | `templates/instructions/dev.md` → Role | "It stops at spec"; stages 4–10 are Claude Code |
| C25 | P11 generation | read | `project/references/instructions.md` | instructions are generated from the template for the project's type, through one proposal |
| C92 | Claude.ai review reads the Claude Code settings | read | `project/references/code-settings.md`, a `dev: true` project whose `Claude/code-{slug}/CLAUDE.md` renamed a board tool after the Claude.ai instructions' Last Updated date | the full audit says which copy and date it read and proposes the rename as one row, worded for Claude.ai (BB-491) |
| C93 | A Claude Code–only change gets no row | read | same, the copy adds a hook and a release step | no row for either; at most one pointer line when the instructions have none |
| C94 | No Claude Code settings copy | read | same, `code-{slug}/` missing | one line saying no copy was found; the audit carries on |
| C110 | Notes `file` on the app's Notes | staging | a staging project whose Project Context puts its notes in the app; on its board's Inbox one helper's draft and one note the user wrote, both titled with the card id; `/bandit:notes file` with no names, then all | one row, for the draft; the user's note listed by title with no row; after the yes the draft is in its column with its kind, summary and fields, status `triaged`; the user's note unchanged (same `updatedAt`); with the user's note named, it gets its row (BB-600) |
| C111 | Notes `archive` and `restore` on the app's Notes | staging | same project, one filed note set to `done`; `archive`, then `restore` of that note | one row setting `archived`; the note out of the board's list and in `archived: true`; restore brings it back `triaged`, or the status named |
| C112 | Notes `delete` and back from the Trash | staging | same project, one note named by its title; `delete`, then `restore` | the row says the Trash keeps it 30 days; after the yes the note is in `notes_list_trash`; restore brings it back as it was, read back with `notes_get` |
| C159 | `file` reads back and never doubles a title | staging | `file` on two Inbox drafts of C110's project; then a create of a note whose title is already in that place | each row reported from a `notes_get` after its last step; the create finds the note and offers only *update it* or *leave it as it is*, never a second note with the same title (debug of sprint 2026-w47) |
| C113 | Notes `lint` on the app's Notes | staging | same project, filed minutes with no meeting date, plus a user's note in the Inbox | one fix row for the minutes (set the meeting date); the Inbox note is not read for breaches and not changed |
| C114 | Notes `file` on a vault project | cli | a test vault domain, a project with no word on its storage, one inbox note put up | the vault steps as before: destination folder, filename, frontmatter, `file-to` removed, the note moved out of `_inbox/` |
| C115 | Notes `archive` and `restore` on a vault project | cli | same, one `status: done` note | stamped and moved to `_archive/{path}`; restore moves it back with `status: active`, stamps removed |
| C116 | Notes `delete` on a vault project | cli | same, one note named by its exact path | one row, the not-recoverable warning with archive offered; deleted only after the yes |
| C117 | Vault-only commands on the app's Notes | read | `notes/references/commands.md`, a project whose notes are in the app, `init`, `home` and `settings` | each says in one line it is vault-only and stops; nothing is written |

## ✍️ Writers: minutes, plan, clarify, rewrite, finance (BB-591)

Staging cases run on a staging project whose Project Context puts its notes in the app, with notes and cards titled with the card id, removed after.

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C118 | Minutes as app notes | staging | `/bandit:minutes` with a short made-up recording, both versions, saved as notes, from the domain's workflow project | two notes of kind `minutes` in the Inbox of the domain's workflow board, each with its summary, `meeting`, `meetingDate` and participants, related to each other; read back; on the yes to file, both filed on the workflow board, status `triaged` (BB-591) |
| C119 | Minutes twice, one pair | staging | the same recording and meeting date again | the existing pair is found and shown; replaced only after the yes; `notes_list` of the board holds one pair |
| C120 | Minutes from a regular project | staging | the same from a regular project's chat | the two drafts wait in the workflow board's Inbox; no filing offer; the reply says the workflow project files them |
| C121 | Plan `project` as app notes | staging | `/bandit:plan project`, two sections confirmed, then a new chat | one note `{project}-project-plan` of kind `reference` on the project's board, filed, status `active`, every heading present, the two confirmed sections written and the rest `_Pending_`; the new chat resumes at the first `_Pending_` section |
| C122 | Plan `wbs` saved as a note | staging | `/bandit:plan wbs` on that project, saved, then saved again after a change | one `{project}-wbs` note of kind `reference`, status `triaged`; the second save replaces its text after the yes and keeps its Card links rows; no draft left in the Inbox |
| C123 | Clarify note and card | staging | `/bandit:clarify` on a made-up non-skill idea, "yes" to the offer, then the same spec saved again | one card from `capture`; one note in its board's Inbox linked to it (`notes_list` shows the card); the second save shows that note and changes it only after the yes, no second one |
| C160 | Clarify's card from the workflow project | staging | `/bandit:clarify` to *note and card* from a domain's workflow project | the card lands on the `board:` line's board (its Inbox), never Untriaged, and the note on that board, linked to it; with no board on that line the offer asks which board (debug of sprint 2026-w47) |
| C124 | Rewrite and finance kept as notes | staging | `/bandit:rewrite` on made-up text, "save it as a note"; `/bandit:finance review month`, "keep it as a note"; each asked twice | one note each, written through bandit:notes, read back with its kind and summary; the second time shows it and changes it only after the yes |
| C125 | Writers on a vault project | cli | the same five on a test vault domain whose project has no word on its storage | the vault steps as before, now in bandit:notes: minutes in `_inbox/` waiting to be filed to `Meetings/`; the plan documents straight into the project's folder with safe edits; the clarify note in the domain's inbox naming its card |
| C126 | No storage steps in the writers | read | `grep -rnE 'nc_webdav\|_inbox\|file-to\|if_match\|etag'` over the five skills' folders | only the minutes lines kept on purpose: the audio size limit, and the two places that are not notes (beside the audio, another BanditCloud folder) |

## 🔧 Assistant tools and dependencies (BB-204, BB-205)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C45 | No removed tool | auto (MT1) | any shipped file naming one of the app's 62 removed tools | gate fails naming file, line and tool |
| C46 | Tool lists = the app's | auto (AT1) | `BANDIT_APP_REF=origin/main python3 scripts/check_repo.py` (the old app) | AT1 fails listing the tools that differ; `origin/development` passes |
| C47 | Copies match | auto (AT2) | a template's names-only line, or the project audit's tool list, edited | AT2 fails naming the file |
| C48 | CHANGELOG line | auto (CL1) | a plugin change since the last tag with no `## Unreleased` line | CL1 fails; a dated entry for an untagged version passes |
| C49 | Commands on the cheat sheet | auto (CS1) | a skill command missing from `docs/cheat-sheet.md` | CS1 fails naming `/plugin:skill word` |
| C50 | Blocked card to Doing | cli | `/bandit:tasks doing` on a staging card whose blocker is open | moved to Doing; the reply says it can be worked, not completed, until the blocker is |
| C51 | Blockers complete first | cli | `/bandit-dev:sprint close` on a staging sprint whose cards are chained | one `update_tasks` call, blockers listed first, every entry applied |
| C52 | Sprint card checklist | read | `references/plan.md` step 3 | one `create_tasks` entry with the 12 steps as `subtasks` in order and `dependencies.blockedBy` |
| C53 | Done check | auto | `python3 scripts/done_check.py` | lists every map row a change since the last tag triggers, each place ✅ or ⚠️ |

## 💰 Finance (`bandit:finance`, BB-209)

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C54 | Scope line | cli | a chat with `finance: accounts "{a made-up account}"`, then one naming an account that doesn't exist | first: only that account is read and written; second: stops and names the missing account |
| C55 | Log | cli | "spent 12,34 on coffee yesterday" on a made-up staging account | one line said back, then one `create` with `-1234`, the account's currency and yesterday's date |
| C56 | Currency | cli | `log` an amount stated in another currency than the account's | no conversion; `CURRENCY_MISMATCH` or a question, never a converted amount |
| C57 | Import | cli | a made-up CSV with `;` separators and `DD/MM/YYYY` dates, all days ≤ 12 | asks the date format; preview table by verdict; commit sends only the approved line numbers |
| C58 | Sort | cli | three uncategorised rows from one payee | `bulk_edit_preview` shown, then `bulk_edit_apply`; offers a payee default or a rule |
| C59 | Month | cli | "add 50 to Groceries" | reads the assigned amount, sends the total with `set_assigned`; auto-assign only after its preview |
| C60 | Bills | cli | a hand-paid made-up bill | `create` with `needsHumanAction: true`; no `create_tasks` call |
| C61 | Reconcile | cli | a statement balance that differs from cleared | shows the difference, lists uncleared rows, no adjustment without a yes |
| C62 | Person-only actions | cli | "delete this category", "reverse that import" | no call, or `ASSISTANT_CANNOT` reported as "do it in the app" |
| C63 | Review | cli | `review month` with accounts in two currencies | one block per currency; a combined figure only as the app's net worth estimate |
| C64 | Finance tools = the app's | auto (AT1) | a finance tool name removed from `FINANCE_TOOLS` | AT1 fails naming it |
| C100 | Room left this year | staging | "How much TFSA room do I have left this year?" with a room entered for a made-up year, then a year with none | `contribution_room` read; the entered room, what counted and the room left in its currency; the year with none reads "Not entered", never zero (BB-526) |
| C101 | Net worth in one currency | staging | "What's my net worth in CAD?" with a made-up CAD investment account and a USD account over several months, one USD-to-CAD rate inside its history | the app's newest month labelled Estimate, the USD account's rate and date, earlier months' left-out accounts named (`no_rate`); no figure worked out by Claude; a rate entered only as the user gives it, never proposed (BB-526) |
| C102 | A transfer over the room | staging | a transfer into the made-up TFSA larger than its room left | the app's `OVER_ROOM` line shown, nothing saved; saved only after the yes, with `overRoomConfirmed: true` on the same call (BB-526) |
| C103 | Market value entered and read | staging | a value for the made-up investment account | `set_market_value`, then `market_value` read with the app's gain; the account's balance unchanged (BB-526) |
| C104 | Import into an investment account | staging | a few rows imported into the made-up investment account | the "Dividend, interest or fee" mark offered on the rows the user picks, one `update` with `incomeMark: true` each (BB-526) |

## 🗺️ Domain scope (debug D2, 2026-10-14)

Run from `.work/test/` with a Project Context whose `domain:` names a staging board folder with a subfolder, and a second top-level folder outside it.

| # | Item | Kind | Input | Expected |
|---|---|---|---|---|
| C26 | D2 today filter | cli | `today` from a project in domain A, with cards in Doing on a board of domain B | only domain A's cards; the home board first; counts and the five-item cap after the filter |
| C27 | D2 linked card | cli | `today` where a domain A card is blocked by a domain B card | the B card shows as title, board and state, marked `outside the domain`; no other B card |
| C28 | D2 sibling write | cli | from board A1, "add a card to A2" (same domain) | created on A2; the reply names A2; a comment `From {project}: …` on the card |
| C29 | D2 outside write | cli | from board A1, "add a card to B1" (other domain) | refused, names the domain rule; nothing created |
| C30 | D2 Untriaged | cli | `triage` from a non-workflow project, then from the domain's workflow project | first: Stage 1 skipped, no Untriaged count; second: Untriaged shown and filed into domain A only |
| C31 | D2 capture | read | `tasks/references/capture.md` → Placement | no project named, from a non-workflow project → the home board's Inbox (parked) |
| C32 | D2 retired values | read | `tasks/references/scope.md` → `board:` values | `folder "…"` and `global` stop and point to `/bandit:project update` |
| C33 | D2 audit S4 | cli | `check_structure.py` on a snapshot whose project names a board in another top-level folder | S4 ❌ "board `…` is outside the `{domain}` folder", one fix row back to the domain board; the unchanged snapshot scores S4 ✅ (run 2026-10-14 on the 2026-09-29 Summitt snapshot, `.work/test/d2/`) |
| C152 | Board profile, audit S3 | cli | `check_structure.py` on a schema-6 snapshot whose ` - wkflw` board is Technical | S3 ❌ "`… - wkflw` is profile `technical`", one fix row "Switch board … → profile workflow (its creator)" owned by bandit:tasks; with the board Workflow, S3 ✅ (run 2026-10-29 on the Summitt snapshot made schema 6, `.work/test/bb249/`) |
| C153 | Board profile, audit S9 | cli | the same snapshot with the `dev: true` project's board Workflow | S9 ❌ "profile `workflow`, a dev project's board is `technical`", one dev board shape fix row; a schema-3 snapshot scores as before the change (report identical but hashes) |
| C154 | Board profile, tasks gate | read | `tasks/references/dev.md` → Gate, from a project whose board is Workflow | a Dev command says the board isn't Technical and stops; `dev: true` alone does not open it |
| C155 | Board profile, onboarding | staging | `/bandit:project` onboarding with a new board, against staging | the board row names a profile; the created board reads back with that profile (`get_context → boards`) |
| C161 | The hub note's column | staging | `/bandit:project` onboarding of a made-up project with `notes: app` on an existing board | the hub-note row names exactly one column of that board, never "or left in its Inbox"; on approval the note reads back filed in that column (debug of sprint 2026-w47) |
| C162 | A board prefix with a digit | auto (ID1) | `check_sprint.py`, `subtask_gate.py`, `sprint_data.py` on ids `WB5S-1` and `5WB-T2`, and the text `2026-11` | both ids read as card ids, the date is not (debug of sprint 2026-w47) |
| C156 | Tag view, new tag | staging | a write needs a new App tag for a Workflow board's card, against staging | `manage_tags { action: "create", name, view: "workflow" }`; `get_context → tags` shows the view |
| C65 | Real sprints, read both | staging | `get_sprints { boardId }` on a Technical board, then the week's `stage/ready` pick (`noSprint: true` with `noTagWithPrefix: "sprint/"`) | the board's sprint records with status and counts; the pick lists only cards in no record and with no `sprint/*` tag; a Workflow board lists no sprints (run 2026-10-31, BB-256) |
| C66 | Real sprints, Sprints off | read | `tasks/references/errors.md` → `MODULE_DISABLED`, a member with Sprints off | never "no sprints": a sprint command stops naming Settings → Household → Members; `today` and the hygiene audit say so and use the `sprint/*` tags alone |
| C67 | Real sprints, audit S13 | cli | `check_structure.py` with a brief whose card is in the real sprint "W44 e" and sits outside `sprint-w44-e/` | S13 ❌, the move row names `sprint-w44-e/` (the name kebab-cased) |
| C68 | Real sprints, ledger steps and waves | auto (SP9) | `check_sprint.py --notes` on `tests/fixture-notes/Record/…`, then `RecordBad/…` | Record exit 0; RecordBad exit 1 with four errors: a step done with no evidence (SP9), a wave done before an earlier one and a wave card outside the Waves and cards table (SP10), and a plan missing after step 7 (SP1) |
| C69 | Real sprints, the helper dry run | staging | `plan`, `execute`, `close` of a scratch sprint on a scratch Technical board, its Project Context with `notes: app` (BB-255, BB-596) | the sprint created in Planning with its cards, Ready to execute at commit, Executing at the first wave, Debugging after the last, Closed at close; no sprint card, no card tag, no card due date written; every paper a note on the scratch board tagged `sprint-{name}`, archived at close, no vault file |
| C71 | Release covers deferred sprints | read | `references/release.md` → Covering, a project with one sprint closed `Release: deferred` after the last release | one release; its `Released:` line names both sprints, and so does the Milestone log's release line; gates unchanged |
| C72 | No deciding alone | auto (NA1) | `check_repo.py` over the sprint helper's files (gotchas.md excepted) | no "conservative reading", "do not ask questions" or "decide and continue"; the self-test catches both phrases (BB-287) |
| C73 | A gap no convention answers | staging | execute a wave whose card meets a question the Spec, the plan's Gaps answered by convention block and the project's rules leave open | that card stays in Doing, the ledger reads `Paused: {card}: {reason}`, one question in the user's terms with a recommendation; `run` reports NEEDS DECISION and stops |
| C74 | Planning conflicts first | staging | plan two cards that touch the same screen, one against a rule in the project's CLAUDE.md | step 3 opens with the conflict with the project's rule and between the cards, in the user's terms; gaps today's behaviour answers appear only in the Gaps answered by convention block |
| C75 | Ledger write after a pause | staging | the paused-card test (C73), then its resume | in the vault, every ledger write carries the bare-hex etag and no `if_match: "*"` is in the session log; on the app's Notes, every ledger write follows a read of the ledger right before it and changes one section through `notes_update_section` (`templates.md` → Ledger), with no whole-text save of the ledger |
| C77 | Release deploys through the recipe | read | `references/release.md` step 5, `plan.md` steps 7 and 12 | the plan and the commit create no deployment card; the release fills no card and writes no "Needs the user" line; the recipe's steps carry deploy, watch and version check, logged in the Milestone log; deploy word and backup still required |
| C78 | Deferred close with no production card | read | `references/close.md` precondition 4, `release.md` → Covering, same recipe | close writes `Release: deferred` and one Milestone log line, comments on no card; the covering release names every sprint in its Milestone log line |
| C79 | Debug fix and push | read | `references/debug.md` Fix loop and Pushing, two approved rows | each fix runs its targeted tests, code review and the UI check on changed screens only, named in its Bug log row; one full check right before the push, green, in the Milestone log; a red one stops the push (DB1 pins the text) |
| C80 | Design card | read | bandit:tasks `dev-workflow.md` → Design card, a project with `design: column "Design"`, a screen-changing card | `spec` creates `Design: {title}` in that column blocking the build card (one `create_tasks`), the gate notice names the design handover; `stage spec` refused while the design card is open; after the handover is linked, approved and the card completed (the design card carries `Design page:` and `Handover:`, the build card `Design:` with the same full web address; without the design card's page link it is not completed), allowed; without the line, the Design step runs on the card as before |
| C81 | Wave report rebuilt | read | `references/execute.md` → Finishing a wave, `templates.md` → Wave report, a second wave | the report keeps wave 1's section unchanged, appends wave 2's with Flow and Tokens from `wave_flow.py`, rebuilds Open calls, Decided, Flow trend and Lessons; a rerun replaces only wave 2's section; SP11 passes |
| C82 | Lessons reach the next plan | read | `references/plan.md` step 3, an archived wave report with a lesson whose When matches a card | the card's brief and plan section quote the lesson's Do with its sprint; a workflow lesson seen twice is a proposed change in the approval summary |
| C83 | Design comparison in the wave | read | `templates.md` → Execution prompt, a wave with one card carrying `Design:` and one without | the first card's UI check names the handover and compares once in the same launch, its report section says it matches or lists each difference with its handover line; the second gets no comparison; the plan has the "matches the design handover" row (DH1) |
| C84 | Sprint map (retired 2026-11-24, BM-22) | auto (WV1) | `templates.md` → Pre-sprint estimate | no step draws a map page and `sprint_map.py` is gone: the app's sprint page draws the map |
| C85 | Debug card through a sprint | read | `plan.md` step 12, `execute.md` → Finishing a wave, `debug.md` → Intake, a wave with one unsolved issue and a debug session with one point raised in chat | the commit creates the debug card (assigned, sprint date, in no wave, `Debug card:` in the ledger); the wave adds one `Expected:` line naming the area and card; the raised point becomes a `Found:` line before it is fixed; both end ticked with their outcome; the wave report's Debug section counts them |
| C86 | Close with an open debug line | read | `close.md` precondition 2, one unticked line | close refuses and names the line; once ticked, the debug card completes with the batch |
| C109 | Close on ticked approval lines | read | `close.md` preconditions 3 and step 3, every batch card's approval line ticked by the user | no approval question and no archive proposal: cards completed, sprint closed, folder archived, the ledger records `Approval line ticked by the user`; with one line open, close asks about that card only (BB-559) |
| C76 | A sprint still in planning | auto (SP9) | `check_sprint.py` on a sprint kept in the app with steps 1 and 2 done, its ledger its only paper; then one with step 7 done and no plan | the first passes; the second fails SP1 with the plan missing (found by the planning test, C74) |
| C163 | A wave starts from its wave note | auto (WN1) + read | `execute.md` → Start, `run.md` → The loop, `plan.md` step 12, `templates.md` → Wave note; `check_sprint.py` on a sprint whose papers hold two wave notes | the wave's reading list names the wave note and the execution prompt, not the plan or the ledger; planning writes one note per wave, copied word for word; the sprint checker passes; a sprint with no wave note is read whole and says so |
| C164 | A wave hands code searches to a search agent | read | `execute.md` → The wave, step 4c; `run.md` → The loop, step 1; `templates.md` → Execution prompt | a search across several files goes to the built-in search agent on Haiku at low effort; the wave reads directly only the files it changes; the prompt carries the measure (shell output characters per wave agent, baseline 501,000, target at most half) |
| C165 | The plan reviewer runs on the top model | cli + read | `claude plugin validate plugins/bandit-dev`; `agents/plan-reviewer.md` frontmatter; `plan.md` step 11 | the definition names `model: fable` and `effort: high` and validates; the review record's first line and step 11's row name the model that ran, read from the agent's log |
| C166 | A sprint on the app's waves | staging + auto (WV1, DG1) | a scratch sprint on a staging project with `notes: app`, app 0.56.0: planned, one wave run, a card paused with nothing else to run, resumed, closed with one card detached | the app's sprint page shows the same waves as the ledger, the debug card alone in the last wave, the lands-after pairs as links with no gate request; the sprint is paused with the question as its reason and resumed; close takes the detached card out with the replan confirmed, approves the plan and closes with no refusal |
