# Achieve Goal Run Pickup

Resume only with the exact objective `/goal #N`. The achieve pickup helper
resolves the repository, reads the Goal Run parent once, validates its metadata,
immutable Goal Binding, frozen draft hash, approved Work Item manifest by KEY,
and managed parent cursor, then reads only the cursor's next open child.

The binding freezes the plan by draft hash and the approved Work Item manifest
by KEY. Children are identified by marker. Membership comes from the provider's
sub-issue graph plus parent-metadata `amendments`; prose edits never invalidate
a run.

Pickup returns `verified-read` or a typed refusal. It does not infer execution
state from a local artifact, scan or reconcile the provider graph, mutate the
provider, or create a second progress record. Use the issue-owned Goal Run
bootstrap, sync, apply, and close commands for those operations.

## Parent execution cursor

The parent-owned cursor is the object at metadata `progress`. It holds exactly
six required fields: `schema` (the literal `charness.goal-progress/v1`),
`revision` (positive integer), `total`, `completed`, `open` (`total` is
positive and `completed + open` equals `total`), and `next`. `next` is `null`
when `open` is zero, otherwise one object with `key`, `repo`, `number`, `url`,
and `state` (`state` is `OPEN`, the URL is the canonical issue URL, and the key
names an approved Work Item). Two legacy digests are tolerated and never
compared: `progress.membership_sha256` and top-level
`current_membership_sha256`. Either may be absent; when present, pickup ignores
the value. Membership truth is the provider's sub-issue graph plus parent
`amendments`, so write the minimal cursor without inventing a hash. The cursor
may also carry `ready_keys`, the sorted ready frontier whose hard dependencies
are satisfied; `next` stays the primary resume pointer and must belong to it.
