# Workflow + host-state hardening bundle
Date: 2026-06-14

## Mode

session

## Context

Closeout retro for goal
`charness-artifacts/goals/2026-06-14-workflow-host-state-hardening-bundle.md`:
three non-blocking workflow/host-state guards landed and released as 0.48.0 — S1
agent-browser orphan scoping (bug-class #365), S2 #363 close-keyword-leakage
advisory, S3 #364 decaying-habit advisory — each reusing an existing surface (no
new blocking floor, per Floor-Addition Restraint), through push + release.

## Evidence Summary

- 5 commits ahead of origin/main → pushed; release `v0.48.0` verified
  (`release_url` returned, `public_release_verification: verified`,
  `fresh_checkout_probe_status: passed`, `install_refresh` 0.47.0→0.48.0 `== repo`).
- `verify-closeout --expect-state CLOSED` = verified for #363, #364, #365
  (status verified, missing_fields [], resolution_critique ok).
- `run-quality.sh --read-only` push gate: 75 passed, 0 failed (broad pytest
  `PASS pytest 21.0s` included) after the seam-index rebuild.
- Host-log probe (window absent → thread-wide): 439 token snapshots, 188
  function calls, 37 patch applications, 3 subagent spawns, no repeated broad
  gates, no repeated VCS commands
  (`charness-artifacts/retro/2026-06-14-workflow-host-state-hardening-bundle-host-log.md`).
- Causal review + resolution critique (S1/#365) + bundle release critique
  (#363/#364) all fresh-eye subagents; verdicts: causal PASS, resolution
  committed-ready, release PUBLISH-WITH-NITS (no blockers).

## Waste

- **S2 detour — my own debug artifact blocked closeout repo-wide.** I wrote the
  #365 debug artifact's `## Seam Risk` with `Risk Class: host-state` + a prose
  `Generalization Pressure`. `validate_debug_artifact` accepted it, but the
  stricter `risk_interrupt_lib` parser rejected it, so `plan_risk_interrupt`
  returned `blocked` unconditionally and EVERY `run_slice_closeout` failed.
  Cost: a debugging detour to reverse-map the failure → reclassified to
  `operator-visible-recovery` / `monitor`. Filed as #366.
- **Seam-risk index not rebuilt in S1.** Adding a debug `## Seam Risk` section
  requires `build_debug_seam_risk_index.py --write`; I missed it and the
  `validate-debug-seam-index` gate caught it at the bundle boundary (one round,
  no escaped drift).
- **Reword-dispatcher process error (mine, not repo).** My first commit-reword
  rebase used a grep dispatcher that mis-assigned messages; aborted to a backup
  branch and redid it with a robust position-based `exec git commit --amend -F`.
  One extra round; the backup branch made the abort safe.

## Critical Decisions

- **cwd as the agent-browser ownership signal, verified empirically.** Before
  designing the fix I spawned a real daemon and observed `cwd =` the launching
  checkout and `ppid == 1` from birth (detached-by-design) — falsifying the
  "ppid==1 == abandoned" model AND confirming cwd is reliable (the daemon does
  not chdir). This is what made cwd-scoping defensible rather than a guess.
- **Fail-closed, uniform scoping of all three selectors.** Orphan daemons,
  reparented residue, and zombie residue all scope by cwd; unknown cwd → never
  killed/flagged. A neighbor's daemon is never touched; the cost (no auto-clean
  on a host where cwd is unreadable) is the safe direction.
- **Advisory, not a blocking floor (Floor-Addition Restraint).** #363/#364 are
  non-blocking advisories on the existing slice-closeout surface, reusing the
  REAL gate signals (shared `is_artifact_only_commit`, the packaging mirror map,
  the boundary-bypass inventory) so they cannot drift from the gates they
  forecast.
- **Reworded the slice commits to carry full closeout ledgers.** Direct-commit
  auto-close requires the ledger in the commit body; the honest fix was to make
  each fix commit carry its own ledger rather than route around the verifier.

## Expert Counterfactuals

- **Michael Feathers (seams / declaration-over-convention):** the #366
  cross-validator gap is an invariant that still relies on the author
  *remembering* the risk_interrupt taxonomy rather than the debug validator
  *declaring* it. Changed action: when two validators read the same field, the
  upstream (author-time) one should import the downstream enum, not duplicate or
  omit it — surfaced as #366.
- **A release engineer's "carrier ledger" lens:** the fix commit should carry
  its closeout ledger from the first commit, not be reworded at release time.
  Changed action: when resolving a tracked issue, author the slice commit body
  with the JTBD / root-cause / debug-artifact / siblings(decision+proof) /
  prevention / `Critique #N` / `Closes #N` ledger up front, so no reword is
  needed at the bundle boundary.

## Sibling Search

- axis: same-layer (other author-time artifact validators) | location: any
  validator that under-constrains a field a downstream consumer parses strictly,
  where the strict failure only fires at a blocking gate | decision: valid
  follow-up outside the slice | proof: static — `validate_debug_artifact` vs
  `risk_interrupt_lib` enum gap, reproduced this run (host-state accepted then
  blocked closeout) | follow-up: #366

## Next Improvements

- workflow: when authoring a debug `## Seam Risk` section, use the
  `risk_interrupt_lib` taxonomy (`Risk Class` ∈ external-seam / host-disproves-
  local / repeated-symptom / operator-visible-recovery / contract-freeze-risk /
  none; `Generalization Pressure` ∈ none / monitor / factor-now) AND run
  `build_debug_seam_risk_index.py --write` before closeout; when resolving a
  tracked issue, author the fix commit body with the full closeout ledger so no
  release-time reword is needed.
- capability: `validate_debug_artifact.py` should enforce the `risk_interrupt_lib`
  enums (reusing `ALLOWED_RISK_CLASSES` / `ALLOWED_GENERALIZATION_PRESSURE`) so an
  off-taxonomy value fails at write time, not as a repo-wide closeout block — #366.
- memory: persisted here and rolled into recent-lessons by the persister.

## Persisted

yes: charness-artifacts/retro/2026-06-14-workflow-host-state-hardening-bundle.md
