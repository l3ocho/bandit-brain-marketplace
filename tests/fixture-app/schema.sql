-- Test fixture: a small app for the testdata skill. Two tenants' worth of tables:
-- a team owns members and lists; a list holds items; an item may be assigned to a member.
CREATE TABLE teams (
  id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name  text NOT NULL
);
CREATE TABLE members (
  id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id  uuid NOT NULL REFERENCES teams(id) ON DELETE RESTRICT,
  username text NOT NULL UNIQUE,
  role     text NOT NULL CHECK (role IN ('owner', 'member'))
);
CREATE TABLE lists (
  id       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id  uuid NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  title    text NOT NULL,
  private  boolean NOT NULL DEFAULT false
);
CREATE TABLE items (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  list_id     uuid NOT NULL REFERENCES lists(id) ON DELETE CASCADE,
  title       text NOT NULL,
  assignee_id uuid REFERENCES members(id) ON DELETE SET NULL,
  done        boolean NOT NULL DEFAULT false
);
