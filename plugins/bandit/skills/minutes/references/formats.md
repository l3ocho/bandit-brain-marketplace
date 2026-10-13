# 📝 Minutes formats and writing rules

> Read before writing the minutes: the full and short layouts, and how to write them.

## 📝 Minutes format — full

```
# <Meeting type> — Minutes

> <the frontmatter summary sentence>

| | |
|---|---|
| **Date** | <from filename or transcript> |
| **Duration** | <n> minutes |
| **Source** | `<audio file>` |
| **Names mentioned in discussion** | <comma list> |
| **Next checkpoint** | <if stated> |

> Prepared from an automated transcript ... Anything marked *(to confirm)* was unclear in the recording.

## Discussion

| Subject Item | Summary (Notes) |
|---|---|
| **1. <Topic>** | <1–3 sentences> |

## Action Items

| # | Action | Owner | Due |

## Related

- [[<full-version filename>]] — full minutes
- [[<project slug>]] — project hub   (project meetings only)
```

The `## Related` section appears only when writing to the vault; other folders don't use
wikilinks.

Condensing rules: keep every subject (never merge topics), every decision, and every figure, date, name and amount. Cut the background, the path the discussion took, and anything the decision already implies. Rows carrying several decisions (schedules, policy changes) stay longer than the rest — that's correct, not a failure to condense. The header block collapses to one line and the caveat note is dropped; keep the *(to confirm)* markers.

## ✂️ Minutes format — short

Same subjects, same numbering, same action items, about a third of the words (roughly 600 words for a 78-minute meeting).

```
# <Meeting type> — Minutes (Short)

> <the frontmatter summary sentence>

**<Date> · <n> minutes · Source: `<audio file>`**
Next checkpoint: <if stated>

## ✍️ Writing rules (professional and human)

- Write like an experienced executive assistant, not an AI. Use plain, confident sentences, active voice and past or present tense. Avoid filler ("it was noted that", "a robust discussion") and inflated verbs.
- One row per real topic, in meeting order, with a numbered, specific subject ("Texas commercial cancellation fees", not "Fees").
- Each summary covers context → what was discussed → **Decision:** / **Going forward:** in bold where one was made. Keep the numbers, dates, amounts and IDs exactly as spoken — system, user and document IDs, never customer account numbers (see below).
- Leave out banter, jokes, personal chatter, profanity, private matters about individuals (e.g. someone's leave balance or personal life) and one-sided phone calls, except where the call produced an action.
- Don't invent attendees, owners or deadlines. If no owner was stated, write "Owner not stated".
- Fix obvious transcription errors only when the context makes them certain ("Leon Iyer" → "Leo and I", "Genesis" → "Genesys"). Otherwise mark them *(to confirm)*.
- Keep company and system names as used in the meeting.
- **No customer data, ever** — even when it's spoken in the meeting: no customer names, account
  numbers or references, addresses, phone numbers or call contents. Describe the case instead
  ("a PA residential account", "a customer whose name was stored with a typo") or use a
  placeholder (`[account]`, `[customer]`). Colleagues' names are fine. The verify step (10)
  re-checks for this.
- **Dates unambiguous:** written month ("October 1") or `YYYY-MM-DD`, never `10/01`.
