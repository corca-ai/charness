# Issue 759 declaration intersection

Date: 2026-08-30

## Decision Under Review

Whether `#759` — a change range containing deletions having no valid
declaration as bounded-review input — is repaired, and whether closing it is
safe.

## Verification Scope Decision

- Claim under test: a committed range containing deletions can be declared as
  reviewed input, with the identity still bound to the range.
- Changed surfaces: `scripts/reviewed_input_identity.py`,
  `scripts/reviewed_input_nonblob.py`, `scripts/reviewed_input_verification.py`,
  `scripts/surfaces_lib.py`, `scripts/render_critique_section_changed_surfaces.py`,
  `skills/public/critique/scripts/run_review_support.py`,
  `skills/public/critique/references/prepare-packet.md`, and their tests.
- Minimum sufficient proof: the issue's own evidence range (`e3d7aeef0`, 57
  paths, 6 deletions) captures and verifies `current` in both the `--range` and
  `--commit` forms, with recorded hashes byte-identical to the pre-image blobs.
- Deliberately omitted checks: the `e3d7aeef0` real-host-removal delta was NOT
  substantively reviewed; that is a separate obligation recorded in
  `charness-artifacts/release-review/2026-08-30-8.0.0-real-host-removal-surface-lock.md`.
- Verifier contract: `skills/public/critique/scripts/run_review.py`, file-backed
  worker, `codex_exec`. Changed during this series (`run_review_support.py`), so
  treated as suspect and re-run after each change.
- Failure classification: subject-defect
- Negative control: command `run_standing_pytest.py --pytest-target tests/test_reviewed_input_identity_binding.py` | expected refusal `declared reviewed inputs are stale` on a submodule HEAD moved off the index | observed both refusals plus PermissionError propagation | receipt 36 passed
- Subject identity: sha256:f71ae3fd32c17aed97670036d1f46c959a7188932ad9f5f08f3e73cc080a9aeb
- Verifier identity: sha256:124361ca934404c10cc010b46ae9ac97114973a05384a07c7e601e2865caae18
- Input identity: sha256:5798cbb7eae086573ded909b1a41ae0ca53f94bcf3482de0dc015398b563a0b8
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:dc350f41bb3c628dacef6d7cac1d5791a8e0ea90b0270debf205be22735ec4ff

## Failure Angles

- The repair could close the reported symptom while leaving the CLASS open — two
  components answering "what is the reviewed input" differently. A five-lens
  sweep found eight further instances; four root causes, seven repaired.
- A repair could convert a refusal into a silently passing verdict, which is
  worse than the refusal. This happened twice and both were caught.
- A test could share a premise with the defect it guards and pass over a
  constant. This happened three times.

## Counterweight Pass

- Concern: nine review rounds is over-investment for one issue.
  Disposition: each round returned a reproduced defect, several of them
  false-`current` verdicts, which is the failure this machinery exists to
  prevent. Not over-worry.
- Concern: submodule support is unfinished.
  Disposition: valid-but-defer — charness has no submodules, so live impact is zero;
  unprobed states are filed as `#761`.
- Concern: closing `#759` implies the 8.0.0 removal is approved.
  Disposition: act-before-ship — stated as an explicit non-claim in the closing
  comment and in the release record.

## Structured Findings

- CR-759-001 | bin: act-before-ship | evidence: strong | ref: scripts/reviewed_input_nonblob.py | action: fix | note: repaired in e59bc71e7 by catching the absent-directory FileNotFoundError; a function named `_optional` must not raise at its caller.
- CR-759-002 | bin: act-before-ship | evidence: strong | ref: scripts/reviewed_input_nonblob.py | action: fix | note: repaired in dd0b4d17a by narrowing the catch; the blanket form let a PermissionError bind the stale index value and report current.
- CR-759-003 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/release-review/2026-08-30-8.0.0-real-host-removal-surface-lock.md | action: document | note: the closing comment states this is not approval of the e3d7aeef0 removal delta; the reviewer recorded the same non-claim.
- CR-759-004 | bin: valid-but-defer | evidence: moderate | ref: tests/test_reviewed_input_identity_binding.py | action: fix | note: the test now moves the checkout off the index and invokes the public consumer, rather than lowering its claim.

## Reviewer Tier Evidence

- Requested tier: medium
- Requested spawn fields: typed `bounded-reviewer`, session-model inheritance (per-host contract)
- Host exposure state: host-defaulted
- Application state: unverified-by-packet
- Execution mode: file-backed-worker
- Delivery state: findings-received
- Worker report: charness-artifacts/critique/reports/2026-08-30-issue-759-worker-report.yaml
- Worker report identity: c701dd4524e5eb5e7e3f3599fefcdd16d044812ca773e5c3dbef79c42a421cb7
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 6e584f3ec6c12762460e6a5d2eda8c1a7d16ddb7a5a2909b37c48aa9c8053062
- Worker report input identity: 5798cbb7eae086573ded909b1a41ae0ca53f94bcf3482de0dc015398b563a0b8
- Worker report parent receipt identity: parent-40546f2d380771a47263a623c9d3eed12229a01646990a9e
- Worker report findings identity: 9bd68a6e29148be711bda4e3ab540955b2171166049cba1f4461d5dbada82483

## Fresh-Eye Satisfaction

worker-delivered — nine file-backed rounds across `code-critique` and
`release-safety` lenses. Rounds 1-8 returned `block` and every finding was
reproduced before repair. Round 9 returned `pass` with `approval_eligible: true`
and one `low` finding, repaired by strengthening the test rather than narrowing
its claim.

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/review-20260830T084439Z-3456882-packet.json
- Packet SHA256: 6e584f3ec6c12762460e6a5d2eda8c1a7d16ddb7a5a2909b37c48aa9c8053062
- Identity SHA256: 5798cbb7eae086573ded909b1a41ae0ca53f94bcf3482de0dc015398b563a0b8

## Boundary Ownership

- Verdict: owned-correctly

Producer: `scripts/reviewed_input_identity.py` (enumeration, range resolution,
content digests) and `scripts/reviewed_input_nonblob.py` (gitlink and
current-pointer binding). Consumer: `scripts/reviewed_input_verification.py` and
the critique packet path. The split is load-bearing: the shipped reviewer runtime
loads these files by path, so the production half stays a leaf and each sibling
is resolved deterministically rather than through whatever is importable.
