# ✅ Self-check (`check`)

> A project checks in: it writes its stamp (what it runs on, its Project Context, and in Claude
> Code the state of its working folder), then scores itself with the script. Run inside the
> project being checked.

## 🔢 Steps

1. **Read what's running.** From this project's own instructions, on its surface (bandit:project
   `references/surfaces.md`: the folder's `CLAUDE.md` in Claude Code, the system prompt's project
   instructions on Claude.ai), take:
   - the surface: `claude-code` or `claude-ai`
   - the `**Version:**` line
   - the `## 🧭 Project Context` block, every key as written
   - on Claude.ai, the project's name, if the session shows it. Not shown → ask once; no answer →
     `null`. In Claude Code the name is always `null`.
   No `**Version:**` line or no Project Context → no stamp. Run the fix instead:
   `/bandit:project audit` of this project, which adds the missing line or block.
   `domain: none` → no stamp either: say that the audit scores domain projects only, and stop.
2. **Read the working folder** (Claude Code, no `dev: true`). From the folder the session runs from:
   - `guard.script_sha12`: `sha256[:12]` of `.claude/hooks/workdir.py` (`s12.hook_file`), or `null`
     when the file is missing
   - `guard.settings_parses`: `.claude/settings.json` exists and is valid JSON
   - `guard.hooks`: each event of `s12.hook_events` whose command hooks name `s12.hook_script`
   - `workdir`: `.claude/workdir-manifest.json` (`s12.manifest`), parsed, or `null` when missing

   On Claude.ai, and for a `dev: true` project, `guard` and `workdir` are `null`.
3. **The stamp row**, written straight away, no question:

   ```
   | # | Action | Target | Effect | Why |
   | 1 | stamp {domain}/{project} = 9.0.0 | note `{domain}-audit-stamps` · section `{project}` | one section | checks in for the domain audit |
   ```

4. **Write the stamp** through bandit:notes (its write safety; `references/other-skills.md` there →
   Who writes what):
   - **Find the note.** `search` its title (`stamps.note_title`, `{domain}` as a slug), then
     `notes_list` of the domain's boards. Found → use it, wherever it is.
   - **Not found → create it** on the domain's workflow board (the board of the domain's folder
     whose name ends in ` - wkflw`); the domain has none → ask once which board of the domain keeps
     its audit notes. Kind `reference`, summary "Self-check stamps of the {domain} projects, one
     section each: written by /bandit:audit check, read by /bandit:audit.", filed in that board's
     first column.
   - **This project's section only.** A `## {project}` heading and under it one fenced `json`
     block (Stamp format). The section exists → `notes_update_section`. It doesn't → `notes_get`
     right before, then `notes_update` with the whole text plus the new section, sections kept in
     alphabetical order. Every other section stays exactly as read.
   - Read the note back and confirm the section.
5. **Score this project.** Build a snapshot per `references/snapshot.md` with the full board,
   every stamp of the note **as just written**, and only this project's notes. It is a working
   file in a scratch folder, never saved: `check` writes only the stamp. Then:

   ```
   python {skill folder}/scripts/check_structure.py --rules rules.yaml --rulebook rulebook.md \
       --snapshot snapshot.json --project {domain}/{project}
   ```

   Show its output as printed. Domain-wide rules (S1 folder, S3 one workflow) need the whole domain:
   they're `audit {domain}`'s job. Its fix rows run right away, no question, through their owners
   (`references/fix-rows.md` → **▶️ Running the rows**): here every row is in reach, since this
   chat is the project.
6. **Report in one line** what was stamped, then the script's table and one result line per row run.

## 🗂️ Stamp format

One section of the stamps note, keys sorted:

````markdown
## home-reno

```json
{
  "checked": "2026-11-22",
  "context": {"board": "project \"Home Reno\"", "dev": "true", "domain": "Acme", "prefix": "hr", "project": "home-reno", "type": "product_service"},
  "guard": null,
  "name": null,
  "surface": "claude-code",
  "version": "2.0.0",
  "workdir": null
}
```
````

- The snapshot's key for it is `{domain}/{project}`, from the note's domain and the section's heading.
- `context`: the Project Context's keys and values as text, exactly as written (`"dev": "true"`).
- `name`: on Claude.ai, exactly as it shows; otherwise `null`.
- `version`: the first token after `**Version:**` (`4.2.1 · **Last Updated:** …` → `4.2.1`).
- `guard`, `workdir`: step 2. `workdir` is the manifest as the guard wrote it, unedited.
- `checked`: today's date, local time. A stamp older than `stamps.max_age_days` gets an Unchecked
  line in the audit asking for a new check.
