"""Test fixture: the rules the small app enforces in code, not in the schema.
The testdata skill must read these and create data that respects them."""


class Refused(Exception):
    pass


def add_member(team, members, username, role):
    # One owner per team: a second owner is refused.
    if role == "owner" and any(m["role"] == "owner" for m in members if m["team_id"] == team["id"]):
        raise Refused("a team has exactly one owner")


def assign_item(item, member, lst):
    # An item is assigned only to a member of the list's own team.
    if member["team_id"] != lst["team_id"]:
        raise Refused("assignee must belong to the list's team")
    # A private list's items go to its owner only.
    if lst["private"] and member["role"] != "owner":
        raise Refused("a private list's items are assigned to the team owner only")
