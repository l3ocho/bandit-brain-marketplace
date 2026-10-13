# 🔄 The rewrite procedure

> Read before every rewrite: the four steps, the output shape and the edge cases.

## 🎯 Core Philosophy

Neurodivergent brains process information differently. Walls of text, buried structure, and repetitive content create cognitive friction that makes documents functionally inaccessible. This skill reduces that friction by:

- **Visual anchoring** — emoji icons on headings create landmarks for scanning and re-finding sections
- **Progressive structure** — information flows from high-level to detail, so readers can stop at the depth they need
- **Deduplication** — repeated ideas get merged, not stacked; every sentence earns its place
- **Format-matching** — data types dictate presentation (tables for comparisons, lists for sequences, prose for narrative)
- **White space** — generous spacing between sections gives the brain room to reset

## 🔄 Process

### Step 1: Ingest and Audit

Read the source material (file or chat context) completely before writing anything. During this read-through, identify:

1. **Content inventory** — what topics/ideas are present?
2. **Structural skeleton** — is there an existing hierarchy (headings, sections, numbered items)? Preserve its intent even if you reshape it.
3. **Redundancy map** — flag content that appears more than once, in any form (exact duplicates, paraphrases, overlapping points). These get merged in Step 3.
4. **Data type scan** — for each chunk of content, tag it:
   - `comparison` → will become a table
   - `sequence/steps` → will become a numbered list
   - `properties/attributes` → will become a definition list or key-value pairs
   - `options/choices` → will become a bullet list with brief descriptions
   - `narrative/explanation` → will stay as prose paragraphs (kept short — 2-4 sentences max)
   - `reference data` → will become a table or code block
   - `action items / tasks` → will become a checkbox list
5. **Missing clarity** — note spots where the original is vague or ambiguous. You can expand these with clarifying language, but only to make the *existing* idea clearer — never inject new ideas or opinions.

### Step 2: Design the Structure

Build a heading outline before writing content. Rules:

- **H1** (`#`) — document title only; one per document.
- **H2** (`##`) — major sections. Each gets an emoji prefix that visually represents the section's topic.
- **H3** (`###`) — subsections within an H2. Also get an emoji prefix (can be the same family as parent or a more specific one).
- **H4** (`####`) — use sparingly, only if a subsection genuinely has sub-parts. Emoji optional at this level.
- **No deeper than H4.** If you need more depth, restructure — deep nesting is the enemy of scanability.

#### Emoji Selection Guidelines

Pick emojis that create **semantic landmarks**, not decoration. The reader should be able to scan just the headings and know what each section is about from the emoji alone.

Good patterns:
- 🎯 for goals/objectives/purpose
- 🔧 for setup/configuration/tools
- 📋 for requirements/checklists/specs
- ⚡ for quick reference/shortcuts/key points
- 🧩 for components/architecture/structure
- 📊 for data/metrics/analytics
- 🚀 for deployment/launch/getting started
- ⚠️ for warnings/caveats/gotchas
- 💡 for tips/insights/notes
- 🔄 for processes/workflows/cycles
- 📦 for packages/dependencies/resources
- 🗺️ for overview/roadmap/navigation
- ✅ for action items/tasks/done criteria
- 🔐 for security/auth/permissions
- 📝 for examples/templates/samples

Avoid: purely decorative emojis, multiple emojis per heading, or emojis that don't map to meaning.

### Step 3: Write the Content

Work section by section through your outline. For each section:

1. **Gather** all relevant content from the source (it may be scattered across multiple places in the original).
2. **Merge** redundant points into a single, clearer statement. If two paragraphs say the same thing differently, pick the better phrasing and enhance it — don't keep both.
3. **Rewrite** in plain, direct language. Short sentences. Active voice. No filler words ("basically," "essentially," "it should be noted that").
4. **Format** according to the data type you tagged in Step 1:

   **Tables** — use for comparisons, feature matrices, config options, or any content with 2+ attributes across 2+ items:
   ```
   | Feature | Free | Pro |
   |---------|------|-----|
   | Storage | 5GB  | 50GB |
   ```

   **Numbered lists** — use for sequences, steps, ranked items, or anything with inherent order.

   **Bullet lists** — use for unordered collections. Keep each bullet to 1-2 lines. If a bullet needs a paragraph, it should probably be its own subsection.

   **Checkbox lists** — use for action items and tasks:
   ```
   - [ ] Set up the database
   - [ ] Configure auth
   ```

   **Bold key terms** — bold the first occurrence of important terms or labels within a section to help scanning. Don't over-bold — if everything is bold, nothing is.

   **Code blocks** — use for any technical content: commands, config snippets, file paths, API calls. Always specify the language for syntax highlighting.

   **Callout blocks** — use blockquotes for important warnings or tips:
   ```
   > ⚠️ **Warning:** This will delete all data. Back up first.
   ```

5. **Verify** you haven't added ideas that weren't in the original. Expanding for clarity is fine ("the API" → "the REST API endpoint at `/v1/users`" if that's implied). Inventing new points is not.

### Step 4: Final Pass

Before outputting:

1. **Dedup check** — read through the full draft. If any idea appears twice, merge or cut.
2. **Heading scan** — read only the headings with emojis. Does a reader get the full picture from headings alone? If not, rename.
3. **Length check** — any prose paragraph longer than 4 sentences gets split or converted to a list.
4. **Consistency** — same formatting pattern for same data types throughout (don't use a table for one comparison and bullets for another similar one).

## 📝 Output Format

The final output is always markdown. Deliver it as a `.md` file (or inline for short input). If the user wants it in the MyNotes vault, hand the result to bandit:notes to file it.

If the rewrite turned up gaps or open questions (the "missing clarity" spots from Step 1), list them in a short `## ❓ Open questions` section at the end, and offer to run `/bandit:clarify` on them. Don't answer them yourself.

Structure:
```
# [Document Title — concise, descriptive]

> Brief 1-2 sentence summary of what this document covers and who it's for.

## 🗺️ Overview
[High-level summary — the "if you read nothing else, read this" section]

## [emoji] Section 1
...

## [emoji] Section 2
...
```

Every document starts with a title, a summary blockquote, and an overview section. The rest follows the structure derived from the content.

## 🧩 Edge Cases

- **Very short input** (< 5 lines): Still apply emoji headings and formatting, but don't force structure where there isn't any. A short note can stay short.
- **Already well-structured input**: Focus on emoji anchoring, dedup, and formatting improvements. Don't restructure for the sake of it.
- **Mixed languages**: Preserve the original language. Emojis are universal.
- **Code-heavy content**: Don't rewrite code. Structure the *surrounding* documentation and context. Code blocks stay as-is.
- **No clear topic grouping**: Create groupings based on affinity — things that would be useful to read together. Name the groups clearly.
