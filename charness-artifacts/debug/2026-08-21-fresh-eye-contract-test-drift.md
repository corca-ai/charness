# Debug Review
Date: 2026-08-21

## Problem

The changed-line proof for the R2 reviewer-worker slice returned `no-verdict`:
the producer ran 909 focused tests and one existing contract pin failed. The
failure was caused by the shared fresh-eye reference no longer containing the
explicit no-same-agent wording pinned by that test.

## Correct Behavior

The shared contract, its plugin mirror, and its pinning tests must agree that a
file-backed worker is the canonical fresh-eye path, typed subagents are an
optional host adapter, and neither path may be replaced by a same-context
review. A contract wording refactor must preserve that invariant or update the
test and contract together with equivalent strength.

## Observed Facts

- `prepush_focused_changed_line_coverage.py --base-sha 825b2a419...`
  reported `908 passed, 1 failed` and deliberately emitted no verdict.
- The failing test is
  `tests/quality_gates/test_subagent_delegation_ladder.py::test_ladder_does_not_loosen_what_counts_as_proof`.
- The test pins `Do not silently collapse into a same-agent review`; the
  source reference had only the semantically related `same-context` wording.
- `skills/shared/references/fresh-eye-subagent-review.md` and
  `plugins/charness/shared/references/fresh-eye-subagent-review.md` are the
  same contract surface after mirror synchronization.
- `skills/public/critique/SKILL.md` and `skills/public/prove/SKILL.md` already
  consume this shared boundary and describe the file-backed worker default,
  optional typed-subagent path, typed delivery, and no same-context proof.

## Reproduction

Before the repair:

`python3 -m pytest -q tests/quality_gates/test_subagent_delegation_ladder.py::test_ladder_does_not_loosen_what_counts_as_proof`

fails on the missing literal. The smallest reproduction is the assertion
against the shared reference at `test_subagent_delegation_ladder.py:555`.

## Candidate Causes

- Contract-edit cause: the 9b4ee5d40 default-worker rewrite changed a pinned
  phrase without preserving an equivalent explicit marker.
- Mirror cause: source and plugin reference could have diverged during sync.
- Semantic weakening cause: the rewrite might have removed the no-substitute
  rule rather than merely changing its words.

## Hypothesis

The primary cause is contract/test wording drift, not a weakened runtime rule.
Disconfirmer: inspect both mirrors and the critique/prove consumers, then run
the smallest pinned test after restoring an explicit same-agent prohibition.

## Verification

- Confirmed: the source and mirror had the same `same-context` rule, while the
  test alone required the missing explicit `same-agent` marker.
- Confirmed: critique and prove still route through the shared reference and
  retain the stronger worker/receipt/no-same-context semantics.
- Confirmed after repair: the shared reference now says
  `Do not silently collapse into a same-agent review (a same-context local pass)`;
  the plugin mirror is synchronized and the pinned test passes.

## Root Cause

The canonical contract was refactored at the authorization/execution boundary
but its wording-preservation test was treated as a phrase detail. That made a
proof-surface gate fail after the implementation was otherwise correct and
prevented a changed-line verdict. The structural defect was lack of an explicit
semantic pin at the shared contract location during the default-runner
migration.

## Invariant Proof

- Invariant: a fresh-eye verdict requires a separate worker or explicitly
  selected typed-subagent context and never a same-context substitute.
- Producer Proof: the focused changed-line producer and the ladder test assert
  the shared contract's authorization/proof distinction.
- Final-Consumer Proof: `prepush_focused_changed_line_coverage.py` refuses to
  render a verdict when that contract test fails.
- Interface-Shape Sibling Scan: `skills/public/critique/SKILL.md` and
  `skills/public/prove/SKILL.md` consume the same shared reference; both retain
  the worker/receipt boundary.
- Non-Claims: this repair does not prove a host typed-subagent run, external
  provider behavior, release publication, or issue closure.

## Detection Gap

- `tests/quality_gates/test_subagent_delegation_ladder.py` fired, but the
  changed-line proof was run only after commit-level closeout gates, so the
  workflow had already spent time on a no-verdict run.
- The smallest prevention is to keep the explicit semantic marker in the
  canonical reference and require changed-line proof before broad quality or
  release lanes; the resumed handoff now records that order.
- Mirror synchronization and the ladder test together catch source/mirror and
  wording drift; a future migration should update both before running closeout.

## Sibling Search

- Mental model: proof contracts are executable interfaces; prose refactors can
  silently remove the only reader-visible invariant.
- same layer: `tests/quality_gates/test_subagent_delegation_ladder.py:548-555` |
  decision: same bug, fix now | proof: focused pytest and changed-line producer.
- abstraction up: `skills/public/critique/SKILL.md:22-28` and
  `skills/public/prove/SKILL.md:78-81` | decision: same class, diagnostic-only
  for this slice | proof: static scan plus targeted contract tests; both rely on
  the shared reference and no same-context wording.
- cross-file: `plugins/charness/shared/references/fresh-eye-subagent-review.md`
  | decision: same bug, fix now | proof: mirror sync plus byte/content check.

## Seam Risk

- Interrupt ID: fresh-eye-contract-test-drift-2026-08-21
- Risk Class: none
- Seam: shared fresh-eye contract prose -> pinning test -> changed-line verdict
- Disproving Observation: a future contract rewrite removes the semantic
  prohibition while every consumer and focused gate remains green.
- What Local Reasoning Cannot Prove: host-specific typed-subagent availability
  or external worker delivery semantics.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-21-fresh-eye-delivery-boundary.md

## Prevention

Keep the explicit no-same-agent marker in the shared reference, synchronize its
plugin mirror, and test both execution modes through the common contract. Run
changed-line proof immediately after each verdict-surface repair and before
broad lanes. Record this incident in the RCA ledger so future default-runner
migrations treat contract wording as a structural interface, not cosmetic text.
