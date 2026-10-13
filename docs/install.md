# 🚀 Install and deploy v0.1.0

> Leo's steps to deploy bandit-brain-marketplace v0.1.0 after approving the release candidate. Nothing here was run in sprint marketplace-v1: `development` is pushed and green, `main` is untouched, there is no tag.

## 1. Release the repo

On Bandit Port, in `~/projects/banditlabs/bandit-brain-marketplace`:

```
git checkout development && git pull
python3 scripts/check_repo.py                 # must print: check_repo: OK
git checkout main && git merge --ff-only development
git tag -a v0.1.0 -m "v0.1.0 · first version: rebrand, lighten, pipeline behaviour"
git push origin main --follow-tags
git checkout development
```

## 2. Claude.ai

1. Customize → Plugins → **Add marketplace** → `l3ocho/bandit-brain-marketplace`. Turn on **Sync automatically**, or use Re-sync after each release.
2. Install **`bandit`**. (`bandit-dev` and `bandit-maker` are Claude Code only: their agents and hooks don't run in chat.)
3. Customize → Skills: **remove the uploaded copies** of the ten old skills (the task board, notes, audit, project settings, clarify, text rewriter, project planner, WBS generator, meeting minutes and skill creator skills). **Keep** prompt-engineer and data-tools.
4. Check: type `/` in a chat; the `bandit` skills are listed with the plugin name, and no old copy appears twice.

## 3. Claude Code: laptop and Bandit Port

```
/plugin marketplace add l3ocho/bandit-brain-marketplace
/plugin install bandit@bandit-brain
/plugin install bandit-dev@bandit-brain          # developers: laptop and Bandit Port
/plugin install bandit-maker@bandit-brain        # Bandit Port only
```

`bandit-dev` declares `bandit` as a dependency: Claude Code disables it (its hooks and agent included) unless `bandit` is installed too (seen in the W7 tests).

Then `/plugin` → Marketplaces → `bandit-brain` → turn **auto-update on** (it is off by default for non-official marketplaces).

## 4. Laptop cleanup

- Remove from `~/.claude/skills/` the copy of the old sprint skill and the nine retired stub folders: their names are listed under D18 in `docs/decisions.md`.
- Remove the old sprint checker's `Stop` hook from `~/.claude/settings.json`: `bandit-dev` ships its own (`hooks/hooks.json`). Both at once would run the checker twice.
- In each dev repo that wired the old checker by hand in `.claude/settings.json`, remove that entry (the dev-mirror hook stays).

## 5. Project instructions (v5)

In each Claude.ai project, run `/bandit:project instructions`: it builds the next version from the one-page template for the project's type (`templates/instructions/`). Paste it into the project's instructions, then run `/bandit:audit check` there. Start with BanditBrain (`dev.md` template: the Claude.ai agent stops at spec).

The structure rules now pin the renamed working-folder guard (`s12.hook_sha12`): every existing Claude Code twin scores its `workdir.py` as outdated until `bandit:project` re-hands it (a comment-only change). Accept those rows at the next audit.

## 6. Archive the old skills project

Archive the `_Skills Manager` Claude.ai project. Its vault folder already moved to `MyNotes/BanditLabs/_archive/skills/_project/`.

## 7. Test

Run `tests/cases.md` once on each surface you use, then say approved. Claude.ai can't reach staging (tailnet only): test there read-only, or in a sandbox project.
