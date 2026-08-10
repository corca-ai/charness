# Resolution critique — #591 (two floors gated on a reason that is not about behavior)
Date: 2026-08-10

## Decision Under Review

Whether the fix for [#591](https://github.com/corca-ai/charness/issues/591) — removing
the `BEHAVIORAL_VERDICT_CLASSIFICATIONS` gate from `evaluate_ai_provenance` and from
`evaluate_hotl_dispositions` — actually discharges what the issue asked, or whether it
left a residue that a close would silently bury.

**Outcome: CLOSABLE.** A bounded fresh-eye reviewer read the current tree against the
issue's ask and found both defects structurally absent, not reworded.

## Failure Angles

- **The fix relocated the surface.** The floors no longer live in
  `issue_verify_closeout_body.py`; they moved to
  `skills/public/issue/scripts/issue_closeout_rung1_floors.py`. A close that cited the
  old path would send a reader to a file that no longer holds the code.
- **A widened floor that refuses nothing is theatre; one that refuses too much is an
  irreversible-boundary regression.** The issue named this explicitly and demanded a
  before/after rather than a drive-by tightening.
- **The issue's ask had two halves and one was added by a later comment.** A fix that
  addressed only `AI-provenance` and not `HOTL` would look complete against the body.
- **The advisory that TELLS authors which floors run is a separate surface from the
  floors.** A correct floor behind a stale advisory is the shape this repo's own
  lessons name as where the blockers are.

## Counterweight Pass

- The concern that the widening would refuse previously-passing carriers was measured,
  not argued away: 84 commit-msg carriers plus three consolidated direct-write closes,
  every light-classification carrier already carrying the marker voluntarily and none
  presenting a HOTL entry. Zero refusals. This was over-worry, and it was retired by
  measurement rather than by assurance.
- The concern that the advisory would go stale was NOT over-worry: it is exactly what
  the reviewer had to check, and the fix had to move a pinned sentence to keep it true.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_closeout_rung1_floors.py | action: document | note: `evaluate_ai_provenance` (`:324-343`) has no classification branch at all; `applies` is unconditional `True` and the docstring states "No classification gate ... classification is reported, never gating". The defect is absent from the code, not merely renamed.
- F2 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_closeout_rung1_floors.py | action: document | note: `evaluate_hotl_dispositions` (`:308-321`) retains exactly one early return — the PRESENCE gate `if not lines` — which is the gate the issue explicitly called sound and left in scope. The classification is carried to the payload as data only. Pinned by tests/quality_gates/test_issue_closeout_rung1_floors.py:131-136, which asserts `applies is True` / `ok is False` for an undispositioned HOTL entry across question, decision-needed, consolidated and bug.
- F3 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_closeout_rung1_floors.py | action: document | note: the undercounting advisory was corrected in the right direction, not merely deleted. `review_advisory_for_classification` (`:53-110`) now names AI-provenance and HOTL as floors that still apply, and `:92-96` records that the pinned wording was moved deliberately because byte-stability "does not license an advisory that misreports which floors ran". The stale string "silently bypasses two of the three floor checks" survives nowhere in the source tree. `describe_closeout_draft_shape.py:110-119` now OBSERVES the floor rather than restating the tuple.
- F4 | bin: over-worry | evidence: strong | ref: .agents/closeout-floor-matrix.json | action: document | note: the string `591` appears zero times in the matrix; all 26 formerly-`undispositioned` cells are re-declared `fires`, matching the recorded 134-up-from-108 delta. The only two `undispositioned` cells left pointed at #592, a separately filed issue, and are dispositioned by the same carrier as this close.
- F5 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/spec/2026-08-10-closeout-floor-carrier-matrix.md | action: fix | note: the spec quoted the defect in the present tense against `issue_verify_closeout_body.py:116`, a location the fix deleted. It read as history because the next section records the repair, but the file:line pointer was dangling. Repaired by marking the citation as the pre-fix observation it was and naming the current module.
- F6 | bin: bundle-anyway | evidence: strong | ref: .agents/closeout-floor-matrix.json | action: document | note: #591's own body cites the matrix as `skills/public/issue/references/closeout-floor-matrix.json`, which does not exist; the canonical path is `.agents/closeout-floor-matrix.json` per `scripts/check_closeout_floor_matrix.py:34`. No code or doc still points at the wrong path — only the issue text. The close comment names the real path so the reader can find the evidence.

## Disposition

CLOSABLE. Both defects the issue names are gone from the tree, the widening was
measured before it shipped and refuses nothing that previously passed, the advisory
surface that would have gone stale was carried with the fix, and the matrix
re-declaration proves the floors moved rather than asserting it. One cosmetic dangling
pointer (F5) is repaired in this slice; one issue-text path error (F6) is corrected in
the close comment rather than in the tree, because the tree is already right.

## Reviewer Tier Evidence

- Requested tier: bounded read-only fresh-eye reviewer (`bounded-reviewer`), unnamed and synchronous.
- Requested spawn fields: subagent_type=bounded-reviewer, run_in_background=false, no host addressing name.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer returned findings in-band. The boundary verify for window `w-20260810T100928Z-54567` returns ok with the single drift entry `parent-attributed` (`.charness/wave1-issues.json`, an untracked payload file the parent wrote after the snapshot and declared on verify). No tracked file and no index entry moved across the review window.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated. The reviewer's decisive contribution was negative in the useful
sense: it verified the code, the advisory, the tests, the matrix and the spec against
the ask and found no residue, while surfacing two pointer defects (F5, F6) the parent
had not looked for. The parent did not re-run the floors' tests or the matrix gate as
the reviewer read them; the matrix gate was run separately by the parent after the
#592 re-declaration in the same carrier and reports 36 pairs in agreement.

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed: the reviewed input was the current worktree at HEAD 91a9b52b. -->

## Boundary Ownership

- Producer: `issue_closeout_rung1_floors`, which renders the rung-1 presence verdict on every closeout carrier.
- Consumer: the GitHub close itself — an irreversible external write — and the rung-2 fresh-eye observer who reads it.
- Owning surface: `skills/public/issue/**`.
- Verdict: single-surface
