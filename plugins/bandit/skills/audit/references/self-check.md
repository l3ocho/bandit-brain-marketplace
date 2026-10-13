# ✅ Self-check (`check`)

> Stamps the Claude.ai instructions version this project is running, then scores this one project
> with the script. Run inside the project being checked.

## 🔢 Steps

1. **Read what's running.** From this project's own instructions (the system prompt), take:
   - the `**Version:**` line
   - the `## 🧭 Project Context` block: `domain`, `project`, `type`, `board`, `prefix`
   - the Claude.ai project name, if the session shows it. Not shown → ask Leo for it (one line), or
     record `null`.
   No `**Version:**` line or no Project Context → no stamp. Propose the fix row instead:
   `bandit:project` audit of this project, which adds the missing line or block. Run it on Leo's yes.
2. **Find the vault folder.** `domain` ≠ `none` → `MyNotes/{domain}/Claude/ai-{project}`.
   `domain: none` → ask Leo for the path.
   List it with `nc_webdav_list_directory`.
3. **Read the vault versions.** For each `{prefix}-instructions-v{N}.md`, read the file raw and take
   its `**Version:**` line. Stop reading once one matches.
4. **Compare** and name the S5 case from the rulebook (its S5 table, first match wins).

5. **Propose one row**, then write only on Leo's yes:

   ```
   | # | Action | Path | Effect | Why |
   | 1 | stamp {domain}/{project} = 9.0.0 | the stamp ledger (`paths.stamps`) | one ledger entry | S5 check for the domain audit |
   ```

6. **Write the ledger.** Read it first and keep its etag. Missing → create it (omit `if_match`).
   The `.audit/` folder missing → that's its own row: ask before creating it.
   Replace only this project's entry; keep every other entry as read. Write with the bare-hex etag.
   On a 412, re-read once and re-merge; a second 412 → stop and report.
7. **Score this project** (`domain` ≠ `none` only). Build a snapshot per `references/snapshot.md`
   with the full board, this domain in `vault.domains`, only this project's folder under
   `settings`, and the ledger **as just written**. Then:

   ```
   python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
       --snapshot snapshot.json --project {domain}/ai-{project}
   ```

   Show its output as printed. Domain-wide rules (S1 folder, S3 one workflow) need the whole domain:
   they're `audit {domain}`'s job. Its fix rows are shown with the stamp row and run on Leo's yes,
   through their owners (`references/fix-rows.md` → **▶️ Executing approved rows**).
8. **Report in one line:** the S5 result and what was stamped, then the script's table.

## 🗂️ Ledger format

the stamp ledger (`paths.stamps` in `references/structure-rules.yaml`), pretty-printed, keys sorted:

```json
{
  "projects": {
    "Acme/home-reno": {
      "claude_name": "B - Bandit Brains",
      "version": "0.3.0",
      "prefix": "bb",
      "folder": "MyNotes/Acme/Claude/ai-home-reno",
      "type": "product_service",
      "board": "project \"Bandit Brains\"",
      "checked": "2026-09-25"
    }
  }
}
```

- Key: `{domain}/{project}` from the Project Context (`none/skill-manager` for `domain: none`).
- `claude_name`: exactly as Claude.ai shows it, or `null`.
- `version`: the first token after `**Version:**` (`4.2.1 · **Last Updated:** …` → `4.2.1`).
- `folder`: the settings folder that actually exists, as listed in step 2. Never derived.
- `checked`: today's date, local time.
