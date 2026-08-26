# Implementation contract — #693 distinct-context critique provenance

Date: 2026-08-27 Asia/Seoul

## Decision

Make critique round recording consume one delivered typed worker report. The
existing shared delivery-chain owner validates the report, receipt, result,
capability envelope, and ledger joins. The recorder copies the exact typed
`result.json` bytes into the durable round record and records the worker report,
execution identity, packet identity, reviewed-input identity, parent receipt,
and boundary fingerprint. Raw stdin and `--findings-file` submissions are no
longer a reviewer finding source.

Delivered `block` and `defer` results are valid round evidence because they are
findings that the next round must read; only the existing approval consumer may
require `verdict: pass`. Source and exported plugin mirrors remain byte-identical.

## Owned surface

This slice owns `record_round_findings.py`, the shared worker-carrier delivery
helper, their checked-in plugin mirrors, the critique contract text, focused
tests, and the evidence-led debug/implementation artifacts. It does not claim
host-attested process identity, fresh-eye execution, handoff maintenance,
changed-line proof, installed-host behavior, remote CI, or issue closure until
the separate provider readback and closeout floor are complete.

## Acceptance checks

- Accept a provenance-valid typed worker report whose semantic verdict is
  `block`.
- Refuse missing, raw, malformed, stale, or boundary-mismatched report input
  before writing a round record.
- Preserve the approval consumer's `pass` requirement.
- Record explicit worker execution and reviewed-input identities plus exact
  report/result digests.
- Prove source/plugin parity, focused critique tests, related worker-report
  tests, and static checks from a clean named proof worktree.

## Verification receipt

- Base: `48a69fd6b1117f403dcec2a0e18994fc32ee3cce`
- Target: pending implementation commit
- Proof branch/path: pending clean named proof worktree
- Focused standing command: `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/test_critique_round_findings.py`
- Pre-commit and related combined gates: pending

## Non-claims

No claim is made that a local file can cryptographically prove a human or host
process was distinct. The enforceable Charness boundary is that round recording
requires a typed report whose attempt, producer run, execution mode, reviewed
input, packet, parent receipt, boundary, receipt, result, and ledger identities
join. No forced fresh-eye review, handoff update, micro-slice record,
installed-host/consumer rollout, push, release, tag, or remote provider action
is included.
