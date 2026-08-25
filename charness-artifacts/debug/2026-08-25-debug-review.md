# Consumer Boundary Invariant Debug Review
Date: 2026-08-25

## Problem

The second fresh-eye review found four defects after the #715–#721 repair:
failed worker outcomes could bypass the lesson write-fence, producer output/
receipt/run-id joins were optional to the final reviewer consumer, malformed
candidate manifests could escape typed refusal, and duplicate-lineage
readiness was diagnostic while the gate could remain green.

## Correct Behavior

When any producer emits a result, lifecycle outcome, manifest candidate, or
lineage readiness signal, its final consumer must consume the bound identity and
refuse an approval/readiness claim when required evidence is absent. This must
hold for every terminal worker outcome, not only success.

## Observed Facts

- `skills/shared/scripts/reviewer_runner_support.py` owns lesson validation, but
  the receipt-specific lane check is conditional on `status == succeeded`.
- `skills/shared/scripts/reviewer_worker_report.py` now rejects missing producer
  joins, but the delivery model still exposes those fields as optional and the
  rule is local to one consumer.
- `scripts/capability_catalog_resolver.py` needed explicit catches for invalid
  UTF-8/non-object candidate manifests after the review exposed the untyped
  parse boundary.
- `skills/public/quality/scripts/check_dup_ratchet.py` exposes
  `lineage_approval_eligible`, while the lineage contract remains a separate
  diagnostic surface.

## Reproduction

Remove one producer binding from a hand-authored delivery ledger; make a worker
receipt fail while adding a parent lesson mutation; supply an invalid-UTF-8
candidate `.codex-plugin/plugin.json`; or remove baseline member paths from a
duplicate family. Each input previously reached a local helper or a green
diagnostic path before the final consumer had a complete invariant.

## Candidate Causes

- A transient worker or malformed file was treated as the primary problem.
- Each fix was added to the nearest function, so the same boundary rule was
  represented by optional dict fields and success-only branches.
- Producer, transport, and final-consumer contracts were not represented in one
  executable matrix, and tests emphasized successful producer output rather
  than adversarial terminal states and malformed inputs.

## Hypothesis

The defects recur if the repository lacks one executable producer-to-final-
consumer invariant contract. If a contract registry names required joins,
all-outcome fences, typed refusal requirements, and readiness-to-approval
rules—and a gate verifies that registry plus representative negative fixtures—
then removing any one of these obligations fails before a reviewer must find it.
Disconfirmer: a registry-backed gate remains green after deleting a required
binding or changing a non-success outcome to bypass the fence.

## Verification

The four findings were independently reproduced by the second reviewer and
then repaired locally. The focused suite and staged pre-commit passed, but the
review still exposed that the protections were distributed rather than
contract-complete. The hypothesis therefore remains the next structural slice,
not a claim that another local guard is sufficient.

## Root Cause

The structural cause is a missing executable boundary-invariant contract: the
repository had producer helpers and final consumers, but no single durable
declaration or gate that required every producer identity, every terminal
outcome fence, every malformed-input refusal, and every readiness limitation to
be carried through to the consumer that owns success. Issue-by-issue repairs
therefore made the observed paths correct while leaving omission paths easy to
write and hard to detect.

## Invariant Proof

- Invariant: when a boundary producer emits identity/evidence/readiness, the
  final consumer must surface or refuse it before success.
- Producer Proof: reviewer receipts, lesson snapshots, candidate manifests,
  and duplicate-ratchet verdict payloads are the four observed producers.
- Final-Consumer Proof: reviewer worker report, lesson finalization, skill
  selection, and duplicate-ratchet verdict consumers are the owning surfaces;
  the new gate must exercise each with a negative fixture.
- Interface-Shape Sibling Scan: same producer→transport→consumer omission
  appears in `reviewer_delivery_attempt.py`, `lesson_session_boundary.py`,
  `capability_catalog_resolver.py`, and `check_dup_ratchet.py`; decision:
  same class, fix now; proof: local source and focused fixtures.
- Non-Claims: no installed-host, Ceal/Claude provider, GitHub, push/release,
  or Cautilus roundtrip is proven by this local contract.

## Detection Gap

- Focused tests caught the concrete regressions only after a fresh-eye reviewer
  supplied the missing adversarial input. The smallest durable detector is a
  registry-backed contract gate with one negative fixture per boundary row.
- Existing source/plugin parity and lint gates cannot detect a missing row or a
  consumer that stops reading a producer signal; they remain necessary but are
  not sufficient.

## Sibling Search

- Mental model: a local validator is mistaken for end-to-end proof.
- Same layer: the four final consumers above | decision: same class, fix now |
  proof: local payload and consumer tests.
- Abstraction up: `charness-artifacts/spec/2026-08-25-consumer-friction-715-721.md`
  already states the joins separately | decision: same class, fix now | proof:
  contract readback.
- cross-file: `skills/shared/scripts/reviewer_worker_report.py` and
  `skills/public/quality/scripts/check_dup_ratchet.py` | decision: same class,
  fix now | proof: distinct consumers with the same missing-invariant shape.

## Seam Risk

- Interrupt ID: consumer-boundary-invariant-2026-08-25
- Risk Class: repeated-symptom, external-seam
- Seam: producer payload → transport/durable artifact → final consumer verdict
- Disproving Observation: the registry-backed gate can be bypassed while a
  consumer still claims approval/readiness without its required evidence.
- What Local Reasoning Cannot Prove: installed host selection and live provider
  behavior.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-25-consumer-boundary-invariants.md

## Prevention

Create one typed, durable boundary-invariant registry consumed by a deterministic
quality gate. Require each row to name producer, final consumer, required joins,
terminal-outcome policy, refusal code, and a negative fixture. Make the affected
consumers call shared binding/readiness helpers, and keep source/plugin copies
in parity. This prevents the next repair from stopping at a local symptom.
