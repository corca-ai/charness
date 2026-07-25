# Issues 455 456 resolution critique
Date: 2026-07-25

## Decision Under Review

Resolving corca-ai/charness#455 (bounded reviewer results have no deterministic
retrieval path) and #456 (issue closeout floor is discoverable only by violating
it). Both are `enhancement` class, so this critiques the design rather than
running a causal review. Both are instances of one class: **a repo capability
exists but is discoverable only by violating the gate that enforces it** — the
same class as the artifact-shape work committed earlier in this cycle.

## Failure Angles

- Does #455's helper institutionalize the workaround it was built to retire?
- Does #456's fix generalize, or did it patch two instances of a class?
- Is the `$SKILL_DIR` idiom in a machine-read planner payload actually usable?
- Anything wrong: a typed status that lies, a cap that hides data, a test that
  pins an implementation detail rather than the contract.

## Counterweight Pass

The reviewer ran the counterweight inside the lens and graded down as often as
up. It rejected the `$SKILL_DIR` concern outright by checking five sibling
planners and the bootstrap-resolution reference — the idiom is the deliberate
injection seam, not a defect. It found no defects in `reviewer_result.py`'s typed
statuses after reading the terminality logic and its tests, and said so plainly.

Most usefully, it refuted the parent's own proposed generalization: a test over
the preflight REGISTRY would NOT have caught #456, because the producer was
already registered there and already pinned by a test. Registration is not
reachability. That correction is what produced the guard that actually works.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/references/closeout-discipline.md | action: fix | note: #456 wired the planner but the required-read the planner routes to still named only the validator, so an agent reading the documented path still discovers the shape by failing the gate; fixed by naming the producer before the validator paragraph
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_check_artifact_surface_preflight.py | action: fix | note: the proposed REGISTRY test would not have caught #456 since the producer was already registered and pinned; replaced with a reachability guard asserting each registered producer is named somewhere inside its owning skill package, proven to fire on the pre-fix tree and pass now
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/critique_reviewer_evidence.py | action: fix | note: transcript recovery folded into `findings-received` would make the diagnostic path indistinguishable from clean inline delivery, eroding the spawn-shape discipline by exactly the mechanism the helper's author warned about; added a signal-bearing `findings-recovered-from-transcript` state so this is enforcement rather than framing
- F4 | bin: over-worry | evidence: weak | ref: skills/public/issue/scripts/issue_plan.py | action: defer | note: emitting an unexpanded `$SKILL_DIR` in a planner payload is the established convention across five sibling planners and the documented injection seam; no change
- F5 | bin: over-worry | evidence: weak | ref: skills/shared/scripts/reviewer_result.py | action: defer | note: the typed statuses, the size cap reporting true `text_chars`, and the id/path clipping exemption were all inspected and found honest; no defect
- F6 | bin: valid-but-defer | evidence: moderate | ref: skills/shared/scripts/reviewer_result.py | action: defer | note: the built-in transcript layout is inferred from one host at one version and is unversioned, so a host layout change degrades silently to `layout-not-found` — the safe direction, but the built-in path has an expiry nobody will notice

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (resolution critique over both changes).
- Requested spawn fields: none sent — per the repo's per-host subagent split, Claude Code hosts use the host's own typed-agent controls (`bounded-reviewer`) with session-model inheritance.
- Host exposure state: host-defaulted
- Application state: reviewer ran on the session-inherited model; no host tier-application signal exposed.
<!-- allowed Delivery state: findings-received | findings-recovered-from-transcript | spawn-accepted-no-delivery | pending-parent-spawn. Boundary cleanliness is a separate claim and does not imply delivery. -->
- Delivery state: findings-received — the reviewer returned findings inline under the unnamed spawn shape.

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded reviewer spawned as `bounded-reviewer`; it
returned findings inline and self-reported the read-only envelope bound. Rail-1
boundary verified `{"ok": true, "drift": []}` after it returned, before any fix
was applied.

Non-claim on the implementation reviews: the two subagents that built these
changes ran their own bounded reviews, and the `reviewer_result.py` author
disclosed that its rail-1 window was not cleanly bracketed around its second
reviewer (the drift list was that agent's own edits). That review is therefore
recorded as unproven-for-boundary, and this critique is the boundary-clean one.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: the artifact-surface preflight REGISTRY (which producers exist) and the planners/references that name them at the moment of need.
- Consumer: an agent reaching a validator-gated closeout, which either receives the shape or discovers it by failing the gate.
- Owning surface: `scripts/check_artifact_surface_preflight.py` for registration, the owning skill's planner and required-reads for reachability.
- Verdict: owned-correctly — registration and reachability are genuinely different properties owned by different surfaces, and the new guard binds them without collapsing one into the other.

## Release Note (v2.7.0 scope)

This critique also covers the v2.7.0 release surface: the same reviewer's
findings were applied before the tag, and the bump is `minor` because
`reviewer_result.py` is a new additive capability and the new
`findings-recovered-from-transcript` delivery state is an additive enum value
(existing artifacts and the scaffold are unaffected; the floor's date grandfather
is unchanged).
