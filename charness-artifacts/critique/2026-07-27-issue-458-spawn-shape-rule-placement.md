# Issue 458 spawn-shape rule placement
Date: 2026-07-27

## Decision Under Review

Resolving #458 by moving the `name`-parameter spawn-shape rule from the
review-scoped `fresh-eye-subagent-review.md` onto the always-loaded `AGENTS.md`
contract, scoped to every spawn, and rewording the `handoff`/`setup` pointers from
a post-failure remedy to a precondition of spawning.

## Failure Angles

- **Placement without reach.** The rule could land on charness's own always-loaded
  surface and still miss the repos that need it, since #458 was filed FROM a
  consuming repo whose `AGENTS.md` is seeded by `setup`'s template rather than by
  this file.
- **Placement without a pin.** A prose-only fix sits in a file under active
  compaction pressure, and the defect's own root cause is a rule decaying out of
  reach — so the fix could decay exactly the way the lesson it replaces did.
- **Two copies drifting.** The rule now exists in `AGENTS.md` and in the shared
  reference. A stale second copy is the failure mode the repo's single-sourcing
  rule warns about, and the reference is the pointer target for non-claims.
- **Burial.** One long bullet added to a ten-bullet section whose other nine
  bullets are reviewer-scoped may read as reviewer-scoped regardless of what it
  says.
- **Overclaiming the evidence.** The resolution asserts retrieval was "confirmed
  impossible" and the findings "never recovered", while the repo ships a transcript
  diagnostic for precisely this case.

## Counterweight Pass

Real blockers, both folded: the consuming-repo propagation gap, and the missing
test pin. Both are the difference between a rule that binds and a rule that reads
well.

Raised and deliberately NOT acted on: adding a gate that observes a general spawn
(no gate can see a host-owned spawn parameter — the debug artifact's Detection Gap
says so and is right); restating the rule in the remaining skills (duplication
without reach); and treating the upstream re-check as a close blocker (the
workaround is correct whether or not the upstream defect is open, and the artifact
already says re-probe rather than assume).

The overclaim angle turned out to be real and cheap to settle: running the
diagnostic recovered the findings, which both corrected the claim and surfaced an
action item the parent had missed.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/setup/references/agent-docs-policy.md | action: fix | note: the rule reached only charness's own AGENTS.md, so every setup-normalized consuming repo — including #458's filer — would keep stranding non-review spawns while setup reported its AGENTS.md conformant; fixed in the copy-verbatim template, the generated block, and the compact-contract required snippets
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_reviewer_result_delivery.py | action: fix | note: the entire fix was prose placement with no test pin, in a file under compaction pressure, when the root cause is lesson decay; four tests now pin the AGENTS.md rule, the consuming-repo template, and that a pre-rule compact contract reads as stale
- F3 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md | action: fix | note: the reference still claimed `n=1` per arm and stayed reviewer-scoped throughout, so a reader following the new AGENTS.md pointer landed back in the narrow scope; both corrected
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/debug/2026-07-27-named-spawn-recurrence.md | action: fix | note: "retrieval confirmed impossible" and "never recovered" overclaimed, since reviewer_result.py get recovered the text; narrowed to delivery channels and the recovery recorded, which also surfaced the stale sibling-scan audit that generated this session's phantom slice
- F5 | bin: over-worry | evidence: moderate | ref: AGENTS.md | action: defer | note: bullet placement within the section (first vs fifth) and a retitled heading were suggested; the content is scoped explicitly to EVERY spawn and now test-pinned, so reordering is cosmetic churn against a pinned string
- F6 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-07-25-reviewer-delivery-seam.md | action: defer | note: second recurrence of one external seam, so forward work (host-plural delivery proof, whether anything can observe a general spawn's delivery) stays with the existing seam spec rather than another point fix

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye reviewer, read-only scope.
- Requested spawn fields: `subagent_type: bounded-reviewer`, `run_in_background: false`, no `name` (the rule under repair), prompt-embedded output contract.
- Host exposure state: metadata-hidden
- Application state: the host exposes no per-subagent tier field on this surface; the typed `bounded-reviewer` agent supplied the read-only envelope and the reviewer self-reported tool absence.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: the parent agent's `Agent` spawn call, which selects the delivery channel via the `name` parameter.
- Consumer: any parent that needs a subagent's result — every spawn, not only fresh-eye review.
- Owning surface: the always-loaded repo contract (`AGENTS.md`) for the rule that must bind before a spawn, plus `setup`'s template and compact-contract inspector for the same rule in managed repos; the shared reference keeps lineage, host scope, and non-claims.
- Verdict: moved-to-owner
- Rationale: the rule previously sat only on a review-scoped reference while the mechanic it governs is spawn-scoped, so the fix is a move to the surface whose load timing matches when the rule must fire — one level out, the same move into `setup`'s template so managed repos inherit it.
