# Critique: Issue-Closeout Goal Coordination Floor

Date: 2026-06-02
Fresh-eye satisfaction: `parent-delegated`

## Reviewed Change

Add a deterministic achieve coordination floor requiring an `Issue closeout:`
line, or an explicit opt-out, for goals Created >= 2026-06-02 when the goal
names tracked issue closeout work. Gather/release floors keep their 2026-05-31
cutoff.

## Reviewers

- Huygens: counterweight review.
- Descartes: correctness/regression review.
- Boyle: process/workflow-fit review.

## Findings and Disposition

- applied: Huygens and Descartes found the issue trigger was too narrow. The
  floor now recognizes GitHub issue URLs, `owner/repo#N` context refs, and
  repo-qualified close keywords such as `Close corca-ai/charness#277`.
- applied: Descartes found close-keyword scanning was too broad and could treat
  planning constraints such as `Do not close #276 until push` as recorded work.
  Close-keyword scanning is now scoped to `## Slice Log` and
  `## Final Verification`; context-source issue refs still trigger directly.
- applied: Huygens found stale single-cutoff wording in
  `docs/prescribed-skill-closeout-contract.md`. The doc now states separate
  gather/release and issue-closeout cutoff dates.
- applied: Boyle found `docs/handoff.md` prematurely claimed local `main` was
  clean while this bundle was still uncommitted. The handoff now avoids a stale
  cleanliness claim and points operators to live `git status`.
- applied: Boyle found the active goal did not record the proof for the new
  deterministic floor. The goal's `## Final Verification` now records focused
  tests, skill/dogfood/doc checks, line headroom, active-goal validation, and the
  historical completed-goal scan.
- applied: Boyle noted the template only described resolved issues, while the
  validator also triggers on tracked issue context sources. The template now
  tells operators to use `Issue closeout: n/a — <reason>` when a tracked issue
  is context only.
- accepted: Descartes suggested pinning GitHub issue URL contexts as both gather
  and issue floor triggers, and short issue opt-outs as refusals. Both are now
  covered by regression tests.

## Counterweight

No expansion into content validation was accepted. The floor remains
presence-only; the `issue` skill still owns closeout verifier proof. The
Coordination Cues and Auto-Retro exclusion remained intact where relevant, and
the final close-keyword scope was narrowed rather than broadened.

## Verification

- `pytest -q tests/quality_gates/test_goal_coordination_floors.py
  tests/quality_gates/test_goal_artifact_lib.py
  tests/quality_gates/test_achieve_before_activation.py` passed after folding
  review blockers.
- `ruff check skills/public/achieve/scripts/goal_artifact_coordination_floors.py
  tests/quality_gates/test_goal_coordination_floors.py` passed.
- `./scripts/check-markdown.sh` passed after doc/artifact edits.

