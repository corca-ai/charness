# Retro — North-Star Overhaul (Track 1a + Track 2), 2026-06-18

Mode: `session` (closeout retro for the
`2026-06-18-north-star-overhaul` achieve goal).

## Context

One autonomous run executed the whole north-star overhaul goal: Track 1a
(generalize the #386 per-unit behavioral-verdict framing to every irreversible
boundary) + Track 2 (slim the standing prose surface). Slices S1 (boundary
audit) → S2 (issue/PR close pilot) → S3 (release/deletion sweep) → S4 (Track-2
audit) → S5 (AGENTS.md PUSH→PULL + retro SRP) all landed, each commit gated, with
four bound fresh-eye critiques (S2, S3, S3-relocation, S5) all PASS. What matters
next: the closeout (S6) and the recommended spin-out of the remaining-13-body SRP
sweep.

## Evidence Summary

Commits `c6c0cc56` (S1) · `8b3e38e9` (S2) · `439c4112` (S3) · `fde33bb8` (S4) ·
`142329b2` (S5); critique artifacts under `charness-artifacts/critique/2026-06-18-s{1..5}-*`;
slice-closeout gate runs (ruff/length/mirror-drift/validate_skills/doc-links/
markdown/check_skill_contracts) green per commit; broad pytest at S6 closeout.

## Waste

- **Release cap fight (S3, ~4 wasted edit-cycles).** I tried to land the G3
  per-surface-verdict framing inside the capped `release/SKILL.md` body several
  times before recognizing the `check-skill-core-headroom` ratchet (a ≥4-line
  core-headroom buffer that blocks a *regressing* change) required relocating the
  detail to a reference. Checking the binding constraint *first* would have routed
  it to `install-surface.md` immediately.
- **Staged-blob gate confusion (S3).** `check_skill_surface_preflight.py` reads
  the STAGED index blob (`git show :<path>`), not the working tree — so my
  unstaged relocation edits didn't move the headroom number until I re-`git add`.
  A couple cycles lost to "why isn't the number changing?".
- **Skill-prose slim broke 3 deterministic tests the per-slice gates missed
  (caught only at the S6 bundle-boundary broad pytest).** (a) `retro/SKILL.md`
  reworded a trigger sentence `check_skill_contracts.py` pins (caught at the S5
  commit by `run_evals`); (b) the S3 release consolidation dropped the exact
  phrase "tag push alone as publish completion" that `test_release_real_host.py`
  pins (NOT in the `run_evals` subset, so it survived to S6); (c) the S5
  `retro/SKILL.md` slim dropped "fresh-eye reader misread an invariant" that
  `test_retro_skill.py` pins. The fresh-eye critiques checked safeguard *content*,
  not the verbatim pinned-phrase tests — so the broad suite, not the reviewer or
  the per-slice subset, was the catch. **Lesson: the bundle-boundary broad pytest
  is load-bearing for skill-prose slims; the per-slice `run_evals` subset does
  not cover every pinned-phrase test.**
- **AGENTS.md `## Skill Routing` is a GENERATED surface (S5 → reverted in S6).**
  The S5 collapse treated it as free prose, but `setup/scripts/render_skill_routing.py`
  pins the canonical compact block verbatim (`matches_compact_block`), and
  `charness doctor`'s `repo_onboarding` status flips `ready → required` when
  AGENTS.md diverges — failing `test_charness_doctor_reports_managed_surface` in
  the broad suite. The S5 fresh-eye reviewer AND I both missed that an AGENTS.md
  section can be skill-owned/generated. Reverted to the canonical block; a real
  collapse needs a lockstep `render_skill_routing.py` edit. **Lesson: before
  editing an AGENTS.md section, check whether a `setup`/`render_*` script
  generates or pins it.**

## Critical Decisions

- **S1 worst-gap pick = issue/PR close (G1+G2).** Grounded the pilot in the
  literal #386 shape and the highest-blast-radius carrier (PR merge → shared
  history), validated by the S2 critique.
- **In-place per-boundary instantiation over a shared-ref hoist (S3).** Kept each
  boundary's mandate boundary-specific (different unit/proxy/channel/observer);
  the reviewer's Q5 confirmed it is not a duplicated paragraph. The cap then
  forced G3's *detail* into a release-owned reference — which preserved the
  in-place (per-skill) method while respecting P2/the cap.
- **B2 guardrail (mandate-the-question, never declare-completion)** baked into
  every gap and every critique's declares-vs-mandates check — the thing that
  stops a generalized fix from re-creating the #386 terminal green.
- **Re-verified the S3 relocation** rather than rubber-stamping a material change
  made after the critique passed (provisional-success discipline, north-star P4).

## Expert Counterfactuals

- **Jef Raskin (first-reader / "one obvious way").** The two biggest friction
  sources — the AGENTS.md Skill-Routing/Start-Here duplication and the release
  cap fight — are both *non-orthogonal surface* symptoms: a second place saying
  the same thing, and a body holding detail a reference already owns. A Raskin
  "where does a first reader look for X, and is there exactly one home?" pass run
  at the *start* of Track 2 (not S4) would have surfaced both before any edit
  churn, and is the orthogonality lens the goal's Design section already names.
- **Donald Knuth (premature placement).** Placing the G3 framing in the body
  before checking the binding constraint (the headroom ratchet) is the
  optimization-before-measurement trap; measuring the constraint first routes the
  content to its right home in one move.

## Next Improvements

- **workflow:** before editing a near-cap SKILL.md, in one shot check
  `check_skill_surface_preflight.py` core-headroom AND grep
  `check_skill_contracts.py` for that skill's pinned snippets — the two traps
  above are both pre-checkable. Re-stage before re-reading any staged-boundary
  gate.
- **capability:** a small pre-edit affordance that, given a SKILL.md path, prints
  its core-headroom margin + its pinned contract snippets would collapse both
  traps to one read. Candidate follow-up issue (not filed this run — see
  Auto-Retro disposition).
- **memory:** the staged-blob-headroom-ratchet and contract-snippet-slim traps
  are captured durably in this retro's Waste + Sibling Search (the canonical
  memory home the `recent-lessons.md` digest selects from on its next persist
  cycle) so the spun-out 13-body SRP sweep can pre-check them.

## Sibling Search

`Structural pattern:` "a body-slim edit silently drops a phrase a deterministic
contract/test pins verbatim" and "a near-cap SKILL.md edit ignores the
staged-blob core-headroom ratchet." `Triggering instance(s):` retro S5
contract-snippet break; release S3 cap fight. Both are **transferable to the
spun-out remaining-13-body SRP sweep** — every one of those bodies is near the
cap and several have pinned contract snippets. `Destination:` `repo-local guard`
is not needed (the gates already catch it post-hoc); the cheap win is the
`memory` note above so the sweep pre-checks. Captured durably here (the
`recent-lessons.md` digest selects from this artifact on its next persist cycle).

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-18-north-star-overhaul-retro.md
