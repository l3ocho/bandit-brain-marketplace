#!/usr/bin/env python3
"""Test fixture: stands in for a project's own command that removes a made-up Account and everything in it
(BanditBrain: scripts/remove-household.mjs). A dry run prints counts; --confirm "removes"; the id `fail` fails."""
import sys

account, confirm = sys.argv[1], "--confirm" in sys.argv
if account == "fail":
    print("remove: refused", file=sys.stderr)
    sys.exit(1)
print(f"{'removed' if confirm else 'would remove'} account {account}: members 2, sessions 3, finance_settings 1")
