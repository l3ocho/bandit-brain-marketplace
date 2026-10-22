# 📥 Import

**Command:** `/bandit:finance import`
**Owns:** bank CSV files into one account: mapping, preview, commit

> 🔴 The hardest seam in the module. A wrong guess either duplicates real rows or swallows one into
> the wrong bill, and nothing looks wrong until the numbers are. **Nothing is guessed.**

---

## 1️⃣ The file and the account

The user shares the file in the chat. Read its whole text (at most 1 000 000 characters; bigger →
ask for a shorter date range). One account per import; ask which when more than one is in scope.
The file is read **in that account's currency**, so a file from another currency's bank goes into
an account in that currency or not at all.

## 2️⃣ The mapping — read, never guess

Show the first five lines as they are, then fill the mapping from them:

| Key | How to decide |
|---|---|
| `delimiter` | The character between columns: `,` or `;` (many Brazilian banks use `;`). Default `,` |
| `hasHeaderRow` | Is line 1 names, not data? |
| `dateColumn`, `payeeColumn`, `notesColumn?`, `transactionIdColumn?` | Columns counted from 0 |
| `dateFormat` | `YYYY-MM-DD` · `DD/MM/YYYY` · `MM/DD/YYYY` · `DD-MMM-YYYY`. 🔴 When every day in the rows is 12 or less, `DD/MM` and `MM/DD` can't be told apart: ask |
| `amountMode` | `signed` (one `amountColumn`) or `debitCredit` (`debitColumn` + `creditColumn`) |
| `invertSign` | True when the bank writes spending as positive |

Show the mapping as a table beside the sample lines. Anything unclear → ask before the preview.

## 3️⃣ Preview — always

`finance_import_transactions { action: "preview", accountId, csvText, mapping, dateProximityDays? }`.
It writes nothing. Each row comes back with its verdict and `willImport`, the app's own default; `summary` counts them. Show the result as one table, grouped by verdict:

| Verdict | Default |
|---|---|
| **New** | Import |
| **Duplicate** (a known bank id, or same amount, near date, similar payee) | Skip; the user can override per row |
| **Matched to a bill** | Import: the bill's expected occurrence becomes this real row, no second row |
| **Unreadable** (a date or amount the mapping couldn't read) | Left out; its `problem` says why. Fix the mapping and preview again |
| **Ambiguous** (more than one bill could match) | Left out, unless the user picks the bill: `resolvedMatches { "<line>": "<scheduleId>" }`, from that row's own candidates only |

Show each row's raw cell beside the amount it was read as. A file refused whole names the likely
cause (wrong currency, wrong separator, an amount column with nothing in it): fix the mapping and
preview again.

## 4️⃣ Commit — only what the user approved

`commit { accountId, csvText, mapping, importLineNumbers, fileName, dateProximityDays?, resolvedMatches? }`
with the **same** text and mapping as the preview, the approved line numbers, and the file's name
(kept on the import record). All or nothing.

The app runs the user's rules and payee default categories on commit, so rows can arrive
categorised. Report: how many imported, how many matched bills, how many skipped, how many still
uncategorised, and offer `sort` for those.

## ↩️ Undo

Reversing an import is the user's own action, in the app. The skill can show what it would remove:
`finance_get_account_history { kind: "imports", accountId }`, then
`{ kind: "import_reversal_preview", batchId }`. A batch with any row since reconciled, split,
edited or made a transfer can't be reversed: the preview names those rows.
