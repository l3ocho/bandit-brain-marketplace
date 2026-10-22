# 📆 Month

**Command:** `/bandit:finance month [YYYY-MM]`
**Owns:** the budget month: assigning, moving, holding, overspending, auto-assign from targets

Each on-budget account has its **own budget**. Work one budget at a time; with more than one in
scope, ask which or go through them in turn. No month given → the current one.

---

## 1️⃣ Read it

`finance_get_budget { month, accountId }` (or `currency` when the member has one budget in it).
Show, from the app's figures only:

| Block | From the read |
|---|---|
| **Left to assign** | `assignableCents`. 🔴 Negative = money assigned that doesn't exist: say so first |
| **Overspent** | Categories with `availableCents` below 0 |
| **Behind on target** | Categories whose target progress is short |
| **The rest** | Group, category, assigned, activity, available, one row each |

Real money only: projected bills never count as money to assign.

## 2️⃣ Change it

Every change is proposed as a table first (category, before, after), then written.

| Ask | Call |
|---|---|
| Put money in a category | `finance_manage_budget { action: "set_assigned", categoryId, month, assignedCents, currency }`. 🔴 A **set**, not an add: "add 50 to Food" → read the current assigned, add, send the total |
| Move money between categories | `move_between { fromCategoryId, toCategoryId, month, amountCents, currency }`: both rows or neither |
| Fill from targets | `auto_assign_preview { month, accountId }` → show it → on yes `auto_assign_confirm`. 🔴 It **overwrites** what those categories had assigned |
| Hold money for next month | `set_held { month, heldCents, currency, accountId }`; `0` releases it |
| Let a category carry its overspending | `set_carry_forward { categoryId, month, carryForward }` |
| Give or change a target | `set_target` (`references/setup.md` → targets) |

## 🔴 Overspending: two ways

| Mode | What happens | Right for |
|---|---|---|
| **Deduct** (the default) | The shortfall comes out of next month's left to assign; the category resets to 0 | Day-to-day spending: cover it now from elsewhere |
| **Carry forward** | The category stays negative next month; left to assign is untouched | A debt category: the negative is the debt |

Suggest covering an overspent category with `move_between` from one with money left; the user
picks where it comes from.

Editing a past month changes every month after it: say so before writing to one.
