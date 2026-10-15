#!/usr/bin/env python3
"""Test fixture: stands in for a database command (`psql` reading SQL from stdin) so the guard
can be checked without a server. It answers each RETURNING 'testdata' row with a made-up id and
each DELETE with a count, the way psql prints them in unaligned, tuples-only mode."""
import re
import sys

sql = sys.stdin.read()
n = 0
for table, key in re.findall(r"RETURNING\s+'testdata'\s*,\s*'(\w+)'\s*,\s*'(\w+)'", sql, re.I):
    n += 1
    print(f"testdata|{table}|{key}|fake-{n}")
for table in re.findall(r"^DELETE FROM (\w+)", sql, re.M):
    print(f"DELETE 1")
if "BEGIN READ ONLY" in sql:
    print("read ok")
