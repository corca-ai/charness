# Issue 336 host goal-slot resolution critique
Date: 2026-06-08

## Decision Under Review

The #336 resolution: making the `achieve` Before-phase artifact-only so drafting
a goal does not consume the host active-goal slot (the slot is consumed only at
`/goal @artifact` pursuit). Reviewed for correctness, honesty of the
portable-vs-host determination, and whether it prevents recurrence of the class.

## Failure Angles

- Faked-fix risk: a "portable" contract that does nothing because the host
  auto-activates the slot regardless of agent behavior. Verified against the
  drafting helper: `upsert_goal.py` is pure file I/O and calls no host goal
  API, so drafting cannot consume the slot by construction — the contract is the
  real fix for the agent/operator-driven path, not a fig leaf.
- Mislabeled-completeness risk: closing #336 while a host-runtime gap remains
  silently unaddressed. Folded: the host-runtime residual (a host that
  auto-activates on artifact creation) is recorded as an explicit non-claim in
  `lifecycle.md` and the closeout, not assumed away.
- Recurrence risk: the rule decays to prose and a future agent re-introduces the
  friction. Folded: a contract-pinning test plus a third dogfood acceptance
  criterion give the rule by-construction teeth.

## Counterweight Pass

The host-runtime residual is a real but low-probability boundary, not a blocker:
the Claude host demonstrably does not auto-activate (drafting this session left
the slot empty; only `/goal` consumed it), and the Codex host slot is updated by
agent-callable tools the contract now forbids during drafting. Filing a
speculative host-side issue now would be noise; documenting the conditional
boundary is the honest disposition. No over-worry was folded into scope creep.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: valid-but-defer | evidence: moderate | ref: skills/public/achieve/references/lifecycle.md | action: document | note: host-runtime residual (a host auto-activating the slot on artifact creation) is outside achieve's control; recorded as a conditional non-claim, not filed as a speculative issue
- F2 | bin: over-worry | evidence: strong | ref: skills/public/achieve/SKILL.md | action: document | note: achieve SKILL.md core sits at the headroom buffer floor after the +1 line; not a #336 blocker, recorded so later achieve-core edits move prose to references

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: fresh-eye bounded implementation/resolution critique (general-purpose subagent, opus-class).
- Requested spawn fields: the bounded Slice-1 review packet — intent, determination, changed files + owning/generated surfaces, expected invariants, proof already run, non-claims, out-of-scope lines, reviewer questions.
- Host exposure state: applied
- Application state: host-confirmed: subagent a31204a067a3ad801 spawned and returned a SHIP verdict after independent verification.

## Fresh-Eye Satisfaction

SHIP. The reviewer independently confirmed the determination is honest
(`upsert_goal.py` is pure file I/O, so drafting cannot consume the host slot by
construction), the SKILL.md/lifecycle/adapter-contract surfaces are consistent,
the contract-pinning test reproduces all assertions and would catch a
regression, the dogfood "unchanged behavior" claim is defensible, and zero
portability-gate findings. The host-runtime residual is correctly a conditional
non-claim, so a speculative host-side issue is premature. No blockers; findings
are valid-but-defer / over-worry class only.
