# Implementation contract — #692 adapter bootstrap ownership

Date: 2026-08-27 Asia/Seoul

## Decision

Make `scripts/adapter_init_lib.py` the single Charness-owned lifecycle for
public adapter initialization. Every shipped public wrapper emits one typed
`charness.adapter-bootstrap/v1` receipt. Fresh state initializes, valid
existing state is unchanged, dry-run reports without mutation, and invalid,
unestablished, symlinked, or escaping state refuses unless explicit `--force`
is present.

## Owned surface

The slice owns the canonical common initializer, its checked-in plugin mirror,
all 16 `skills/public/*/scripts/init_adapter.py` entrypoints and mirrors, the
consumer-classification declarations, and local contract tests. It does not
own scheduler behavior, hosted enforcement, conditional-trigger execution,
installed-host adoption, or consumer-repository rollout.

## Acceptance checks

- Cover all 16 public entrypoints with fresh, repeat, dry-run, invalid-version,
  explicit-force, unestablished, outside-root, and symlink-boundary cases.
- Keep the resolver callback authoritative for valid existing state while
  making the receipt and mutation decision common.
- Prove canonical/plugin parity and the classification contract without
  aggregating the dirty parent diff.
- Run focused tests and the relevant combined gate from a clean named branch;
  ordinary implementation does not owe universal changed-line proof.

## Verification receipt

- Base: `55026bdb6b5423fdaadffff218f32bff3b0f5811`
- Target: `47f5ddc30179f9a3a20954d69678b01c47319ef1`
- Commit: `fix(adapter): unify public bootstrap idempotence (#692)`
- Proof branch: `proof/issue-692-adapter-20260827`
- Proof path: `/tmp/charness-692-proof-20260827`
- Focused contract: `32 passed`
- Related suite: `76 passed`
- Standing classification: `37 passed`
- Combined focused/standing: `69 passed`
- Selected adapter evals: `10/10 passed`
- Source/plugin parity, Ruff, length, diff, and clean postflight: passed.
- No-`--verify` pre-commit: all 20 hook commands passed after a proof-only,
  unstaged compatibility overlay supplied the two stale critique snippets;
  that overlay was removed before postflight and is absent from the target.

## Aggregate-gate non-claim

The exact target without the overlay exits at the existing
`representative-skill-contracts` checker because it still requires
`Task-completing repo work always records critique before closeout.` and
`Scale the` / `pass, not the obligation`, which the current critique skill
already removed. The target run recorded 18 PASS scenario lines before that
failure. #692 does not restore deleted constraints or claim the aggregate eval
as green.

## Non-claims

No universal changed-line gate, forced fresh-eye review, handoff update,
micro-slice record, installed-host behavior, hosted/provider roundtrip,
scheduler or conditional-trigger change, consumer-repository adoption, remote
CI, push, release, or tag is claimed. Fresh proof used a named branch and an
explicit base/target/path; parent dirty state and the frozen goal/handoff
surfaces were preserved.
