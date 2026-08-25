# Adversarial Consumer Boundary Review
Date: 2026-08-25

## Decision Under Review

Approve the second-round structural hardening of the #715–#721
producer-to-consumer proof boundary: degraded lineage refusal, typed JUnit
fixture proof, registry-owned trigger closure, exported anchor checks, and
pre-push refusal when provenance proof is unavailable.

## Failure Angles

- False approval when degraded duplicate inputs collapse to an empty ready set.
- Pytest skip, xfail, xpass, namespace, timeout, or zero-test states being read
  as executable proof.
- Dependency-helper edits, package removal, or path traversal bypassing the
  commit/package boundary.
- Artifact prose claiming a fresh count or runtime proof that was not bound to
  the executed receipt.

## Counterweight Pass

- The duplicate consumer still owns `lineage_approval_eligible`; the registry
  supplies trigger closure and obligation metadata rather than calculating its
  domain verdict.
- Plugin proof is deliberately split: mapped consumer anchors are checked,
  final-consumer pytest execution remains an explicit non-claim.
- JUnit parsing treats parameterized cases as one named fixture family, but any
  skipped/failing/errored case refuses the proof.
- `required_fields` and `refusal_code` remain an audit index backed by
  consumer-owned fixtures, not a claim of generic runtime enforcement.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `skills/public/quality/scripts/check_dup_ratchet.py` lineage eligibility | action: fix | note: degraded inputs previously became ready; now eligibility requires an established scan and has a refusal message.

- F2 | bin: act-before-ship | evidence: strong | ref: `skills/public/quality/scripts/check_provenance_contract.py` JUnit parser | action: fix | note: return code alone admitted skipped/xfail; structured testcase outcomes, namespaces, xpass, timeout, and zero-test cases are now typed.

- F3 | bin: act-before-ship | evidence: strong | ref: `skills/shared/scripts/provenance_contract.py` trigger_paths and `scripts/staged_commit_gate_plan.py` | action: fix | note: trigger closure is registry-owned and includes delivery, lesson, capability, duplicate helpers, fixtures, and mirrors.

- F4 | bin: act-before-ship | evidence: strong | ref: plugin anchor validator and `scripts/run-quality.sh` | action: fix | note: unsafe plugin paths refuse; mapped anchors are checked; missing checker refuses at pre-push instead of looking green.

- F5 | bin: valid-but-defer | evidence: moderate | ref: spec/artifact test-count claims | action: document | note: exact focused command is recorded; standing count is delegated to the canonical runner receipt rather than copied prose.

- F6 | bin: valid-but-defer | evidence: moderate | ref: registry `required_fields`/`refusal_code` | action: document | note: metadata-only rows are an intentional non-claim; future rows need consumer-owned executable fixtures or adapters.

## Reviewer Tier Evidence

- Requested tier: high-leverage read-only bounded reviewer.
- Requested spawn fields: unnamed read-only context with inherited host controls.
- Host exposure state: metadata-hidden
- Application state: host accepted distinct reviewer contexts; provider settings were not independently observable.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

accepted-unreviewed-under-round-cap two-round-verdict — two independent angle
reviews and a separate counterweight delivered findings. The counterweight's
repairs were applied after the second verdict-surface round; the operating
contract caps this class at two rounds, so those post-round repairs are not
claimed as a third fresh-eye approval.

## Reviewed Input Identity

No prepare packet was consumed. The reviewers read the live current surface;
no packet-byte or installed-host identity claim is made.

## Boundary Ownership

- Producer: duplicate scans, worker receipts, pytest fixtures, package exports, and canonical runner receipts.
- Consumer: duplicate verdict, provenance checker, staged gate, plugin anchor checker, and closeout artifact.
- Owning surface: producer-to-final-consumer contract registry plus each domain consumer's verdict logic.
- Verdict: owned-correctly

## Deliberately Not Doing

- No GitHub issue mutation, push, release, or Ceal/Claude live-host roundtrip.
- No claim that registry metadata alone enforces every domain refusal.
- No third fresh-eye round beyond the operating-contract cap.

## Next Move

Run the canonical standing gate after mirror synchronization, run the focused
contract command, verify the boundary fingerprint is clean, and commit only
after the receipts and non-claims are synchronized.
