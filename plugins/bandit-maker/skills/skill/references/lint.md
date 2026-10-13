# 🧹 Lint

> Read for `/bandit-maker:skill lint [folder…]`: run the house gate over skills and turn every failure into a fix row.

1. **Targets.** The skill folders named. None named → every skill in the marketplace repo,
   `plugins/*/skills/*` (each folder holding a `SKILL.md`).
2. **Run the gate** without writing into a skill folder:
   `python3 -B ${CLAUDE_SKILL_DIR}/scripts/house_lint.py <folder> [<folder> …]`
   (`-B`: no `__pycache__` next to the scripts). R15 compares each skill's command words with every
   other skill in the repo; add `--names <file>` for any other file whose commands count as taken.
3. **In the marketplace repo,** also run `python3 scripts/check_repo.py`: it adds the repo's own
   rules (descriptions ≤ 300 characters, `SKILL.md` ≤ 150 lines, no project details, no old names).
4. **Show both outputs as printed.** Never reword or recount a result.
5. **Findings come fixed** (rulebook R12): each ❌ and ⚠️ becomes a numbered fix row with the skill,
   the rule, the exact change and the recommended fix. One answer approves all, a list or none.
6. **Write only approved rows**, then re-run both gates and paste their last lines.
