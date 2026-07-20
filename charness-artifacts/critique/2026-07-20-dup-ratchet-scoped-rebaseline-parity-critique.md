# Critique Review
Date: 2026-07-20

## Decision Under Review

Fixing the #448-reported disagreement between the dup-ratchet gate's evaluate
path and its scoped re-baseline path. Evaluate judged
`live - baseline - intentional - reductions`; the scoped accept refused
everything in raw `live - updated`, so the exact rotations evaluate suggested
were refused whenever overlay-`intentional` families or membership reductions
were live. The slice:

- `dup_ratchet_lib.py`: new pure `scoped_rebaseline_exemptions` (exempts
  overlay-intentional families and unnamed membership reductions, builds the
  evidence lists and advisory lines); `plan_scoped_rebaseline` gains
  keyword-only `exempt_live_ids` excluded from `refused_added`.
- `check_dup_ratchet.py`: `_scoped_rebaseline` wires the exemptions and reports
  `ignored_intentional` / `unnamed_reductions` plus advisories; exempt ids are
  never absorbed into the written baseline.
- `dup_ratchet_scan.py`: shared preamble `live_scan_for_rebaseline` extracted
  (used by `_write_baseline` and `_scoped_rebaseline`) after the repo's own
  clone gate flagged the two functions as a new family and the CLI file crossed
  its hard length cap; the extraction removed the clone instead of accepting it.
- Regression tests in `tests/quality_gates/test_dup_ratchet_scoped_rebaseline.py`;
  operator reference `references/dup-ratchet.md` scoped-mode sentence updated.

Diff scope: 4 canonical files + plugin mirrors; no evaluate-path behavior
change; all error-path `status`/message contracts preserved (verified).

## Execution

Three bounded angle reviewers (Jackson problem-framing, Weinberg diagnostic,
Gawande operational) plus one separate counterweight, all spawned as typed
read-only `bounded-reviewer` subagents in the shared worktree. Rail-1
`reviewer_boundary_fingerprint` snapshot/verify ran around the angle phase and
the counterweight phase; both verifies returned `ok: true`, `drift: []`.
## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: none — the adapter's `high-leverage` mapping is the
  Codex host contract; on this Claude Code host the per-host split uses typed
  `bounded-reviewer` with session-model inheritance (not a degradation).
- Host exposure state: host-defaulted
- Application state: not-applied (session-model inheritance; no per-spawn
  model/effort fields sent)

Fresh-Eye Satisfaction: parent-delegated
Target: code critique (`references/code-critique.md`)

Packet Consumed: charness-artifacts/critique/2026-07-20-115343-packet.md

## Reviewed Input Identity

- Packet path: charness-artifacts/critique/2026-07-20-115343-packet.json
- Packet sha256: b11d3ed1f140d81bb89afd31507d074e91ab26fd52743adea8851eb6df59ee14
- Identity sha256: f1d05d60f60956f92b3718713dbf2c4dd94602c2a6208e36a36e7373a5f639a4
- Note: the angle/counterweight reviewers consumed the pre-fix packet
  (`2026-07-20-111813`); the packet was re-rendered after applying only the
  reviewer-prescribed bundle edits (reference-doc sentence, docstring caveats,
  over-swallow test), so the delta between the two identities is exactly the
  review's own output.

## Failure Angles

- Problem framing: same-universe parity actually achieved vs an adjacent
  convenience; scope of the resolution claim vs the issue's
  fingerprint-normalization hypothesis; refactor scope creep.
- Diagnostic: cause-layer placement (planner purity, scan-module ownership),
  exemption/rotation interaction edges, scan-before-baseline reordering,
  refusal arithmetic with exemptions.
- Operational: silent failure modes (overlay unreadable), advisory clarity,
  typed status contract stability, JSON consumer compatibility, recovery path.

## Counterweight Pass (four-bin triage)

- Act before ship | D: narrow the closeout claim — the fix resolves
  within-invocation family-universe parity only; the wrapper-side
  cached-inventory / fingerprint-normalization hypothesis in #448 is untouched,
  and cross-invocation drift or an OLD-still-live rotation can still refuse.
  Applied: commit/issue wording carries the residuals; #448 stays open pending
  consumer re-verification.
- Act before ship | G: `references/dup-ratchet.md` still said scoped mode
  refuses "any other live delta" — now factually wrong on an operator surface.
  Applied: exemption sentence added; authoring preflight run.
- Bundle | C1: over-swallow guard test added
  (`test_inproc_scoped_rebaseline_refuses_genuine_new_alongside_exemptions`):
  genuine-new refused while intentional + reduction stay exempt, baseline
  untouched.
- Bundle | F: "same family universe" docstrings qualified with "(given
  readable overlay/baseline inputs)" in the CLI and lib.
- Over-worry (confirmed, no change): scan-before-baseline reorder (reordering
  back would un-share the extracted preamble to optimize a rare error path);
  set-precedence at the `ignored_intentional` line (independently verified
  mathematically equivalent by two reviewers); advisory wording divergence
  between paths; rollback-hint absence (bounded write, recoverable via git).
- Valid but defer | A: overlay missing/unreadable during a scoped accept
  silently disables the intentional exemption (fails closed — refusal, never
  absorption; an advisory line is a parity nicety).
- Valid but defer | B: the refused early-return drops the computed exemption
  advisories; they reappear on the next successful run.
- Valid but defer | C2: no test for explicit `--accept-family` of an
  overlay-intentional id (explicit-operator-intent-wins absorb path).

## Deliberately Not Doing

- Not reordering the baseline-readability check ahead of the shared scan
  preamble; both-fail message precedence flip noted here instead.
- Not claiming #448's fingerprint-normalization hypothesis resolved; the Ceal
  wrapper should re-verify against the released fix before closure.
- Not blocking explicit `--accept-family` of an intentional id; explicit
  operator naming wins over the passive exemption by design.

## Boundary Ownership

Producer/consumer brief (diagnostic angle): the exemption policy (which
classes the gate tolerates) lives in the pure `dup_ratchet_lib` next to
`evaluate`'s own universe math, the subprocess/scan preamble lives in
`dup_ratchet_scan`, and the CLI stays the integration seam that wires adapter
config into both. The exemption is computed from the same `overlay_intentional`
/ `classify_reductions` producers the evaluate consumer already uses, so the
two consumers cannot drift within one invocation.

- Verdict: owned-correctly

## Defect Class Cross-Link

Producer/consumer universe drift between two paths reading "the same"
inventory is the disconfirmer-scope class in
`charness-artifacts/retro/recent-lessons.md` Repeat Traps (a check whose scope
does not match the claimed universe); the parity fix pins both paths to the
same helpers over the same inputs.

## Pre-Merge Action

Both act-before-ship items are applied in this slice (claim narrowing in
closeout wording; reference-doc sentence fixed + preflighted). Deferred items
A/B/C2 are recorded above; none blocks merge.

## Next Move

Sync mirrors (done), locked slice closeout with mutation coverage producer,
commit with the narrowed #448 wording, then comment on #448 naming the fix,
the residual hypotheses, and the consumer re-verification ask.
