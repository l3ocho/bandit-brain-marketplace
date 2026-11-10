# 🚀 The release cycle

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint release {sprint}`. Run after
debug and before close (pipeline stage 10). **Releasing is the user's option**: a sprint may close
with no app release, and a later release covers it (Covering, below). The recipe is the project's
`bandit.yaml` (`release`, `branches`, and the optional `migrations.check` and `staging.refresh`), read through
`scripts/recipe.py`; this file holds the gate, never the project's commands.

Contents: Preconditions · Steps · Covering · Marketplace cards · Never

## Preconditions

Check all before anything runs. Each miss is refused by name, with what would satisfy it, and nothing runs:

1. **Every card tested.** Each batch card's ledger status is `Tested by the user`, or the user skips the
   test for a named card in this chat (quote them). Name every card that is neither.
2. **Debug done.** The ledger's At a glance says debug is done, or the user says no debug was needed (quote them).
3. **The user's deploy word,** in the message being answered, quoted in the ledger: "deploy", "release" or
   "ship it" for this sprint. An earlier message, an urgency remark or a test result is not it.
4. **Migration tail recorded.** `python3 ${CLAUDE_SKILL_DIR}/scripts/recipe.py tail`; write the tail in
   the ledger. It must equal the last row of the plan's Migration tail table plus the waves' additions
   (the ledger's migration lines); a difference is refused and shown. A recipe without migrations prints `none`.
5. **Backup confirmed.** The user confirms in this chat that the production backup the project's runbook
   names has been taken (quote them), or the recipe's own backup step is the first `release` step.
6. **Recipe present.** `recipe.py require release branches.trunk branches.deploy`. A missing key is
   refused by its name. `migrations` and `staging` are optional sections (`references/bandit-yaml.md`).
7. **Clean trunk.** `git status --short` empty, branch `branches.trunk`, level with origin after a fetch.
8. **Nothing owed to the repository.** `check_sprint.py` is green (SP14: the plan leaves no item for the close, the release
   or after the sprint), and the ledger's Follow-ups noticed and Needs the user name no change to the repository still to
   do for this sprint. Each one is refused by name: it is done now as a debug row, before the release, or becomes a card
   for a later sprint. The release ships all of the sprint's work; nothing reaches the trunk after it.

## Steps

1. **Debug card to Stand By, then run the recipe.** Before the first recipe step (on the marketplace repo, before `release.py --write`), move the sprint's debug card (`Debug card:` in the ledger) to `standby` with `update_tasks`, read back; `close` completes it. A release step that stalls or fails writes a Process line on it at once (`references/templates.md` → Debug card, Process lines). `recipe.py get release` lists the steps. Run them one at a time, in order,
   showing each command and its result. A step that runs the recipe's `verify` runs only when
   `python3 ${CLAUDE_SKILL_DIR}/scripts/code_changed.py --since {the commit of the last green full check, from the Milestone log}`
   says "full check: needed"; "not needed" (only docs, notes or comments) → the step is skipped and its line shown instead. `{version}` in a step is the version picked by Semantic
   Versioning (Marketplace cards, step 1). A failing step stops the release: nothing after it runs,
   the output goes under "Needs the user", and the ledger says which step failed.
2. **Marketplace cards** (below), when the sprint carries any.
3. **Record the release.** Ledger At a glance: `Released: {version} · {date} · {commit} · covers {sprints}` (the line
   `close` checks). Milestone log: one line with the deploy word quoted.
4. **Status line.** Ledger: `Released {version} on {date}; ready to close`. Milestone log: version,
   commit, recipe steps run.
5. **Production handover card.** The ledger's `Production handover:` line names it; none and the
   recipe has a `handover` section → create it now, as `plan.md` step 12 says. `get_task`, then replace
   its title and description with the ready form (`references/templates.md` → Handover cards), built
   from this release's facts and the `handover.production.runbook` section read on `branches.deploy`;
   the runbook's commands are copied, never written by the skill. Comment: version and commit. No
   `handover` section → no card; one line under "Needs the user". The card stays open: the user
   fires its hook and closes it. **No production part** (`recipe.py opt handover.production.column`
   prints `none`): no card and no "Needs the user" line; the recipe's own steps (step 1) carry the
   deploy, its watch and its version check, and the Milestone log holds each one's result.
6. **Staging.** `recipe.py opt staging.refresh`: give the user that instruction to put the release on
   staging; never run it. `none` → no staging step.
7. Final message, ten lines at most, with the production handover card's id (or, with none, the
   running version the recipe confirmed) and the paste for `close`.

## Covering

A release covers this sprint and every **deferred** sprint of the project: one whose ledger (in
`Projects/{slug}/` or `_archive/Projects/{slug}/`) says `Release: deferred` and that closed after the
project's last `Released:` line. Their code is on the trunk already, so the release ships it.

- **The `Released:` line names them all:** `Released: {version} · {date} · {commit} · covers {sprint},
  {sprint}`. The deferred sprints' notes stay as they are: they say deferred, and this line covers them.
- **One handover card:** this sprint's production handover card carries the release; its Facts name
  every sprint covered. A deferred sprint's own production card was left with one comment at its close
  (`close.md`), and the user closes it. With no production card, the Milestone log's release line names
  every sprint covered.
- **Plugins alone.** A sprint with Marketplace cards whose app release the user defers still releases
  the plugins: on the user's word for the plugins alone, run only Marketplace cards (below); the
  `Released:` line names the plugin version and `app deferred`, and close writes `Release: deferred`
  for the app.
- **The gates are unchanged.** Every precondition reads this sprint; the migration tail is this sprint's
  last row, which already follows the deferred sprints' migrations.

## Marketplace cards

A sprint that carries cards from the **Marketplace** column (skill changes) also releases the
marketplace repo, as its own version (decision D12), right after the app's recipe, in the same run: the two were tested together in debug (`debug.md` → Combined test). When the project is the
marketplace repo itself, its recipe already runs these steps: run them once.

1. **Pick the version** by Semantic Versioning, from what the CHANGELOG's `## Unreleased` entry
   holds: **major** = a command, mode or skill removed or renamed, or the Project Context format
   changed; **minor** = a new command, mode, skill or behaviour; **patch** = fixes and wording only.
   The user may name another version: theirs wins, quoted in the ledger.
2. In the marketplace repo, on its trunk: `python3 scripts/release.py {version}` (a dry run), then
   `--write` (versions, CHANGELOG date, gate, commit, tag), then `--push`, on the same deploy word.
3. Record the plugin version next to the app's in the `Released:` line.

## Never

- Release without every precondition, or on a deploy word from an earlier message
- Continue past a failing recipe step, retry it with force, or edit the recipe to get past it
- Run `staging.refresh`, touch production data, or run credential scripts
- Complete a card or close the sprint: that is `close`
- Put a password, token or env value in a handover card, or let its prompt run while the card
  is still in its not-ready form
