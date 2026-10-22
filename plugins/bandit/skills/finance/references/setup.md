# 🏗️ Setup

**Command:** `/bandit:finance setup`
**Owns:** accounts · category groups and categories · targets · the first bills

Builds the money structure from a short talk, shown as one approval table, then written in order.
Also used for a single structural change later ("add a Pets category", "close the old card").

---

## 1️⃣ Read what exists

`finance_get_context`. Show what is already there in one short table per account (name, type,
currency, budget side, balance) and the groups and categories of each budget. Setup **adds to** what
exists; it never rebuilds it.

## 2️⃣ Ask, at most these

One message, plain words, only what the user hasn't already said:

| Ask | Why |
|---|---|
| Accounts: name, type, currency, opening balance and its date | `create` needs all of them |
| On budget or off budget, per account | 🔴 It changes every budget number: off budget = not in any budget. Savings held back, investments and foreign-currency accounts are usually off |
| The spending groups and categories they think in | Two levels only: group → category. One income group per budget |
| Fixed monthly amounts or savings goals, if any | Become targets |
| Regular bills and income: name, amount, how often, next date, which account | Become schedules (`references/bills.md`) |

Account types: `checking` · `savings` · `cash` · `creditCard` · `loan` · `investment` · `other`.
A card or loan you owe on opens **negative**. A new account starts **private to the user who made it**: sharing it is the user's own, in the app.

## 3️⃣ Propose, then write

One table: every row to create, in the order below. On yes, write in that order (later rows need
the ids earlier ones return), reading each result before the next:

| Order | Call |
|---|---|
| Accounts | `finance_manage_accounts { action: "create", name, type, onBudget, openingBalanceCents, openingDate, currency }` |
| Groups | `finance_manage_categories { action: "create_group", name, accountId, isIncome? }`: `accountId` names the budget, never guessed |
| Categories | `finance_manage_categories { action: "create_category", groupId, name }` |
| Targets | `finance_manage_budget { action: "set_target", categoryId, kind, amountCents?, byMonth?, scheduleId?, priority?, currency }` |
| Bills | `finance_manage_schedules { action: "create", … }` (`references/bills.md`) |
| Order | `reorder` / `reorder_categories` / `reorder_groups` only when the user asked for an order: every item named once |

Target kinds: `fixedMonthly` (this much every month) · `topUpTo` (fill to this balance) ·
`saveByDate` (reach this by `byMonth`) · `fundFromSchedule` (follow a bill's amount; `scheduleId`,
no amount, so its bill is created first). A target never assigns money by itself: `month` does.

## 🔧 Later changes

| Ask | Call | Note |
|---|---|---|
| Rename, change type, statement days | `finance_manage_accounts { action: "update" }` | `statementCloseDay`, `paymentDueDay`: 1–31 or null |
| Move on or off budget | `move_budget_side` with the full account order | 🔴 Confirm first: every budget number changes. `ACCOUNT_BUDGET_NOT_EMPTY` → its budget still has categories; the user removes them in the app |
| Retire an account | `close` (history kept, reversible with `reopen`) | Deleting an account is the user's own, in the app |
| Rename, hide, move a category | `rename_category` · `set_hidden` · `move` | Hiding keeps history. `move` stays inside one budget and leaves the assignment history behind: say so |
| Remove a target | `finance_delete_items { kind: "target", id: categoryId }` | Confirm first |
| Delete a category or group | — | The user's own, in the app. Offer hiding instead |
| Who sees an account, the default currency | — | The user's own, in the app |
