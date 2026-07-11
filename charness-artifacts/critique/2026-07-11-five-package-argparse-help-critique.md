# Critique Review — Five-Package Argparse Help Campaign
Date: 2026-07-11

## Decision Under Review

Clear 20 missing-help findings across five cohesive public-skill packages while
preserving every parser/runtime contract and keeping help owned by each CLI.

## Failure Angles

- Problem fit and boundary honesty: descriptions must match the actual gather,
  handoff, issue, achieve, and impl behavior without claiming unused effects.
- Proof fidelity: usage-line presence must not false-green an option whose own
  description is absent or swapped.
- Packaging: nine public sources and their plugin mirrors must remain identical.

## Counterweight Pass

- Review found one cheap test-claim mismatch: handoff's “all options” test
  omitted the already-documented `--intent`; it was added before closeout.
- Duplicated local help-test helpers are acceptable in this campaign; extracting
  a shared abstraction now would widen ownership and add indirection.
- No snapshot tests, generic parser framework, or new blocking floor are needed.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/test_handoff_plan.py | action: fix | note: add the existing --intent option to the test whose name promises all options; fixed and delta-reviewed.
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/{gather,handoff,issue,achieve,impl}/scripts | action: document | note: all 20 descriptions match their parser owner and preserve choices, defaults, required flags, actions, and modes.
- F3 | bin: bundle-anyway | evidence: strong | ref: plugins/charness/skills | action: document | note: all nine changed public scripts are byte-identical to their packaged mirrors.
- F4 | bin: valid-but-defer | evidence: moderate | ref: tests | action: defer | note: repeated option-block helpers remain local until a broader invariant justifies shared test infrastructure.

## Reviewer Tier Evidence

- Requested tier: high-leverage code and quality campaign review.
- Requested spawn fields: typed `bounded-reviewer`, read-only envelope, and
  distinct problem-fit, proof-fidelity, and counterweight lenses.
- Host exposure state: unsupported
- Application state: host rejected typed `bounded-reviewer` as unknown; three
  default fresh contexts ran envelope-unbound, and parent rail-1 fingerprints
  proved zero worktree/index drift before and after both review rounds.

## Fresh-Eye Satisfaction

nested-delegated — two independent angle reviewers consumed
`charness-artifacts/critique/2026-07-11-085201-packet.md`; a third child ran the
counterweight pass and then approved the handoff-test cleanup delta.

## Boundary Ownership

- Producer: each package's argparse parser produces its own help contract.
- Consumer: operators and agents invoking the five public-skill CLIs.
- Owning surface: each public script, its packaged mirror, and its focused
  executable readback test; no generic cross-package runtime owner was added.
- Verdict: owned-correctly
