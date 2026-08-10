# umbrella class disposition plan
Date: 2026-08-11

## Decision Under Review

`charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md` — a 13-item
disposition of the #582-#585 umbrella classes with an operator-directed deletion bias
(headline: 12 delete-or-rule, 1 build), plus a proposed four-rule amendment to
`docs/design-north-star.md`. Nothing had been executed. The operator asked explicitly
whether the plan was serving their stated preference rather than the evidence.

## Failure Angles

- **Minto (structure).** No apex sentence; three competing governing ideas (the classes
  are unrepaired / these teeth have no cliff / the operator wants deletion) that license
  different plans. The evidence artifact's own recommendation was demoted to a sequencing
  step below the dispositions it should govern. The stated universal criterion ("the
  escape test applied to every deletion") appears on 5 of 13 items.
- **Jackson (problem framing).** The escape test is borrowed from the north star's
  *closeout-boundary* definition and misapplied to probes and evals, whose job is to make
  a silent change observable rather than to stop an escape. #524 is refused BECAUSE
  nothing reads it while #525 is built BECAUSE nothing reads it — the same absence used
  both ways.
- **Weinberg (diagnostic / designated sycophancy angle).** The unadmitted accommodation
  is not deletion but *zero engineering effort*: on #524 a deletion was available (a
  schema'd ladder already exists beside the prose one) and the plan chose IGNORE, because
  deleting a shared reference means touching consumers. Seven of fourteen items would be
  decided differently by a reviewer with no knowledge of the operator's preference.
- **Gawande (checklist / operational).** Every disposition names a source location and no
  consumer set. Three of the six deletions invert on a single grep. Sequencing omits
  `plugins/charness/**` mirror sync, a pre-deletion green baseline, and same-commit
  coverage substitution.

## Counterweight Pass

A separate skeptical pass triaged all 18 consolidated concerns into the four bins below.
It pushed back on two: the "the real diagnosis is the authoring rate" reframe is mostly
grand restatement — unfalsifiable as stated, attacks a claim the plan never made, and
changes zero dispositions (keep one sentence of it, not the frame) — and "the bias is
effort, not deletion" is a motive claim whose next action is identical either way. It
also rejected the north-star amendment outright rather than asking for revisions.

Three load-bearing claims were then verified by the parent through channels the
read-only reviewers could not reach:

- `evals/cautilus/handoff-claim-fidelity/pickup-ambiguous.spec.json` has
  `requiredCommandFragments: ["continuation-sequence.md"]` — **not empty**. Only
  `pickup.spec.json` has both floors empty. The plan and its source audit both stated
  "both arms" and were wrong; the audit is corrected in the same change.
- `skills/public/quality/scripts/dup_ratchet_lib.py:305` — `hard_block = bool(new_code or
  new_doc)`, both pure set-differences at `:279-280`. There is no property arm to keep.
- `docs/deferred-decisions.md:685-703,710-726` — D47 publishes the probe figures, the
  entry records a FOURTH and FIFTH refresh (the plan said three), and `:711-714` assigns
  the standing pin tax to #536, not to D47.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/claim_fidelity_lib.py:390-403 | action: fix | note: deleting both pickup specs reds validate-scenario-conditional-reads and makes the incident-reconstruction test error; pickup-ambiguous is the only engage-always forcer of continuation-sequence.md
- F2 | bin: act-before-ship | evidence: strong | ref: docs/deferred-decisions.md:685-703 | action: fix | note: #561's "nothing propagates" is refuted — D47 publishes these figures and the pin is what forces its refresh; deletion makes an open operator decision silently stale
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/dup_ratchet_lib.py:305 | action: fix | note: the dup ratchet has no property arm, so "delete the identity arm" deletes the hard block entirely — a north-star :113-115 failure signature
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/boundary_bypass_ratchet_lib.py:132-139 | action: fix | note: count_increases is blind to one-for-one substitution, so new_keys is the only substitution detector; repair the key, do not delete the arm
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/recount_residue_lib.py:63-67 | action: fix | note: the Premise-residue marker is human-authored BY DESIGN and the fail-open was already repaired at recount_premise_lib.py:80-87, so the deletion premise is refuted
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/plan_handoff_run.py:108 | action: fix | note: the handoff artifact path is adapter-configurable, so #531's hardcoded is_file probe would silently suppress branch (1) in consumer repos; it is also a build shipped to consumers, not reversible session-local work
- F7 | bin: bundle-anyway | evidence: strong | ref: scripts/eval_setup.py:220-224 | action: fix | note: only render_skill_routing's unused parameter is dead — the listed_skill_ids payload key has live consumers and must stay
- F8 | bin: bundle-anyway | evidence: strong | ref: scripts/check_quality_tool_fixtures.py:112-115 | action: file-issue | note: #569's fallback returns 0 on an empty fixture set and is not queued in run-quality.sh, so "leave it as the tamper-evidence check it already is" describes a check that does not run | follow-up: deferred docs/handoff.md Next Session
- F9 | bin: bundle-anyway | evidence: strong | ref: docs/deferred-decisions.md:711-714 | action: document | note: #561's standing tax is tracked as #536, not D47's question, so the decision record routes to the wrong node
- F10 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md:14 | action: fix | note: the 12:1 headline is a labelling artifact — "delete-or-rule" absorbs IGNORE, RETIRE and a pre-existing decision, and one item carries no verb at all
- F11 | bin: bundle-anyway | evidence: moderate | ref: docs/conventions/implementation-discipline.md | action: fix | note: sequencing omits plugins/charness mirror sync, a pre-deletion green baseline, and same-commit coverage substitution for the spec deletion
- F12 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/audit/2026-08-10-umbrella-class-survival-review.md:126 | action: document | note: five rulings (#524 #535 #514 #569 #582-retire) have no named durable destination, which re-creates the laundering the audit diagnoses
- F13 | bin: over-worry | evidence: contested | ref: charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md:176 | action: document | note: "the real pain is the authoring rate" is unfalsifiable as stated and changes zero dispositions; keep one sentence naming what the plan does not touch
- F14 | bin: over-worry | evidence: weak | ref: charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md:151 | action: defer | note: "the bias is effort, not deletion" is a motive claim whose next action is identical either way
- F15 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/audit/2026-08-10-umbrella-class-survival-review.md:112 | action: document | note: the audit's fourth class instance (.agents/quality-adapter.yaml prose sizing 120 checked numbers) is omitted from the plan, and it is the one instance where no deletion is available
- F16 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/spec/2026-08-10-umbrella-class-disposition-plan.md:35 | action: document | note: three different tests are in use under one stated criterion; fix the stated test before the next disposition pass rather than re-grading this one

## Reviewer Tier Evidence

- Requested tier: high-leverage per `.agents/critique-adapter.yaml`, with the adapter's `model` field deliberately not forwarded — it names a model id this host does not expose, and CLAUDE.md routes per-host subagent controls to the host adapter rather than the contract.
- Requested spawn fields: subagent type `bounded-reviewer` (Read/Grep/Glob only), one angle per spawn, unnamed one-shot spawns, session model inherited.
- Host exposure state: host-defaulted
- Application state: the host exposed `subagent_type` and accepted it; it exposed no `service_tier`, `reasoning_effort`, or `fork_turns` control, so those adapter fields were not applied.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated` — four angle reviewers plus one separate counterweight pass, each a
distinct bounded subagent context. Reviewer boundary fingerprint snapshot/verify around
the window returned `clean` with zero drift.

## Reviewed Input Identity

<!-- The binding floor is deliberately NOT claimed here, and the reason is the finding.
The packet at charness-artifacts/critique/2026-08-10-203927-packet.json
(sha256 6e7883fbdd7832d5742a3762590d280d754c8f34fb65f710748fe1c253902299,
identity 00d5d3e6a1aea6f78ddb1828159c47b98b6442af41203650e9ea4be386dad8e6) bound the
PRE-REVISION draft of the plan. That draft was never committed, and the critique's
findings were folded straight back into it, so recomputing the identity today yields
"declared reviewed inputs are stale" -- correctly. Re-running prepare_packet against the
revised plan and re-declaring would produce a binding that PASSES while asserting the
reviewers read text they never saw, which is the exact substitution the floor exists to
refuse. The reviewed text is not lost: the packet .md/.json committed alongside this
artifact carry the draft verbatim. Next time, commit the reviewed version before folding
findings back, so the binding can be honest AND current. -->

## Boundary Ownership

- Producer: the disposition plan under `charness-artifacts/spec/`, which decides what happens to each umbrella class.
- Consumer: the deletion and build slices that would execute it, and the GitHub issues that would be re-split or ruled.
- Owning surface: the spec artifact for the dispositions; `docs/design-north-star.md` for the proposed amendment, which does not belong to the plan that grades itself with it.
- Verdict: escalated-to-issue-spec
