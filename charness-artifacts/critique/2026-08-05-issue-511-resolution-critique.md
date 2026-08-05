# Issue #511 resolution critique
Date: 2026-08-05

## Decision Under Review

Issue #511 repairs the nose clone inventory's default scope and final quality
receipt: missing roots are disclosed, configured/explicit roots are resolved,
and non-scan states cannot appear as measured PASS.

## Failure Angles

- A partial or inapplicable scope could still be represented as clean because
  family counts and the underlying nose exit are zero/green-shaped.
- Adapter-owned paths could escape the repository, or an invalid adapter could
  override an explicit operator path.
- The optional inventory helper fallback and source/plugin export could still
  render a missing capability as PASS or drift across hosts.

## Counterweight Pass

- The first implementation review found real blockers in explicit-path
  precedence, missing-helper fallback, and Windows-form traversal; all were
  repaired with focused regressions.
- The second repaired-surface review confirmed the first two repairs and found
  one final Windows-root (`\\windows-root`) vector. The root guard and test were
  added after that capped round and are recorded accepted-unreviewed; no third
  fresh-eye round is claimed.
- Broader redesign of `dup_ratchet_scan.py`, a hard duplication floor, and a
  private consumer roundtrip were rejected as overreach for this issue.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/inventory_nose_clones.py:136 | action: fix | note: Scope must be resolved before `nose`; requested/scanned/missing paths and `scope_status` now travel through JSON and summary.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:457 | action: fix | note: Only phase status `pass` enters measured scope; unproven inventory outcomes become `unproven_subjects`.
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/quality_adapter_lib.py:280 | action: fix | note: Adapter roots reject POSIX and Windows absolute, rooted, drive, and parent-traversal forms; explicit `--path` overrides invalid adapter scope.
- F4 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/dup_ratchet_scan.py:197 | action: defer | note: The configured ratchet scope is a separate contract and does not justify broad scanner redesign here.

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye review.
- Requested spawn fields: unnamed one-shot; model `gpt-5.6-terra`; reasoning
  `medium`; `fork_context: false`.
- Host exposure state: applied
- Application state: host-confirmed: `multi_agent_v1` returned completed
  findings for the delegated causal review, contract critique, first
  implementation round, and second repaired-surface round.
- Delivery state: findings-received; reviewer boundaries were verified clean
  for each review window before parent repairs.

## Fresh-Eye Satisfaction

parent-delegated; four bounded reviewer contexts read
the diagnosis/contract or repaired implementation, and the final capped round's
accepted-unreviewed root repair is visible above.

Fresh-eye pass: skills/public/quality/scripts/nose_inventory_scope_lib.py — the
bounded contract and repaired-surface reviews walked the scope, non-scan, query,
and receipt branches; the final root guard remains accepted-unreviewed under the
two-round cap.

## Boundary Ownership

- Producer: `inventory_nose_clones.py` and the quality adapter own scope
  resolution and diagnostic status.
- Consumer: `run-quality.sh` owns phase/receipt classification and measured-scope
  eligibility.
- Verdict: owned-correctly for the local reconstructed contract.

## Non-Claims

- No private consumer repository, installed plugin cache, provider roundtrip, or
  remote CI behavior is claimed by this critique.
