# Boundary DBD-2 issue 414 416
Date: 2026-07-05

## Decision Under Review

Extending the portable boundary-ownership checkpoint (First Slice: critique+impl)
to the remaining four lifecycle stages named by #414 — `issue`, `spec`,
`achieve`, `quality` — and closing #414 (missing seam) and #416 (authoring
drift). The design decision: all four resolve to the **impl archetype** (surface
the shared brief + emit-only disposition, leaning on the `critique`/review each
stage already runs); no stage grows a new hard validator floor, because the
boundary disposition is a per-*change* artifact whose validated teeth stay in
`critique` alone.

## Failure Angles

- **Under-delivery**: brief-surface + emit-token could be prose decoration that a
  skeptic rejects as not closing #414/#416.
- **Overstated enforcement**: claiming a stage "floors" the disposition when no
  gate enforces it — re-creating the #408 silent-skip in doc form.
- **Portability leak (#416 core)**: a consumer repo's owner taxonomy entering
  portable prose.
- **Proof gap**: an emitted token/surface asserted but not covered by a
  deterministic test.

## Counterweight Pass

- The hook is real, not decoration: the brief is now surfaced across all six
  lifecycle stages, and every change-producing close (`issue`
  bug/feature/deferred, `spec` finalize, `achieve` slice) routes through a
  `critique` whose validator now floors the typed disposition. That is inherited
  teeth, not a new gate — the correct minimal design.
- The no-new-floor decision is right (Fixed Decision 8 generalizes); the only
  real defect was prose that *claimed* a floor achieve does not have.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/references/coordination.md:90 | action: fix | note: "each slice's critique already floors it" overstated enforcement — achieve's critique role is a recommendation, not one of its four floors, and a probe-less rung-2 inline critique is judgment-only (DBD-4 residual); FIXED by caveating the claim in the reference and the spec record (no floor added).
- F2 | bin: bundle-anyway | evidence: moderate | ref: tests/test_boundary_probe.py | action: fix | note: issue's emit-only `Boundary #N:` close-comment line was unproven while impl+spec tokens are asserted; FIXED by folding a guard into the reachability test at zero net LOC.
- F3 | bin: over-worry | evidence: weak | ref: scripts/validate_critique_artifacts.py:101 | action: defer | note: BOUNDARY_OWNERSHIP_RULE_DATE = 2026-07-06 means the inherited teeth bite one day out; intentional grandfather pattern, not a defect.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage bounded fresh-eye (shared fresh-eye-subagent-review policy).
- Requested spawn fields: fresh-context reviewer, read-only, adversarial four-bin triage over the DBD-2 diff.
- Host exposure state: applied
- Application state: host-confirmed: charness Agent tool spawned a bounded general-purpose reviewer in a fresh context; it returned `Verdict: REVISE` with the findings above, then the two fixes were applied and re-verified.

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: the portable brief + disposition schema in `skills/shared/references/boundary-ownership-brief.md` (Charness owns the question/schema/carrier).
- Consumer: the four lifecycle skills (`issue`/`spec`/`achieve`/`quality`), which reference the shared producer; the repo adapter owns the taxonomy/probe.
- Owning surface: `skills/shared/` for the brief; each stage's own references for its surfacing.
- Verdict: owned-correctly — the change crosses surfaces (one shared brief wired into four skills) but each skill references the shared producer correctly and no consumer taxonomy is encoded into the shared brief or any portable prose (AC6 grep-clean). Note: the repo cross-surface probe (`scripts/*_lib.py`, `skills/shared/**`) does not match this diff's `skills/public/**` paths, so this verdict is self-asserted by judgment, consistent with the DBD-4 residual.
