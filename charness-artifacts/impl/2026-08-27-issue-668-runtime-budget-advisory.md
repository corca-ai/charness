# Implementation contract — #668 runtime-budget timing advisory

Date: 2026-08-27 Asia/Seoul

## Decision

The repeated runtime-budget trigger was a usability failure at the local
quality boundary, not evidence that the pytest suite needed another budget
relevel. The timing signal is now advisory at the `run-quality` orchestration
boundary. The checker remains blocking when invoked directly, and structural
configuration/profile/universe errors remain blocking in every path.

## Owned surface

Charness owns the checker flag, the local/release runner routing, the adapter
contract wording, and the decision record. It does not own a hosted SLO,
consumer repository rollout, or a scheduler redesign in this slice.

## Change carrier

Commit `8241d9922c37e8e63ab407091931a10ff3c839e6` adds `--advisory` to the
canonical and exported runtime-budget checkers, routes both local and release
`run-quality` timing checks through that explicit mode, preserves blocking
configuration/universe failures, and adds focused regression coverage.

## Verification receipt

- Base: `c1e527abb75a69bd1645c8eac9381ccf0caa68cc`
- Target: `8241d9922c37e8e63ab407091931a10ff3c839e6`
- Proof branch: `proof/issue-668-runtime-budget-20260827`
- Proof path: `/tmp/charness-668-proof-20260827`
- Direct focused suite: `86 passed`
- Standing focused suite with external cache/pycache: `86 passed`
- Selected combined quality gate: `2 passed`
- Canonical/plugin parity, diff check, isolated clean status, and final
  worktree cache/pycache absence: passed

The proof scope was explicit and did not aggregate the dirty parent diff.

## Non-claims

No scheduler/concurrency redesign, CPU-normalized metric, 4-core rebaseline,
hosted/remote CI enforcement, installed-host mutation, push, release, tag,
publication, or consumer-repository adoption is claimed. No universal
changed-line proof, forced fresh-eye review, handoff update, or micro-slice
ritual is claimed.
