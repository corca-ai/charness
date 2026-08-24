# Issues 690/691 Debug — goal readiness and terminal state
Date: 2026-08-24

## Problem

Scope: [#690](https://github.com/corca-ai/charness/issues/690), [#691](https://github.com/corca-ai/charness/issues/691). No separate JTBD label was supplied; the following issue `What` text is each JTBD verbatim.

**#690 JTBD (verbatim):**

> `--pursue-ready` reports a goal artifact as shaped and ready to pursue when
> entire required sections are present as headings but empty of content.

**#691 JTBD (verbatim):**

> The `achieve` goal contract accepts `draft` / `active` / `blocked` / `complete`.
> There is no terminal status for a goal that ended without completing — one that
> was superseded, folded into a successor, or abandoned with its remainder handed
> on.

## Correct Behavior

Readiness must distinguish present from written, name hollow sections, and refuse shaping-time hollow content while allowing justified run-filled `N/A` sections. A terminal `superseded` record must not be offered as pursuable; readiness, full validation, installed Charness, and Ceal must agree. `superseded` needs an honest successor-or-reason record.

## Observed Facts

- Source defines `active|blocked|complete|superseded` as non-shaping and `complete|superseded` as terminal (`goal_artifact_pursue.py:59-67`), but hollow evaluation is conditional on shaping status (`:291-310`).
- Ceal is not at `../ceal`; read-only checkout: `/home/hwidong/codes/ceal`. It has no copied checker; its wrapper resolves installed Charness 6.4.0, which matches source (`diff -u`, exit 0).

## Reproduction

1. Current source command on the historical active goal exits 0 with all readiness fields true, but `hollow_sections.evaluated: false` because status is `active`; installed 6.4.0 matches it.
2. The same command on the current `superseded` goal exits 0 with `pursue_ready: true` and `activation_ready: true`, while full validation rejects a missing `Superseded by:` record.
3. A read-only Ceal invocation likewise emitted readiness true while its full check refused the terminal record; Ceal’s status drift accepted 10 superseded artifacts.

## Candidate Causes

- Status-scoped hollow evaluation silently misses active legacy content (verified; local payload proof).
- `--pursue-ready` returns without `check_goal`; terminal status and `Superseded by:` are not refusal invariants (verified; source/Ceal CLI).
- Package drift is disconfirmed for the tested module (`diff` exit 0).
- Ceal’s status gate accepts terminal statuses without readiness parity (verified; runtime/provider roundtrip).
- Run-filled emptiness is legitimate before execution; it does not explain terminal readiness true.

## Hypothesis

The root is conflating “shaping floors no longer apply” with “this artifact may be pursued.” `superseded` skips draft floors, but `activation_ready` has no terminal refusal and the CLI bypasses the full contract. No cross-consumer invariant binds Ceal’s terminal vocabulary.

disconfirmer: diff source versus installed plugin, run identical historical/superseded bytes through readiness and full validation, and run Ceal’s status gate; these were executed above. A source/install mismatch or a readiness result that already refuses terminal goals would disconfirm this hypothesis.

## Verification

Cheapest disconfirmers: package diff (identical); historical replay (hollow active accepted); terminal replay (superseded accepted); full-vs-readiness comparison (different); focused tests (green, no boundary coverage). Five whys: (1) goal called ready; (2) hollow is skipped and terminal is absent from `activation_ready`; (3) floor scope has no pursuability predicate; (4) readiness is an early-return branch; (5) no producer/signal/transport/final-consumer contract binds status to activation. Structural missing invariant/gate, not human error or race.

## Root Cause

Shared mental model: “non-shaping” means “do not grade,” while consumers read `pursue_ready` as “safe to activate.” Vocabulary exists, but not the invariant that terminal is non-pursuable and every signal shares one contract. The old empty section proves #690’s historical gap; superseded replay proves #691’s current contradiction.

## Invariant Proof

- Invariant: When Charness emits `pursue_ready`/`activation_ready`, the final consumer must not surface hollow or terminal work as pursuable; status/readiness gates must agree.
- Producer Proof: `pursue_readiness` emits true for historical active hollow and current superseded goals; `check_goal_artifact.py:162-170` returns it directly.
- Final-Consumer Proof: installed Ceal invocation emits true for superseded while full validation rejects missing `Superseded by:`; Ceal status drift independently passes 10 superseded artifacts.
- Interface-Shape Sibling Scan: producer signal → installed plugin transport → Ceal goal/status consumer; `check-goal-status-drift.ts:15-19` recognizes `superseded` but proves no readiness parity.
- Non-Claims: no `/goal` agent activation, host runtime execution, release/public readback, provider/live proof, Ceal mutation, or GitHub mutation was run. The absent `../ceal` path was not substituted silently.

## Detection Gap

- Public readiness gate | terminal refusal did not fire | add one superseded fixture through the CLI and assert `pursue_ready=false` or an explicit terminal/non-pursuable verdict.
- Hollow classifier integration | active legacy hollow sections were not evaluated | add an active hollow fixture and assert `hollow_sections.evaluated=true` or an explicit grandfathered contract.
- Full/readiness parity | missing `Superseded by:` was invisible to `--pursue-ready` | run both public modes on one fixture and assert the relationship.
- Duplicate-heading parity | readiness reduced required/portability H2 headings to a set while full validation refused duplicate sections | consume the canonical markdown duplicate report in readiness and assert substantive required/portability duplicates through both public CLIs.
- Consumer seam | Ceal status drift can pass beside Charness rejection | add a read-only installed-plugin/Ceal adapter parity check; smallest firing signal is a disagreeing status/readiness result.

## Sibling Search

- Same layer: `goal_artifact_pursue.py` and `goal_artifact_lib.py`; decision: `same class, diagnostic-only for this slice`; proof: `local payload proof`.
- Abstraction up: Ceal’s status drift versus Charness status/readiness contract; decision: `same class, diagnostic-only for this slice`; proof: `runtime/provider roundtrip`; no action required in diagnosis; follow-up: deferred issues-690-691-goal-readiness-causal-review.
- Specialization down: `check_goal_artifact.py --pursue-ready` early return versus full `check_goal`; decision: `same bug, fix now` for a future implementation slice; proof: `local payload proof`.
- Mental-model sibling: Ceal’s 2026-06-03 pursue-ready discussion-gate incident; decision: `same class, diagnostic-only for this slice`; proof: `local payload proof`.
- #698 Auto-Retro/disposition floor: decision: `valid follow-up outside the slice`; proof: `local payload proof`; follow-up: https://github.com/corca-ai/charness/issues/698
- cross-file: `/home/hwidong/codes/ceal/scripts/check-goal-status-drift.ts` and `skills/public/achieve/scripts/check_goal_artifact.py`.

## Seam Risk

- Interrupt ID: issues-690-691-goal-readiness-2026-08-24
- Risk Class: external-seam, repeated-symptom
- Seam: source readiness → installed Charness plugin → Ceal final consumer
- Disproving Observation: a source/install diff or a terminal readiness refusal; neither occurred.
- What Local Reasoning Cannot Prove: actual `/goal` activation behavior and hosted/public readback.
- Generalization Pressure: factor-now

## Interrupt Decision

- Critique Required: yes — a separate causal reviewer must review root cause and bundle/defer boundary before spec or implementation.
- Next Step: factor-first
- Handoff Artifact: `charness-artifacts/debug/2026-08-24-issues-690-691-goal-readiness.md`
- Resolution: resolved; the accepted-unreviewed capped repair now refuses
  substantive duplicate required/portability H2 sections through the shared
  markdown duplicate owner. The earlier round-2 packet used `changed_ref: HEAD`
  and did not cover the repaired working tree; the parent must regenerate a
  working-tree-bound packet.

## Prevention

Keep #690/#691 bundled: they share the readiness producer, lifecycle signal, and Ceal consumer seam, with both historical and current evidence. Defer #698: it concerns the separate disposition/Auto-Retro floor and would widen proof-surface scope. The duplicate-heading repair reuses the canonical markdown duplicate owner and is covered by substantive source/plugin CLI fixtures. The two-round fresh-eye cap is consumed, so this repair is accepted-unreviewed; no third review is claimed. The earlier reviewer packet measured `goal_artifact_pursue.py` at 339 code lines; the current working tree measures 355 after this blocker addition and remains below the hard limit. The reviewer-identified Closeout Binding Plan parsing extraction is a concrete deferred follow-up for parent issue tracking, not part of this repair.
