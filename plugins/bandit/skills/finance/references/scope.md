# 🗺️ Scope — which accounts this chat may touch

Read the `## 🧭 Project Context` section before every read or write: in the Claude.ai project
instructions, or in the repo's `CLAUDE.md` on Claude Code. The block's format is owned by
bandit:project (`references/project-context.md` there). One optional key sets Finance's scope:

```
finance: accounts "Everyday", "Savings"
```

| What the chat has | The scope |
|---|---|
| A `finance:` line | Only the named accounts, plus the budgets and bills that belong to them |
| A Project Context with no `finance:` line | Every account the member can see |
| No Project Context (a plain chat) | Every account the member can see |

The app already limits the member to the accounts they are on the list for. The `finance:` line
narrows that further for one project; it never widens it.

## 🔎 Resolving it

1. `finance_get_context` once (add `includeClosed: true` only when the user asks about a closed
   account). Its `accounts` carry each account's id, name, currency, budget side and balances.
2. Match each quoted name **exactly** to an account name. No match → stop and say which name
   didn't resolve. It may be renamed, closed, or not visible to this member; never pick the
   nearest one.
3. Work by id from here on. Names are for talking to the user.

## 🧱 The rule inside the scope

| Thing | Read | Write |
|---|---|---|
| A scoped account: its register, statements, imports, reconciliation | ✅ | ✅ |
| The budget of a scoped on-budget account: its groups, categories, targets, months | ✅ | ✅ |
| Bills and income (schedules) on a scoped account | ✅ | ✅ |
| Payees | ✅ | ✅ Payees are household-wide: before a merge or a default category, say which scoped account it is for |
| Rules | ✅ | ✅ A rule runs over one account at a time: run it only over scoped accounts |
| An account outside the `finance:` line | Name and balance, only when the user asks | ❌ Never; say it is outside this project's accounts |
| An account the member can't see | ❌ The app answers `NOT_FOUND` | ❌ |

A report (`finance_get_report`) covers every account the member can see. With a `finance:` line,
say so in one line under the report; there is no per-account report.

## 🧭 Plain chat

No project, no line: every visible account is in scope. When more than one account could be meant
("log a coffee"), ask which, once, offering the names. Remember the answer for the rest of the chat.
