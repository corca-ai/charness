# Retro: Portable skill contract quality and routing discipline

## Context

This session closed the active goal
`charness-artifacts/goals/2026-06-04-portable-skill-contract-quality-and-routing.md`.
The work removed concrete repo-local issue/date anchors from portable skill
packages, added package-level skill text-quality subchecks, promoted objective
issue/date rules to blocking defaults, tightened `achieve` phase-routing
evidence, and made `achieve` reference discoverability easier to operate with a
root reference index.

## Evidence Summary

- Goal artifact slice log through Slice 5 and final locked closeout evidence.
- Final locked closeout wrapper:
  `run_slice_closeout.py --verification-lock --ack-cautilus-skill-review`
  against `origin/main..HEAD`; all deterministic gates passed and broad pytest
  passed in 297.5s.
- Final skill ergonomics inventory: 23 skills checked,
  `package_issue_anchor=0`, `package_dated_incident=0`,
  `reference_discoverability=0`, `host_surface_reference=104`.
- Thread-wide host-log probe: 6 context compactions, 660 function calls, 97
  custom tool calls, 14 pytest invocations, and 27 `git status` / 31 `git diff`
  calls. No per-goal metric window was recorded, so these are pressure signals,
  not a per-goal cost total.
- Follow-up issues filed: #295 for closeout test-selection cost and #296 for
  reviewer-tier/cost visibility.

## Waste

- The selected broad pytest gate is expensive for small parser/public-skill
  slices. It passed once before the Slice 5 reviewer fix and again at final
  locked closeout, so the earlier five-minute run became weaker evidence after a
  narrow parser change.
- The subagent reviewer tier was not controlled by the spawn call. The repo
  requires fresh-eye review, but the closeout evidence did not make the
  host-selected cost/model tier predictable to the operator.
- Repeated status/diff/check commands were partly phase-barrier proof, but the
  volume shows that final goal work still pays meaningful context and command
  overhead.

## Critical Decisions

- Cleaning package issue/date anchors was promoted from advisory inventory to
  blocking default rules only after the baseline was clean.
- `host_surface_reference` stayed advisory/deferred because the 104 hits are
  high-recall evidence, not a proven portability violation class.
- `achieve` routing was enforced as a presence floor tied to `find-skills`
  evidence, not as a hard-coded phase-to-skill map.
- Reference-index semantics were tightened after fresh-eye review: only
  `## References` list items and index bullet items count as listings.

## Expert Counterfactuals

- Gary Klein premortem: before running a pre-lock broad pytest on Slice 5, ask
  "what later finding could invalidate this run?" The answer was a reviewer
  parser fix, so the better sequence is focused proof before review, broad proof
  only after mutation lock or at final closeout.
- Kent Beck test economics lens: make the smallest meaningful behavioral proof
  cheap and reserve broad tests for integration confidence. The new
  reference-index test file was the right local proof; the workflow still needs
  a clearer policy for when that local proof is enough between broad gates.

## Next Improvements

- issue #295: make closeout test-selection cost explicit, separating
  pre-lock slice proof from final verification-lock broad proof.
- issue #296: expose bounded reviewer cost/tier selection in closeout evidence
  when the host, not the repo, chooses it.

## Sibling Search

- Test-cost sibling scan: similar pressure appears in existing recent lessons
  about broad reruns and mixed-tree broad proof. No same-session source change
  was made because #295 should design the policy across closeout wrappers,
  changed-surface planning, and quality/testability references together.
- Reviewer-cost sibling scan: fresh-eye review is required across `quality`,
  `critique`, `handoff`, `issue`, and `achieve` closeouts. #296 should treat
  this as a shared bounded-review evidence surface rather than a Slice 5-only
  note.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-04-portable-skill-contract-quality-and-routing-closeout.md`.
