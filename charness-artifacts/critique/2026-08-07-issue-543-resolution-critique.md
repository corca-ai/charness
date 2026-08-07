# Issue 543 resolution critique
Date: 2026-08-07

## Decision Under Review

Raising `check-secrets` from 16500 to 19500 in the `local-linux-x86_64-36cpu` profile and
the `default` map, to resolve #543 — a pre-push budget refusal that was blocking a verified
fix from reaching `main`.

## Failure Angles

- **Raising a bar to land your own commit** is the exact move this repo forbids, and it is
  what this change looks like from outside.
- **Picking the smallest passing number**, which re-blocks on the next sample.
- **Stating a false rationale**, which is worse than no rationale: it plants a rule the
  next maintainer re-derives from.
- **Hiding a real future regression** behind the new headroom.

## Counterweight Pass

- This was refused unilaterally and only made after an explicit operator grant. That is
  recorded, and it is the difference between a raise and a bypass.
- Measured first, changed second: standalone the check runs 7.6s against what was a 16.5s
  bar (gitleaks: ~7.1s over 56.48 MB). The bar was never measuring the check's own cost.
- The chosen value is TIGHTER than the profile's documented convention, not looser.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml:393 | action: fix | note: my stated basis was a rationalization. I wrote that 1.10x was "this profile's own existing convention", derived from sibling `check-markdown`. The real convention is 1.4x of the contended max rounded to 500ms — stated in the block header and mechanized as `runtime_budget_sizing_lib.SLACK_SUGGESTION_HEADROOM = 1.4` — which would give 25000. `check-markdown`'s 1.10 is a DECAYED ratio (set at 1.405x of 12098, whose max has since grown to 15469), not a rule. Comment corrected to state the real convention and that 19500 is deliberately tighter.
- F2 | bin: over-worry | evidence: strong | ref: .agents/quality-adapter.yaml:405 | action: document | note: the reviewer checked whether I cherry-picked a flattering sibling and found the opposite — current ratios are `run-evals` 1.23, `doc-duplicates` 1.17, `check-markdown` 1.10; I picked the tightest, i.e. against my own interest
- F3 | bin: valid-but-defer | evidence: strong | ref: .charness/quality/runtime-signals.json | action: file-issue | note: the drift is profile-wide, not specific to this label — `check-markdown` at 1.10 is the next false red, and `check-secrets` moved ~10% within one hour with no code change. Filed as the class rather than waiting for the next label to repeat the cycle | follow-up: https://github.com/corca-ai/charness/issues/544
- F4 | bin: over-worry | evidence: strong | ref: .agents/quality-adapter.yaml:493 | action: document | note: two further `check-secrets` bars (107500, 110000) belong to 4-core profiles derived from a genuine 76.6s measurement; leaving them untouched is correct, and no test, doc, or fixture pins 16500

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (`.claude/agents/bounded-reviewer.md`).
- Requested spawn fields: subagent_type=bounded-reviewer, no host addressing name, session-model inheritance per the per-host split for Claude Code hosts.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported the read-only envelope and returned findings inline.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. One delegated read-only reviewer critiqued the relevel before close, and
its central finding (F1) changed the shipped artifact. Recorded deviation: no separate
causal-review-before-design round — the diagnosis was produced by executed measurement
(standalone timing, the recorded sample window, and four observed push attempts), not by
analysis.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer read the worktree and
`.charness/quality/runtime-signals.json` directly. The binding floor is not turned on. -->

## Boundary Ownership

- Producer: `.agents/quality-adapter.yaml`, which owns the per-profile budgets.
- Consumer: `check_runtime_budget.py`, whose median-based rule gates the push.
- Owning surface: the repo's runtime-budget policy.
- Verdict: single-surface

## Non-Claims

- `check-secrets` was NOT fixed and is not faster. Nothing in the check changed; standalone
  it is 7.6s before and after.
- 19500 does NOT follow the profile convention — convention gives 25000; this is tighter on
  purpose.
- The false-red CLASS is not eliminated. The same contention mechanism is still growing and
  `check-markdown` is next; that is #544.
- No uncontended baseline exists for any recorded sample of this check, and none can under
  the current runner layout.
- Escape margin is not zero-cost: headroom goes from ~0 to +2866ms on the median, so a
  ~+17% wall-clock regression would now pass where the old bar would have caught it — the
  old bar was, however, already red, so it was catching nothing in practice.
- The `default` map value is not measured on any machine that uses it; it is borrowed from
  the x86_64 profile and labelled as such.
