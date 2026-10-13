# 📧 Email

**Command:** `/bandit-tasks email`
**Owns:** Gmail → **proposals only**

---

## 🔴 The one rule

**Zero writes. Both sides.**

| Never write to | Meaning |
|---|---|
| **Gmail** | No archive, no label, no trash, no spam, no reply, no draft. Reading only |
| **The board** | No task is created until the user names which proposals to take |

A wrong task is a nuisance. A wrongly archived email is gone from view and nobody knows it happened.

⛔ Even if the user says *"and archive them"* — that is a separate, explicit instruction, confirmed one thread at a time. It is not part of `/bandit-tasks email`.

---

## 🔎 Reading

`search_threads(query, pageSize, view)` — the query must be **Gmail syntax**, not natural language.

**Default sweep:**

```
in:inbox is:unread -in:draft newer_than:7d
```

| Variation | Query |
|---|---|
| Everything unread, any age | `in:inbox is:unread -in:draft` |
| Flagged for attention | `in:inbox is:starred` |
| Awaiting a reply from you | `in:inbox is:unread -from:me newer_than:14d` |
| With attachments | `in:inbox has:attachment newer_than:30d` |

- `pageSize` defaults to 20, max 50
- Default `view` returns subject, sender, snippet, date — **usually enough**
- Full bodies require `get_thread`. Only fetch them for threads that survived the filter

📌 Gmail matches at **thread** level. A thread appears if any one message matches, so `-is:starred` will still surface threads containing starred messages. Say so if it matters.

---

## ⚙️ Procedure

1. `search_threads` with the sweep
2. Discard: newsletters, receipts, notifications, anything requiring no act by the user
3. `get_thread` on the survivors only
4. For each, extract **the action, not the subject line**
5. Present proposals as a numbered list
6. Wait
7. On confirmation: `create_task` per accepted item — one call each, there is no bulk create
8. Report what was created and where it landed

---

## ✂️ What makes a task

| ✅ Propose | ❌ Skip |
|---|---|
| An act the user must perform | An act someone else must perform |
| A deadline stated in the message | A "FYI" |
| A commitment the user made in a reply | A thread already resolved further down |
| A form, payment or booking due | Marketing with a fake deadline |

**The title is the action.** *"Reply to Dana with the Q3 numbers"* — not *"Re: Q3 numbers"*.

📌 Read the **whole** thread before proposing. The obligation in message one is frequently discharged in message four.

---

## 📍 Where proposals land

**Untriaged**, by default. `create_task(title)` with no `projectId`.

Email proposals are captured, not filed. Filing is `/bandit-tasks triage`.

**Set a `dueDate` only when the message states one.** An invented date pollutes the Week board with fiction.

🚫 **Never set `origin`.** It requires `system`, `reference` and `link` together, can never be changed afterwards, and is reserved for a system creating a task on its own behalf. A person accepting a proposal is not that.

Put the source in `description` instead — sender, date, subject.

---

## 🧾 Reporting

Always state the shape of the sweep before the proposals:

> 34 threads read · 6 carry an action · 28 discarded

Then the six. If none carry an action, say so in one line and stop. **Do not manufacture a proposal to justify the run.**
