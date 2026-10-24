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
handover:
  board: Bandit CTO
  production: { column: Bandit Labs VPS, runbook: 'docs/deployment.md#Deploy now' }
  staging: { column: Bandit Port, runbook: 'docs/staging-runbook.md#SECTION' }  # SECTION: the app names it
guard:
  credentials:
    block: ['\bscripts/set-password\.mjs\b', '\bscripts/bootstrap-household\.mjs\b', '(?i)\bpassword_hash\b\s*=']
    allow: ['node scripts/set-dev-passwords\.mjs( .*)?']
```

The `guard` lines are a proposal for the app (2026-10-24, from its own `.claude/hooks/block-credential-writes.mjs`: the two interactive credential scripts and any raw write to `identity_users.password_hash` are refused; `scripts/set-dev-passwords.mjs`, the dev-only fixed login pattern, is allowed). The app keeps its own hook until the plugin one is proven.

The `handover` lines are a proposal for the app (2026-10-24, from the BC-24 deployment card: board and production column as used, deploy steps in the app's `docs/deployment.md` section "Deploy now"; staging runs on Bandit Port from `docs/staging-runbook.md`, whose section the app names).

The `testdata` lines are a proposal for the app (checked 2026-10-15: tables in `src/domains/*/schema.ts`, rules in the server actions, staging's database publishes no port, the test suite reads `DATABASE_URL` from the git-ignored `.env.test`). Development reads `DATABASE_URL` from the shell the skill runs in. The app commits its own `bandit.yaml` and adds `.testdata/` to its `.gitignore`.

Sources: the app's `package.json` (verify), `docs/branching.md` rules 6, 8 and 9 (branches, migrations, release), `docs/staging-runbook.md` (staging). The app repo writes its own `bandit.yaml` (card "App repo: pipeline recipe and docs"); this file only defines the contract. Test fixture: `tests/fixture-app/bandit.yaml`, `bandit.missing-key.yaml` for the refusal and `bandit.no-migrations.yaml` for a repo without migrations, staging or testdata, `bandit.testdata-missing-key.yaml`, `bandit.testdata-unsafe.yaml` and `bandit.testdata-secret.yaml` for the guard's refusals; `schema.sql`, `src/rules.py` and `fake_db.py` are a small app and a stand-in database for trying the testdata skill without a server. The marketplace repo's own recipe is `bandit.yaml` at its root.
