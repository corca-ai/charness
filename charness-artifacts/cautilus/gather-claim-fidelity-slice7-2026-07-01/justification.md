# Operator Log — gather claim-fidelity capture (reference-compaction Slice 7)

- source-kind: operator-log

## Approval

- Operator (bae.hwidong@corca.ai) authorized this Cautilus capture on 2026-07-01
  with the session request "@docs/handoff.md sweep 시작. 코틸려스 실행 허용" and a
  follow-up "continue". This is the log-backed behavior-proof request the
  ask-before-run policy requires: `plan_cautilus_proof.py --repo-root . --json`
  returns `next_action: "none"`, `must_ask_before_running: true`, `run_mode: ask`
  (gather is captured read-only at HEAD), so this log is the operator-log override.

## Basis under test (Slice 7 gather floor: RCF-doc-open → emitted access-mode)

- reference-compaction Slice 7 (#410) moves the gather claim-fidelity floor off
  the re-read proxy. Current `requiredCommandFragments=[source-priority.md,
  capability-contract.md]`. The plan KEEPS source-priority.md as the routing floor
  and moves capability-contract.md's floor role to an emitted access-mode token
  (the `Access Mode` closeout field, whose canonical enum
  grant/binary/env/public/human-only/degraded lives in capability-contract.md
  `## Access Modes`). The claim under test: does a representative
  `/charness:gather` run on a public URL EMIT a canonical access mode in its
  closeout, so the emitted-token floor is genuinely forced? The token is OBSERVED
  from THIS capture, not assumed.
- OBSERVE-FIRST decision: this capture runs gather UNCHANGED at HEAD. If the run
  emits a canonical mode (e.g. `public`) from the SKILL.md Output-Shape field +
  general knowledge WITHOUT opening capability-contract.md, the doc-open is a
  wasteful re-read and the move is a create-cli-style spec-only change (no SKILL.md
  lift). If the run emits only vague phrasing, the Access Modes enum must first be
  lifted into gather SKILL.md `## Closeout Vocabulary` before the floor moves.

## Honest reading guard

- `public` is a common word in gather's domain; if the emitted mode token proves
  too weakly discriminating, the retained source-priority.md RCF floor carries the
  routing proof and the finding is recorded — never soften the matcher.
- gather has NO outcome-assertions.json (no substance judge), so the emitted-mode
  token is a FORM floor carried by the retained source-priority.md floor.
- gather's first live claim-fidelity capture (was a HYPOTHESIS floor).
