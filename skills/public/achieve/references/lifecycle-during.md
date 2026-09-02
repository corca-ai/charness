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
