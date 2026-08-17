# Resolution Critique — issue 636 resolution
Date: 2026-08-18

## Decision Under Review

Close [#636](https://github.com/corca-ai/charness/issues/636): the scoping half
(`--paths` with a changed-paths default on `validate_debug_artifact.py`) shipped in a
prior slice, and the one-at-a-time case-sensitive marker half shipped this session
(commits `de9bb2fcc`..`85c943e3d`), reviewed by a bounded round before this close.

## Failure Angles

Raised by the bounded round-1 reviewer, not the author:

- **Verdict equivalence under the rewrite.** The collected-report semantics had to
  accept and reject exactly what the fail-fast semantics did. The reviewer walked
  every moved function: each guard reduces to "extraction succeeded", matching the old
  raise-before-check ordering; the `Risk Class: ","` edge is pinned by test.
- **Message-format consumers.** `risk_interrupt_lib` carries its own message copies
  for the closeout consumer (unchanged); no hook or planner parses the validator's
  strings; every test assertion was updated to the new `(found ...)` suffix.
- **Mirror/export integrity.** The reviewer spot-checked the three plugin mirrors
  line-for-line; the parent then proved byte-identity with `diff` (all three
  identical) and the export's `runtime_bootstrap` resolves the new module.

## Counterweight Pass

- Two reviewer minors, neither a verdict change, both recorded rather than churned:
  the current-path Risk Class parse is now a wording-drift twin of
  `risk_interrupt_lib._parse_risk_classes` (enum single-sourcing holds; parse logic
  duplicated — the sharing constraint is documented in `dup-review.json` entries
  `ddff0a325db1a074`/`f628004cc09e5192`), and the DATED path's
  `validate_dated_seam_risk_enums` still fail-fasts internally — dated records were
  explicitly outside #636's current-artifact ask.
- Round 2 is not owed: the operating contract's verdict-surface rule discharges the
  second round when round 1 produces no repairs, which it did not.

## Structured Findings

- F1 | bin: over-worry | evidence: moderate | ref: scripts/debug_interrupt_grammar.py | action: document | note: Risk Class parse wording now drifts from risk_interrupt_lib's copy; enums stay single-sourced (#366), the constraint that blocks sharing (import cycle + artifact_validator at its length cap) is recorded in dup-review.json.
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/debug_interrupt_grammar.py | action: defer | note: the dated-record enum path still reports one problem per run; #636 scoped its ask to the current artifact, so extending collection there is a separate small slice.

## Reviewer Tier Evidence

- Requested tier: high-leverage (verdict-surface change review).
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, no
  model/effort override (session-inherited).
- Host exposure state: applied
- Application state: host-confirmed: typed `bounded-reviewer` spawn accepted and ran
  with the read-only toolset (Read/Grep/Glob only, per its own envelope report).
- Delivery state: findings-received

## Reviewed Input Identity

<!-- No packet was consumed: this critique reviews the committed slice
de9bb2fcc..85c943e3d in the working tree. -->

## Boundary Ownership

- Producer: `debug_interrupt_grammar.py` mints the marker/enum refusals; the taxonomy
  stays minted by `risk_interrupt_lib` and imported (#366).
- Consumer: `validate_debug_artifact.py` renders the artifact verdict; the closeout
  consumer keeps its own independent parse.
- Owning surface: debug artifact validation (scripts layer).
- Verdict: owned-correctly

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded round-1 reviewer over the whole slice; verdict
SHIP-SAFE with zero repairs, so the two-round verdict-surface floor is discharged by
the no-repairs rule. Boundary fingerprint verify around the round: `ok: true`,
`verdict: parent-attributed`, `drift: []` (window w-20260817T231850Z-1008084; the
parent's one in-window write was the 632/631/630 critique artifact, outside this
slice's surfaces).

## Non-Claims

- No claim about the dated-record path's reporting ergonomics (F2, deferred).
- No claim that consuming repos see this before their next plugin upgrade.
