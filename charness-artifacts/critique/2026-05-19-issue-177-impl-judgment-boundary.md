# Critique: Issue 177 Impl Judgment Boundary

Date: 2026-05-19
Target: code critique
Packet consumed: `charness-artifacts/critique/2026-05-19-105844-packet.md`
Fresh-Eye Satisfaction: parent-delegated

## Change

Resolve Charness #177 by updating the public `impl` skill so user-corrected
agent behavior is classified as either a stable contract or a better case
reading before repo rules, tests, or gates are added. Preserve judgment-quality
corrections as a valid direct-answer, smaller-guidance, or no-repo-change
outcome, and keep proof claims limited to source, wiring, or guidance coverage
unless targeted behavior replay or evaluator comparison actually ran.

## Angles

- Michael Jackson / problem framing: reviewer `Nietzsche`
- Atul Gawande / operational and proof risk: reviewer `Ohm`
- Counterweight: reviewer `Zeno`

## Findings

- Bundle Anyway: `skills/public/impl/SKILL.md` said user-corrected behavior
  "starts the work"; issue #177 can also occur when correction redirects an
  in-progress implementation slice.
- Bundle Anyway: the initial patch shortened Worktree Readiness wording only
  to satisfy the 200-line skill limit, widening the diff outside #177.
- Act Before Ship: `docs/public-skill-dogfood.json` claimed scenario review
  kept the Cautilus registry unchanged without naming the inspected scenario
  surface or why no registry update was needed.

## Counterweight Triage

- Act Before Ship: record the concrete scenario-review decision or weaken the
  dogfood claim.
- Bundle Anyway: change "starts" to "starts or redirects" and restore the
  unrelated Worktree Readiness wording.
- Over-Worry: adding a maintained Cautilus scenario for this slice would
  overstate the proof goal. The issue asks for source/guidance coverage, not a
  live semantic-quality replay.
- Valid but Defer: none.

## Applied Before Commit

- `impl` now says user-corrected behavior may start or redirect the work.
- Worktree Readiness wording was restored; the 200-line limit was preserved by
  compressing nearby proof-policy wording.
- Dogfood evidence now names `evals/cautilus/scenarios.json`, the existing
  `impl-adapter-bootstrap` mapping, and the reason no scenario-registry edit
  was made.

## Next Move

Commit only after rerunning the deterministic closeout gate with the
scenario-review acknowledgement.
