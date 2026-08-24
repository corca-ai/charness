# Worker Boundary Identity Loss Debug
Date: 2026-08-24

## Problem

Four independent lanes appeared recoverable by retrying, narrowing input, or
ignoring ambient files: external workers selected installed Charness 6.4.0
policy after #713 repaired current source; Ceal scope preflight parsed multiline
grep output as a path; canonical Ceal worktrees exposed generated symlinks as
untracked; and each worker opened tracked lesson-session state outside its task
paths. Every apparent recovery changed the stimulus or hid the mismatched owner.

## Correct Behavior

Every worker/helper result must preserve the producer identity the consumer is
authorized to trust: selected skill version, record boundary, generated-artifact
disposition, and parent-owned session. A mismatch or malformed boundary must
return a typed refusal before task work or verdict rendering. A rerun with
changed input is a new observation, not recovery.

## Observed Facts

- Installed 6.4.0 and current source `impl` instructions contain different
  risk-planner invocations; both external workers selected the installed one.
- Ceal preserved the multiline parser failure separately from the later
  exact-token scope result.
- Canonical Ceal lane creation produced expected links and a non-clean status
  inventory naming those same link entries.
- Worker lesson receipts and ledger diffs exist despite those paths not
  belonging to either assigned implementation slice.

## Reproduction

Read current and installed `impl/SKILL.md` side by side; pass a multiline/path-like
seed through Ceal's CLI grep boundary; create a Ceal lane with the canonical
launcher and read porcelain status; then compare each worker worktree against its
assigned path list. These reproduce version skew, malformed record parsing,
generated-link noise, and ambient lesson-state writes without retrying a provider
operation.

## Candidate Causes

- Independent transient tool failures: disconfirmed because stable local files,
  parsers, symlink policy, and session writers reproduce the failures.
- Human retry mistakes: disconfirmed as root cause; retries only changed the
  stimulus or hid the mismatched owner.
- Boundary identity loss: confirmed because each consumer lacks a binding to
  producer version, record framing, generated-file disposition, or parent
  session identity.

## Hypothesis

The four failures share one structural cause: coordination and proof surfaces
carry values but omit the identity needed to join them to the intended consumer
and lane. Cheapest disconfirmer: prove current source was selected, grep records
were unambiguous, generated links were ignored as entries, or workers inherited
one parent session without tracked lane writes. None held.

## Verification

Current-vs-installed file readback, the captured parser failure, post-wire
porcelain status, and worker ledger diffs each confirmed the missing binding at
its respective boundary. Explicit repository issue readback also confirmed the
four structural trackers were created: Charness #715/#716 and Ceal #733/#734.

## Root Cause

A producer's output, version, scope, and lifecycle identity is not carried to
the final consumer. Installed selection is implicit; grep presentation is
treated as records; launcher and ignore policy have no joined readback; and the
handoff treats every worker as the canonical lesson-session owner. Retrying does
not repair any of these ownership gaps.

## Prevention

Bind worker receipts to selected skill/version; use record-safe framing and
typed malformed-record refusal; make generated worktree artifacts part of one
launcher/ignore/status contract; and let one parent own lesson-session state
while workers inherit immutable identity or use explicitly lane-local storage.

## Invariant Proof

- Invariant: producer version, record framing, generated-artifact disposition,
  and session identity remain bound to the intended consumer/lane.
- Producer Proof: installed/source skill bytes, Ceal grep producer, lane linker,
  and lesson writers identify the four actual producers.
- Final-Consumer Proof: worker stop receipts, scope-preflight exit, porcelain
  inventory, and integration worktree diffs show what each consumer received.
- Interface-Shape Sibling Scan: the same missing join occurs across version,
  record, filesystem, and lifecycle interfaces rather than one file format.
- Non-Claims: the follow-up implementations are not complete, and scoped reruns
  do not prove installed adoption or repair the original malformed input.

## Detection Gap

Source/plugin parity omits installed selection; scope tests omit CLI record
framing; lane-worktree tests omit post-wire status; and worker acceptance omits
forbidden lesson-ledger paths. The smallest firing tests are installed readback,
a captured multiline record, clean porcelain after wiring, and an assigned-path
diff invariant for lesson state.

## Sibling Search

- Mental model: a boundary transports a value while dropping the producer/lane
  identity needed by the final consumer.
- Same layer: Charness #634/#670/#679 and Ceal #417 show installed/exported
  consumer skew | decision: valid follow-up | proof: explicit issue reads |
  follow-up: Charness #715.
- Cross-file: Charness #639/#617 show lesson receipt durability crossing actor
  ownership | decision: valid follow-up | proof: issue and writer-path reads |
  follow-up: Charness #716.
- Cross-repo: Ceal parser and launcher policies are separate owners with no
  final readback | decision: valid follow-up | proof: source/tests/status |
  follow-up: Ceal #733 and #734.

## Seam Risk

- Interrupt ID: worker-boundary-identity-2026-08-24
- Risk Class: external-seam, repeated-symptom
- Seam: producer output/version/state -> lane transport -> final consumer
- Disproving Observation: an exact producer identity and record/artifact/session
  binding reaches each final consumer and the four regressions remain green.
- What Local Reasoning Cannot Prove: installed host refresh, future Ceal lane
  state, or cross-process lesson reconciliation before those trackers land.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes — separate issue resolution critiques own each repair.
- Next Step: spec
- Handoff Artifact: charness-artifacts/debug/2026-08-24-worker-boundary-identity-pattern.md
