# 🔒 Security

## Reporting a problem

Please **don't open a public issue** for a security problem. Report it privately through GitHub: the repository's **Security** tab → **Report a vulnerability**. You'll get an answer there.

Useful in a report: the plugin and skill involved, what a skill could be made to read, write or delete that it shouldn't, and the steps to reproduce.

## What's in scope

- A skill writing outside its declared scope (another domain's board, another project's vault folders, the `.obsidian/` settings)
- A skill deleting or overwriting without the confirmation its rules require
- Scripts shipped in the plugins (`scripts/` folders) and the sprint-checker hook

The Bandit Brain app and the MCP servers the skills call are separate projects: report their problems there.

## Supported versions

Only the latest release on `main` receives fixes.
