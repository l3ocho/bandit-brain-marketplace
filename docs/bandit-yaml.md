# 📦 `bandit.yaml`: the project recipe

> The contract between the `bandit-dev` skills and an app repo ships inside the plugin: [`plugins/bandit-dev/skills/sprint/references/bandit-yaml.md`](../plugins/bandit-dev/skills/sprint/references/bandit-yaml.md) (keys, sections, refusals). This file keeps only what is specific to the projects that use it: the app's proposed recipe and the sources behind it.

The checker's rule Y2 holds the plugin file's key table equal to `recipe.py`'s `KEYS`, and every key a plugin reference or script reads to that list.

## 📝 Example (the Bandit Brain app, checked 2026-10-13)

```yaml
verify: npm run verify
branches: { trunk: development, deploy: main }
release:
  - npm version minor
  - git push origin development --follow-tags
  - git push origin development:main
migrations:
  dir: drizzle
  check: python3 -c 'import json;e=json.load(open("drizzle/meta/_journal.json"))["entries"][-1];print(e["tag"][:4])'
staging:
  up: bb-staging up
  refresh: bb-staging up --refresh
  down: bb-staging down
  where: bandit-port
testdata:
  schema: [src/domains/*/schema.ts]
  logic: [src/domains/*/server/]
  databases:
    development: 'psql "$DATABASE_URL"'
    test: "sh -c 'set -a; . ./.env.test; psql \"$DATABASE_URL\"'"
    staging: "docker exec -i bandit_staging_db sh -c 'psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\"'"
  owner:
    table: identity_households
    dry_run: { development: 'node scripts/remove-household.mjs {id}' }
    remove: { development: 'sh scripts/dev-remove-household.sh {id}' }   # the app's: backup, then --confirm
guard:
  credentials:
    block: ['\bscripts/set-password\.mjs\b', '\bscripts/bootstrap-household\.mjs\b', '(?i)\bpassword_hash\b\s*=']
    allow: ['node scripts/set-dev-passwords\.mjs( .*)?']
stop:
  paths: [src, drizzle, package.json, compose.yaml]
  close: /close-round (code review, npm run verify, the UI check when the UI changed, then commit; never push)
release_checks:
  gate: node scripts/check-release-docs.mjs
  ci: gh run watch "$(gh run list --branch main --workflow Deploy --limit 1 --json databaseId -q '.[0].databaseId')" --exit-status
```

The `guard` lines are a proposal for the app (2026-10-24, from its own `.claude/hooks/block-credential-writes.mjs`: the two interactive credential scripts and any raw write to `identity_users.password_hash` are refused; `scripts/set-dev-passwords.mjs`, the dev-only fixed login pattern, is allowed). The app keeps its own hook until the plugin one is proven.

The `stop` lines are a proposal for the app (2026-10-24, from its own `.claude/hooks/stop-gate.mjs`, which holds `src`, `drizzle`, `docs`, `package.json` and `compose.yaml` and names `/close-round`). `docs` is left out: a docs-only change no longer holds the chat. Until the app removes its own copy, that copy still holds docs-only and background-agent changes.

The `testdata.owner` lines are a proposal for the app (BB-492, 2026-11-13: in sprint clean-house-2 every browser check signed in to a made-up Account and the app added its own rows, so each clean-up stopped and the Account was removed by hand with `scripts/remove-household.mjs`: dry run, backup, confirm). The table is `identity_households` (read in `remove-household.mjs`); the wrapper that takes the backup and runs `--confirm` is the app's to write; `remove-household.mjs` needs `DATABASE_URL` and a backup from the last hour.

The `release_checks` lines are a proposal for the app (BB-465, 2026-11-13: its release gate `scripts/check-release-docs.mjs` and the CI Deploy run on `main` its recipe already waits for; the workflow name is the app's to confirm). `version` and `whats_new` are left out until the app has a command that prints them.

The recipe has no `handover` section: no helper creates or fills a deployment card, and `release` runs the deploy itself through the `release` steps (BM-5, 2026-11-23; the app dropped the section on 2026-11-08). Since BM-17 the reader knows no `handover` key either: a `handover` section left in a recipe is read by no command.

The `staging` section may also carry `commit` (a command printing the commit staging runs) and `after_push` (`run` or `show`), added in BM-26 (RS55). The example above is from 2026-10-13 and has neither; the app's real lines are the app's to write (the app agent's card on BB: Development).

The `release_checks` section may carry `no_ci` in place of `ci`: one line saying the release has no CI run and where its build is checked instead (BM-30, RS58). BanditBrain's release lost its CI build when GitHub Actions stopped (its D219): its steps run `verify` and its release gate on the development machine before the push and deploy an image built on Home Lab. Its line is the app's to write (the app agent's card on BB: Development).

The `staging` section may also carry `branch`: the branch staging follows, when it is not the trunk (BM-28, RS57). Absent means the trunk. A project whose staging deploys a `staging` branch that only its release moves writes `branch: staging`.

The `testdata` lines are a proposal for the app (checked 2026-10-15: tables in `src/domains/*/schema.ts`, rules in the server actions, staging's database publishes no port, the test suite reads `DATABASE_URL` from the git-ignored `.env.test`). Development reads `DATABASE_URL` from the shell the skill runs in. The app commits its own `bandit.yaml` and adds `.testdata/` to its `.gitignore`.

Sources: the app's `package.json` (verify), `docs/branching.md` rules 6, 8 and 9 (branches, migrations, release), `docs/staging-runbook.md` (staging). The app repo writes its own `bandit.yaml` (card "App repo: pipeline recipe and docs"); this file only defines the contract. Test fixture: `tests/fixture-app/bandit.yaml`, `bandit.missing-key.yaml` for the refusal and `bandit.no-migrations.yaml` for a repo without migrations, staging or testdata, `bandit.testdata-missing-key.yaml`, `bandit.testdata-unsafe.yaml` and `bandit.testdata-secret.yaml` for the guard's refusals, `bandit.testdata-owner.yaml` with `fake_remove.py` for a made-up Account removed whole, `bandit.notes-after-bump.yaml` for the release guard's order refusal; `schema.sql`, `src/rules.py` and `fake_db.py` are a small app and a stand-in database for trying the testdata skill without a server. The marketplace repo's own recipe is `bandit.yaml` at its root.
