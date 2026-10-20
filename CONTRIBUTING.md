# 🤝 Contributing

Thanks for helping. This marketplace is small and opinionated: every installed skill loads into every chat, so changes stay light and every rule is enforced by code.

## Before you start

- **Open an issue first** for anything beyond a typo, using the [bug](.github/ISSUE_TEMPLATE/bug.yml) or [feature](.github/ISSUE_TEMPLATE/feature.yml) form, so the change is agreed before it's built.
- Read the [contributor guide](CLAUDE.md) (layout, rules L1–L8, branches) and the [decisions](docs/decisions.md) behind them.

## Making a change

1. Branch from `development`; never from `main`, which moves only at a release.
2. Turn on the pre-commit gate once: `git config core.hooksPath .githooks`.
3. Keep each skill within the house rules: a description of at most 300 characters, a `SKILL.md` of at most 150 lines as a router plus hard rules, procedures in `references/`, no project details, no person's name.
4. Run the gate before you push:

   ```
   python3 scripts/check_repo.py
   ```

   It needs Python 3 with PyYAML, and the `claude` CLI for `claude plugin validate` (`--no-cli` skips that rule locally).
5. Add a line under `## Unreleased` in the [changelog](CHANGELOG.md), in Added, Changed or Fixed (the gate fails a plugin change without one).
6. Run `python3 scripts/done_check.py`: it lists every place your change has to reach ([dependencies](docs/dependencies.md)). Update each open one, or say in the pull request why it needs nothing.
7. Open a pull request against `development`. CI runs the same gate.

## A new kind of mistake

If a review finds a mistake the gate didn't catch, the fix includes a new checker rule in `scripts/check_repo.py`, not only a new sentence in a doc.

## Releases

Maintainers release with `scripts/release.py X.Y.Z` (see [install, section 7](docs/install.md#7-release-maintainers)). Versions follow [Semantic Versioning](https://semver.org) as described at the top of the [changelog](CHANGELOG.md).
