# 🚀 Install, update and set up

> How to install the `bandit-brain` marketplace on Claude.ai and Claude Code, keep it updated, set up a first project, and cut a release.

## 1. Before you start

| You need | Why |
|---|---|
| A paid Claude plan (Pro, Max, Team or Enterprise) | Plugins on Claude.ai need one |
| Claude.ai → Settings → Capabilities → **Code execution and file creation** on | Skills run in the code sandbox |
| The **Bandit Brain** MCP server connected | The task board: `tasks`, `audit`, `project`, `sprint` |
| A **Nextcloud** MCP server with WebDAV connected | The notes vault: `notes`, `minutes`, `plan`, `project`, `audit`, `sprint` |
| Gmail connected (optional) | `/bandit:tasks email` |

## 2. Claude.ai (web, desktop, mobile)

1. Customize → Plugins → **Add → Add marketplace** → `l3ocho/bandit-brain-marketplace`.
2. Install **`bandit`**. (`bandit-dev` and `bandit-maker` are for Claude Code: their agents and hooks don't run in chat.)
3. Check: type `/` in a chat on the web; the `bandit` skills are listed with the plugin name. The mobile apps don't list skills in the `/` menu, but a typed command (`/bandit:tasks today`) runs.

## 3. Claude Code

Plugins on your claude.ai account already reach Claude Code: they appear as `bandit@synced` and sync each time Claude Code starts. Install from the command line only on a machine that doesn't use that account:

```
/plugin marketplace add l3ocho/bandit-brain-marketplace
/plugin install bandit@bandit-brain
/plugin install bandit-dev@bandit-brain          # developers
/plugin install bandit-maker@bandit-brain        # maintainers
```

- `bandit-dev` declares `bandit` as a dependency: Claude Code disables it (its hook and agent included) unless `bandit` is installed too.
- Turn **auto-update** on: `/plugin` → Marketplaces → `bandit-brain` → **Enable auto-update** (off by default for marketplaces outside Anthropic's).

## 4. Update

| Where the plugins come from | How to get a new release |
|---|---|
| Your claude.ai account (web, desktop, mobile, and Claude Code as `@synced`) | In the **Claude desktop app**, switch to the **Chat** tab → Customize → Plugins → **Manage marketplaces** → ⋮ on `bandit-brain-marketplace` → **Check for updates**. Claude Code picks the new version up at its next start (or run `/reload-plugins`) |
| A marketplace added from the Claude Code command line | `/plugin` → Marketplaces → `bandit-brain` → **Update marketplace**, or `claude plugin update bandit@bandit-brain` per plugin |

Known limits on Anthropic's side (as of 2026-10-14):

- The claude.ai web app has no update control for a marketplace you added; use the desktop app.
- In the desktop app, **Check for updates** works from the **Chat** tab only. From the Code tab it fails with "Couldn't check for updates. Try again." ([anthropics/claude-code#86818](https://github.com/anthropics/claude-code/issues/86818)).
- **Sync automatically** on an account marketplace doesn't re-sync when a release is pushed, so every release needs the manual check ([anthropics/claude-code#93825](https://github.com/anthropics/claude-code/issues/93825)).
- `/plugin marketplace update` only refreshes the marketplace's listing; it doesn't update installed plugins.

What changed in each release: [CHANGELOG.md](../CHANGELOG.md). After a release that changes the Project Context or the instruction templates, run `/bandit:project audit` in each project to pick up the new version of its instructions.

## 5. First project

1. In the project's Claude.ai chat: `/bandit:project onboard`. One proposal covers the vault folders, the board project and the instructions, with the **Project Context** block every skill reads. Answer all, a list, or none.
2. Paste the instructions it hands over into the project, then run `/bandit:audit check` there.
3. **Dev projects** (`dev: true`): put the same Project Context block in the repo's `CLAUDE.md`, add a [`bandit.yaml`](bandit-yaml.md) at the repo root, and run the **🪞 Dev repo alignment** prompt from the [cheat sheet](cheat-sheet.md) in Claude Code.

## 6. Moving from the old standalone skills

If you used the earlier uploaded skills (task board, notes, audit, project settings, clarify, text rewriter, project planner, WBS generator, meeting minutes, skill creator):

- Claude.ai → Customize → Skills: remove the uploaded copies, so no skill appears twice.
- Claude Code: remove their folders from `~/.claude/skills/` (the retired names are listed under D18 in [decisions](decisions.md)), and remove any hand-wired sprint-checker `Stop` hook from `~/.claude/settings.json`; `bandit-dev` ships its own.

## 7. Release (maintainers)

Releases follow [Semantic Versioning](https://semver.org); the three plugins and the marketplace share one version. The rules for major, minor and patch are at the top of the [changelog](../CHANGELOG.md).

```
git checkout development && git pull
python3 scripts/release.py X.Y.Z             # dry run: shows what changes
python3 scripts/release.py X.Y.Z --write     # versions, CHANGELOG date, gate, commit, main, tag
python3 scripts/release.py X.Y.Z --push      # pushes development, main and the tag
```

The pushed tag publishes a [GitHub release](https://github.com/l3ocho/bandit-brain-marketplace/releases) with that version's changelog entry. Then run [tests/cases.md](../tests/cases.md) on each surface you use.
