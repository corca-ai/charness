# Friction Reset — Ownership Cutover Closeout

Date: 2026-08-26 Asia/Seoul
Status: implemented-uncommitted-with-explicit-review-nonclaim

## Implemented

Moved ordinary closeout risk selection from an unconditional `critique`
obligation to `prove`-owned judgment. Reversible local edits, cleanup, typing,
tests, and ordinary documentation now have a truthful deterministic path:
`Critique: not-required <reason>`. Named high-risk boundaries still select
their owning review surface. The universal task-completing closeout-claims
review and automatic multi-slice midpoint review were removed from the current
operating contract.

The cutover deliberately leaves the worker carrier, adapter bootstrap paths,
reviewer result schema, process cleanup, identity binding, partial-result
non-approval, #724 graph state, and external state unchanged.

## Capability Delivered

A normal local change can prove its result without manufacturing a reviewer
packet or a multi-worker review solely because it completed. A required
authority, durability, external-write, security, release, compatibility,
install/update, deletion, migration, or proof-surface boundary remains visible
and is still routed to its explicit owner.

## Contract Source

- [friction reset amendment](../ideation/2026-08-26-friction-reset.md),
  `## Current implementation contract: ownership cutover`
- [design north star](../../docs/design-north-star.md)
- [operating contract](../../docs/operating-contract.md), `## Critique Discipline`

## Verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_critique_skill.py --pytest-target tests/quality_gates/test_skill_docs_contracts.py --pytest-target tests/quality_gates/test_critique_enforcement_scope.py` — 99 passed.
- `python3 scripts/check_skill_contracts.py --repo-root .` — passed.
- `python3 scripts/check_skill_surface_preflight.py --repo-root . --changed-skill-md skills/public/critique/SKILL.md skills/public/impl/SKILL.md skills/public/prove/SKILL.md` — passed; all three surfaces retain headroom.
- `python3 skills/public/prove/scripts/check_boundary_escalation.py --repo-root . --detail --changed-path docs/implementation-discipline.md docs/operating-contract.md plugins/charness/scripts/check_skill_contracts.py plugins/charness/skills/critique/SKILL.md plugins/charness/skills/critique/references/cadence.md plugins/charness/skills/impl/SKILL.md plugins/charness/skills/prove/SKILL.md plugins/charness/skills/prove/references/review-gate.md scripts/check_skill_contracts.py skills/public/critique/SKILL.md skills/public/critique/references/cadence.md skills/public/impl/SKILL.md skills/public/prove/SKILL.md skills/public/prove/references/review-gate.md tests/quality_gates/test_critique_skill.py charness-artifacts/ideation/2026-08-26-friction-reset.md charness-artifacts/impl/2026-08-26-friction-reset-ownership-cutover.md` — `state: evaluated`, `triggered: false` for this explicit slice path set. The default dirty-tree read is not used as this slice's scope because unrelated work matches the repository probe.
- `python3 scripts/check_skill_contracts.py --repo-root .`, source/plugin `cmp` checks, and `git diff --check` — passed after the final content edits.
- `bash scripts/check-docs.sh` — passed after the final content edits.

## Lint Gate

`Lint Gate: ran-pass bash scripts/check-docs.sh` for the documentation
composite. `bash scripts/check-secrets.sh` scanned the full existing dirty
population and returned one redacted gitleaks finding; this remains
`Lint Gate: ran-fail-deferred bash scripts/check-secrets.sh <unattributed-existing-dirty-population>`.
`gitleaks protect --staged --config .gitleaks.toml --no-banner --redact` passed
over the 17-file cutover index with no leaks. No secret is reported or
reproduced here. The commit hook's final
`python3 scripts/check_boundary_bypass_ratchet.py --repo-root .` failed with
one new candidate, `1e997c7eba64cbe7`. Attribution identifies it as the
pre-existing unstaged pair `tests/quality_gates/test_python_length_gates.py` /
`scripts/check_python_lengths.py`; neither is in this 17-file staged cutover.
This is `Lint Gate: ran-fail-deferred` and the commit was not forced through.

## Truth Surface Sync

Source and checked-in plugin mirrors are synchronized for `critique`, `impl`,
and `prove`. The operating and implementation discipline docs, contract
validator pins, and focused test were updated together. `docs/handoff.md`, the
frozen goal draft, GitHub, remote CI, installed-host state, and external write
surfaces were not changed.

## Boundary Ownership

`Boundary Ownership: moved-to-owner` — `prove` owns the risk disposition;
`critique`, `issue`, and `release` retain the review/closeout decisions for
their material boundaries. This cutover does not absorb worker delivery,
adapter bootstrap, issue, release, or live-behavior ledgers.

## Critique

`Critique: not-run operator-directed exception` — the changed policy is a
proof-surface boundary, so this closeout makes no fresh-eye claim. The user
explicitly instructed that forced fresh-eye execution, handoff updates, and
micro-slices be omitted. Deterministic contract, parity, preflight, and docs
checks are evidence of those checks only; they are not a substitute for the
omitted observer.

## Contract Updates

- `prove` records the risk decision and supports
  `Critique: not-required <reason>` for ordinary reversible work.
- `critique` is selected by material risk, not task completion.
- Universal task-completing closeout-claims and automatic midpoint review
  obligations are removed; proof-surface verdict-logic review remains
  conditional on that logic changing.
- The current Goal Run amendment records #728–#732 and keeps the next
  one-command worker and adapter consolidation cuts visible without executing
  them here.

## Residual Risks

- The whole dirty-tree secret gate has one redacted, not-yet-attributed finding;
  this is not claimed clean.
- The pre-existing boundary-bypass candidate blocks the normal commit hook;
  no `--no-verify` commit was made. The 17 cutover files remain staged for the
  owner to commit after that unrelated dirty-tree issue is resolved.
- No fresh-eye, live hosted/provider, installed-host, GitHub, push, release,
  tag, or remote-CI proof was run or claimed.
- The file-backed worker and adapter ownership cuts remain future work.

## Next Slice

Implement the semantic-input/file-backed lifecycle carrier, preserving typed
preflight, cleanup, timeout, identity, and partial-result non-approval, then
measure the adapter bootstrap census before deleting duplicated paths.
