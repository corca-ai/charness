# Critique Review
Date: 2026-06-14

## Decision Under Review

Publishing charness release 0.48.0 (minor, 0.47.0 → 0.48.0): the workflow +
host-state hardening bundle of three non-blocking guards — S1 #365 (bug-class)
scopes `agent_browser_runtime_guard` orphan/residue detection + `--cleanup-orphans`
to this checkout by `/proc/<pid>/cwd` under `repo_root` (fail-closed, so a neighbor
checkout's live daemon is never killed/flagged); S2 #363 `advise_close_keyword_leakage`
(non-blocking close-keyword-in-artifact-only-commit advisory); S3 #364
`advise_decaying_habits` (non-blocking stale-mirror + in-process-test-default
advisories) plus a `slice_closeout_commit_advisories` module split. This single
fresh-eye pass serves as BOTH the release-hygiene critique AND the
resolution-critique (design review) for #363 and #364; S1/#365 already had its own
causal + resolution critiques. Question: is the bump level, update_instructions,
generated surfaces, operator risk, issue-close hygiene, and the two advisory
designs honest and safe to publish + close #363/#364/#365?

## Failure Angles

- **Wrong bump level.** Patch under-states the new advisory capability; major
  over-states (no break/migration). Either misleads operators.
- **Over/under-claiming update_instructions.** Hiding the agent-browser
  fail-closed BEHAVIOR CHANGE, or claiming consumer impact the code does not have.
- **Stale generated surface.** Plugin mirror drifted from source; packaging vs
  plugin vs marketplace version disagreement; an un-synced seam-risk index.
- **Operator risk.** The fail-closed default silently turning `--cleanup-orphans`
  into a no-op on a host where it used to work.
- **Issue-close hygiene.** Closing #363/#364/#365 when not genuinely resolved.
- **Advisory drift / false-fire.** The #363 regex firing on bare `#N` or in-word
  matches; the #364 detectors hand-rolling signals that drift from the gates.

## Counterweight Pass

- Bump: MINOR is the lightest honest level — S1 bug-fix + S2/S3 additive
  non-blocking capability, no break/migration. S1's fail-closed is additive-safe
  (the guard does LESS, never more), so it does not force major. Confirmed.
- update_instructions: the BEHAVIOR CHANGE (non-Linux/`/proc`-unreadable →
  fail-closed → no auto-clean + init-reap guidance) is disclosed verbatim; the
  "ships in plugin, opt-in, non-blocking, no githooks auto-wired" framing matches
  the code. Not a blocker.
- Generated surfaces: all four scripts byte-identical to `plugins/charness/scripts/`
  (drift gate green); seam-risk index rebuilt this run; the full `run-quality.sh
  --read-only` push gate is green (75 passed, 0 failed, broad pytest included).
- Operator risk: fail-closed cleanup no-op is deliberate and disclosed; residue is
  reported-not-reaped, so under-attribution only risks a missed self-cleanup, never
  a false kill (the prior behavior was the bug). Acceptable.
- Issue hygiene: #363/#364/#365 each carry `Closes #36N` in their slice commits and
  are genuinely resolved by the bundle. Closing all three at this push is correct.
- Advisory designs: #363 regex verified to NOT fire on bare `#N`, `fix#1` (no
  separator), or in-word (`prefix`/`affixes`); reuses the shared
  `is_artifact_only_commit`. #364 reuses `packaging.checked_in_plugin_root` (no
  hardcoded mirror path) + the boundary-bypass inventory/exemptions; both
  asserted non-blocking + not-wired-into-the-commit-gate by tests.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: over-worry | evidence: strong | ref: .claude-plugin/marketplace.json | action: defer | note: version surfaces still read 0.47.0 at critique time — expected, the bump is publish_release.py's job AFTER this gate (correct pre-publish sequencing), not a defect.
- F2 | bin: valid-but-defer | evidence: moderate | ref: .agents/release-adapter.yaml | action: defer | note: the 0.48.0 update_instructions entry describes the close-keyword advisory scanning "an unpushed commit" but does not spell out that it no-ops when no origin/main upstream resolves; honest-but-incomplete consumer edge note, deferred (the advisory degrades silently, no operator action).
- F3 | bin: over-worry | evidence: strong | ref: scripts/agent_browser_runtime_guard.py | action: defer | note: fail-closed cleanup becoming a no-op on a non-Linux / proc-unreadable host is disclosed in update_instructions and safe (the guard reports residue, never reaps it); deliberate, not a regression.
- F4 | bin: over-worry | evidence: strong | ref: scripts/slice_closeout_commit_advisories.py | action: defer | note: #363 close-keyword regex edge cases (bare #N, no-separator, in-word) all correctly do not fire — confirmed by the reviewer and the unit tests; no false-fire.
- F5 | bin: over-worry | evidence: strong | ref: plugins/charness/scripts/slice_closeout_commit_advisories.py | action: defer | note: the new module + the three edited scripts are byte-identical in the plugin mirror; the pre-push plugin-export-drift check will pass.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage bounded fresh-eye reviewer (separate agent context, read-only).
- Requested spawn fields: the bundle diff (origin/main..HEAD), the 0.48.0 release decision, seven angles (bump level, update_instructions accuracy, generated-surface honesty, operator risk/publish boundary, issue-close hygiene, #363 design, #364 design), and a git-show-backed evidence requirement.
- Host exposure state: applied
- Application state: host-confirmed: subagent af184488c4aa97cb1 completed; returned a one-line verdict plus per-angle findings and five structured findings with file/git citations, confirming no act-before-ship items.

## Fresh-Eye Satisfaction

Reviewer verdict: **PUBLISH-WITH-NITS — no blockers, no act-before-ship.** All
seven angles scored strong/acceptable: bump (minor correct), update_instructions
(behavior change disclosed, framing matches code), generated surfaces
(byte-identical mirror, drift gate green), operator risk (fail-closed disclosed +
safe), issue-close hygiene (#363/#364/#365 genuinely resolved), and both advisory
designs (no false-fire, signals reused without drift, asserted non-blocking). The
two nits (F2 update_instructions no-upstream edge note; F1 expected pre-bump
version state) are deferred, not blockers. Safe to run
`publish_release.py --part minor --execute` and close #363/#364/#365.
