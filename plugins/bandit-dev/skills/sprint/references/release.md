# 🚀 The release cycle

Part of `bandit-dev:sprint`. Read before running `/bandit-dev:sprint release {sprint card}`. Run after
debug and before close: one release per sprint (pipeline stage 9). The recipe is the project's
`bandit.yaml` (`release`, `branches`, `migrations.check`, `staging.refresh`), read through
`scripts/recipe.py`; this file holds the gate, never the project's commands.

Contents: Preconditions · Steps · Marketplace cards · Never

## Preconditions

Check all before anything runs. Each miss is refused by name, with what would satisfy it, and nothing runs:

1. **Every card tested.** Each batch card's ledger status is `Tested by the user`, or Leo skips the
   test for a named card in this chat (quote him). Name every card that is neither.
2. **Debug done.** The ledger's At a glance says debug is done, or Leo says no debug was needed (quote him).
3. **Leo's deploy word,** in the message being answered, quoted in the ledger: "deploy", "release" or
   "ship it" for this sprint. An earlier message, an urgency remark or a test result is not it.
4. **Migration tail recorded.** `python3 ${CLAUDE_SKILL_DIR}/scripts/recipe.py tail`; write the tail in
   the ledger. It must equal the last row of the plan's Migration tail table plus the waves' additions
   (the ledger's migration lines); a difference is refused and shown.
5. **Backup confirmed.** Leo confirms in this chat that the production backup the project's runbook
   names has been taken (quote him), or the recipe's own backup step is the first `release` step.
6. **Recipe present.** `recipe.py require release branches.trunk branches.deploy migrations.check staging.refresh`.
   A missing key is refused by its name.
7. **Clean trunk.** `git status --short` empty, branch `branches.trunk`, level with origin after a fetch.

## Steps

1. **Run the recipe.** `recipe.py get release` lists the steps. Run them one at a time, in order,
   showing each command and its result. A failing step stops the release: nothing after it runs,
   the output goes under "Needs the user", and the ledger says which step failed.
2. **Marketplace cards** (below), when the sprint carries any.
3. **Record the release.** Ledger At a glance: `Released: {version} · {date} · {commit}` (the line
   `close` checks). Milestone log: one line with the deploy word quoted.
4. **Status line.** Sprint card section 1: `Released {version} on {date}; ready to close` (read the
   card first, change only that line). Comment on the sprint card: version, commit, recipe steps run.
5. **Staging.** Give Leo the `staging.refresh` instruction to put the release on staging; never run it.
6. Final message, ten lines at most, with the paste for `close`.

## Marketplace cards

A sprint that carries cards from the **Marketplace** column (skill changes) also releases the
marketplace repo, as its own version (decision D12), after the app's recipe:

1. In the marketplace repo, on its trunk: bump `version` in all three `plugins/*/.claude-plugin/plugin.json`
   to the next minor, and turn the CHANGELOG's `## Unreleased` into `## {version} · {date}`.
2. `python3 scripts/check_repo.py` must print OK; commit, then merge to its deploy branch and tag
   `v{version}`, on the same deploy word.
3. Record the plugin version next to the app's in the `Released:` line.

## Never

- Release without every precondition, or on a deploy word from an earlier message
- Continue past a failing recipe step, retry it with force, or edit the recipe to get past it
- Run `staging.refresh`, touch production data, or run credential scripts
- Complete a card or close the sprint: that is `close`
