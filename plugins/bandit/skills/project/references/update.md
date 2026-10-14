# 🎯 Targeted update from the vault

> Read for `/bandit:project update`: another project's instructions changed from their vault copy (bandit:audit settings rows use it).

## 🎯 Targeted update from the vault

Updates **another** project's instructions from its vault copy, because only a project can see
its own instructions. bandit:audit runs this for its settings rows. The user can run it too ("update
the Family instructions: board is now …").

**Inputs:** the settings folder (`MyNotes/{domain}/Claude/ai-{project}`), the production file
(the one matching the project's self-check stamp, given by the caller; not given → list the
folder and ask, never assume the highest `v{N}`), and the exact change.

1. **Read** the production instructions file raw, and keep its etag. Missing or unreadable → stop
   and report; nothing is written.
2. **Apply only the requested change** to this version. No audit, no reformatting. Anything else
   noticed goes back as an **extra fix row** (target + exact change) in the same hand-over, for
   the caller's proposal: never folded in silently, never just mentioned. Check the new value
   live, except a `board:` name that belongs to an approved rename not run yet: check that the old name still resolves, and say the new one is
   checked when the board row runs.
3. **Bump** the `**Version:**` and `**Last Updated:**` lines and the metadata, as Step 5 does.
4. **Write** the next instructions version with **Subsequent Writes** in
   `references/vault-storage.md`, as an approved row. The prompt-reference file is not bumped.
   **Project copy** (`references/output.md`) is skipped: this chat's project is not the target.
5. **Hand over** the file name and the full text to paste, with the Claude.ai project it goes into.
   After the paste: `/bandit:audit check` in that project, unless it has `domain: none`
   (bandit:audit scores domain projects only).
