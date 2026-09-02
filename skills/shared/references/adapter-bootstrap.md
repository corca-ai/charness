# Shared Adapter Bootstrap

> Status: current
> Source of truth: `<plugin-dir>/scripts/adapters/adapter_init_lib.py`.

All skill adapters that use the shared initializer expose the same first-use
contract. The skill wrapper declares only its own low-risk scaffold fields; the
shared initializer owns target resolution, lifecycle classification, idempotent
writes, and the operator-facing receipt.

Run the skill's documented command, or preview it first:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root . --dry-run
```

The command emits one `charness.adapter-bootstrap/v1` YAML receipt on stdout:

- `state: absent` means the target does not exist. A real run reports
  `status: initialized`; dry-run reports `would-initialize` and does not write.
- `state: valid` means the existing target is readable and either uses the
  supported adapter version or omits the optional version for legacy-compatible
  resolution. It is a no-op with `status: unchanged`; skill-specific resolvers
  remain authoritative for their own fields.
- `state: invalid` means the shared shape or a supplied skill resolver refused
  the target. The default is `status: refused` with no mutation.
- `state: unestablished` means the shared command could not establish a safe
  target state. It also refuses without `--force`.

`--force` is the explicit replacement grant. With `--dry-run` it reports
`would-overwrite`; without it, the receipt reports `overwritten` and
`mutation_invoked: true`. A target outside the repository or a symlink is
always refused. Existing adapters and comments are never rewritten merely
because bootstrap was run again.

The receipt is the common carrier, not a new progress ledger. It does not imply
that a skill's optional backend, reviewer, release, install, or other external
boundary is configured or authorized. Those fields remain owned by the skill's
resolver and explicit operator workflow. An absent optional adapter remains a
valid inferred-default state where that skill documents it.
