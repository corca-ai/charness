## Context

`achieve` goal: split `scripts/run_slice_closeout.py` (474/480, in the length
warn band) into the orchestrator plus a cohesive reporting module,
behavior-preserving, with the plugin mirror byte-synced. Outcome: reporting
block (8 fns) extracted to `scripts/slice_closeout_reporting.py`; file 474→370/480
(110 headroom); mirror synced; read-only quality gate 73/0. Awaiting maintainer push.

## Evidence Summary

- Goal artifact + slice log (`charness-artifacts/goals/2026-06-08-...md`).
- Critique artifact (`charness-artifacts/critique/2026-06-08-run-slice-closeout-reporting-extraction.md`)
  + prepare packet.
- Behavior proof: byte-identity of the moved block vs HEAD; a 10-payload old-vs-new
  renderer equivalence battery (every branch); a counterweight 11-payload guard-branch
  battery — all 0 mismatch; 99 targeted closeout tests; `run-quality.sh --read-only` 73/0.
- Host-log probe (thread-wide): subagent spawn=4, function calls=429, repeated broad
  gates=none. Point-in-time/proxy signals, not a per-goal cumulative total.

## Waste

- **One avoidable gate failure cost a second full read-only gate run (~45s).** I
  hand-wrote the critique artifact and omitted the `## Reviewer Tier Evidence`
  section that `validate_critique_artifacts` requires; the gate caught it, I added
  the section, and re-ran the whole gate. Root cause: the critique skill's
  documented path produces a *prepare packet* with the reviewer-tier shape but does
  not route final-artifact authoring through `scaffold_critique_artifact.py` (the
  scaffold exists but no `SKILL.md`/reference cites it), so a hand-author can miss
  validator-required sections. Low-severity, but repeatable.
- Otherwise low waste: the byte-preserving migration script and pre-captured
  baselines made the proof cheap and unambiguous on the first pass.

## Critical Decisions

- **Deterministic byte-preserving migration script (not hand-transcription).**
  Turned "behavior-preserving" from a claim into a `git show HEAD` byte-identity
  proof — the strongest evidence shape for a pure move. Changed the whole
  verification posture.
- **Capture before-baselines BEFORE mutating.** Enabled the output diff; without it
  the behavior comparison would have been reconstructive and weaker.
- **Reporting-block-only seam, block-chain deferred.** The single seam dropped the
  file to 370/480, so further splitting was correctly declined as scope creep.
- **Counterweight that BUILT its own guard-branch battery** rather than only
  triaging paranoia — independently re-proved preservation on the branches a
  happy-path battery skips (non-dict recs, falsy values, non-list headroom,
  trailing-newline ternary).

## Expert Counterfactuals

- **Gary Klein (pre-mortem).** Before writing the critique artifact, a 10-second
  "what gate rejects this file?" pre-mortem would have surfaced the
  `validate_critique_artifacts` required-section list and avoided the re-run. The
  changed action: consult the validator's required shape (or the scaffold) before
  hand-authoring any gated artifact.
- **John Ousterhout (deep modules).** Would endorse the seam: the new module is a
  deep-ish module — one public entrypoint (`print_text`) hiding 7 private helpers and
  a single cross-module dependency — a simple interface over real functionality, not
  a shallow grab-bag. Confirms the cut location rather than changing it.

## Next Improvements

- **workflow:** When authoring a charness critique artifact, check
  `validate_critique_artifacts` required sections (or run
  `scaffold_critique_artifact.py`) BEFORE hand-writing — `## Reviewer Tier Evidence`
  with 4 fields and a host-exposure-state from the fixed set is mandatory.
- **capability:** The critique skill's prepare-packet path and the
  `scaffold_critique_artifact.py` scaffold are disconnected; the scaffold is
  uncited in `SKILL.md`/references. Candidate follow-up: cite the scaffold from the
  critique skill (or have prepare-packet emit an artifact stub with the required
  headings) so the validator-required shape is present by construction.
- **memory:** Persisted to recent-lessons (below) so the next critique author does
  not relearn the reviewer-tier-evidence requirement.

## Sibling Search

Transferable pattern: *authoring a gate-validated artifact by hand instead of via
its scaffold/validator-shape, then tripping the gate.* Four-axis scan across
charness artifact types:

- **goal** artifacts → authored via `achieve` `upsert_goal.py` / `append_slice_log.py` (helper-routed; safe).
- **retro** artifacts → authored via `persist_retro_artifact.py` (helper-routed; safe).
- **debug / handoff** artifacts → have `scaffold_*` helpers in their skills (helper-routed).
- **critique** artifacts → `scaffold_critique_artifact.py` EXISTS but is uncited in the
  critique skill, so the documented path is hand-authoring. **This is the lone live sibling**
  and the source of this session's miss.

Decision: the gap is specific to the critique artifact's uncited scaffold — recorded
as the `capability` follow-up above (cite/wire the scaffold). Not filed as a separate
issue to avoid issue sprawl; captured in recent-lessons and this retro for the next
critique author.

## Persisted

yes — see persisted path in closeout.
