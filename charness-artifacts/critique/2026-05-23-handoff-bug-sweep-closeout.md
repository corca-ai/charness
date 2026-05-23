# Critique Closeout: Handoff Bug-Sweep (selector / followup-tail / set-version)

Date: 2026-05-23

## Execution

Five bounded fresh-eye subagent passes (parent-delegated) matching the goal's
design→impl→pattern→RCA→final shape, on a fresh defect hunt (the open-issue
queue held only deferred ideation #184/#185, so the target was latent bugs in
recently-churned subsystems):

- Three discovery `general-purpose` subagents hunted issue+retro, release+eval_registry,
  and artifact_validator. Concrete defects: A (`parse_selector` accepts issue#<1),
  B (`is_valid_followup_tail` punctuation false-positive), C (`bump_version --set-version`
  unvalidated before manifest write). Clean: retro digest determinism, eval_registry
  immutability, release fail-closed paths, pointer-write symlink safety, the
  multi-issue closing-keyword guard (already exists in `issue_verify_closeout.py`).
- Design critique subagent: all three SHIP; flagged Fix A must reject `start < 1`
  in the range form and confirmed `is_selector("0")` stays False; no range cap.
- Impl+pattern-scan+RCA subagent: fixes correct + tests non-vacuous; Class-A scan
  surfaced `brief-path --number` as a sibling. I verified empirically — it does NOT
  silently succeed (raises loudly, exit 1) — so the only residual was an error-surface
  inconsistency.
- Two closeout angle subagents (behavior-narrowing regression; export/validation
  completeness): no regression (no checked-in artifact uses `deferred.`); exports
  byte-identical; owning-surface validators rc=0.
- Counterweight subagent: SHIP; promoted the `brief-path` structured-error parity
  to Bundle-Anyway.

## Fresh-Eye Satisfaction

parent-delegated

## Packet Consumed

charness-artifacts/critique/2026-05-23-115119-packet.md

## Target

`references/code-critique.md` substrate — post-impl review of a public-skill +
validator + test bug-sweep.

## Change

- A (`skills/public/issue/scripts/issue_runtime.py`): `parse_selector` rejects
  issue number `< 1` for both single and range forms, matching
  `issue_brief.py:53` (`brief_artifact_relpath` already rejected `<= 0`).
- B (`scripts/artifact_validator.py`): `is_valid_followup_tail` strips trailing
  `.,;:` before the `deferred` token compare, so `deferred.` / `deferred,` are
  correctly rejected as a bare deferred (no anchor). Shared by debug/retro/critique.
- C (`skills/public/release/scripts/bump_version.py`): `--set-version` is run
  through `parse_version()` before `write_packaging_version`, failing closed
  before mutating the canonical packaging manifest (parity with the `--part` path).
- Bundled (`skills/public/issue/scripts/issue_tool.py`): `command_brief_path`
  wraps `build_brief_path_payload` so a non-positive `--number` emits structured
  `{"ok": false, "error": ...}` (exit 1) like its sibling commands, not a raw traceback.

## Findings

All three primary fixes are behavior-narrowing (reject inputs previously accepted).
The regression risk concentrated in Fix B because the consuming validators glob
ALL checked-in artifacts, not just changed paths — but no checked-in artifact has
a `follow-up: deferred.`/`deferred,` tail, so the stricter grammar fails nothing
today. Fix A's strictness only flips `is_selector("0")` to False, which is harmless
in `split_resolve_args`. Fix C's `VERSION_RE` accepts all in-repo versions.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/scripts/issue_tool.py:223 | action: fix | note: `command_brief_path` was the lone command in its module emitting a raw traceback instead of structured `{"ok": false}`; wrapped to restore agent-facing JSON parity with `command_select`/`command_resolve_target`
- F2 | bin: over-worry | evidence: weak | ref: skills/public/issue/scripts/issue_runtime.py:84 | action: document | note: extracting a shared `parse_issue_number()` helper for `parse_selector` + the `--number` args is premature abstraction at two sites; per-site positivity checks suffice
- F3 | bin: over-worry | evidence: weak | ref: skills/public/issue/scripts/issue_runtime.py:89 | action: document | note: no range-width cap on `1-100000`; input is operator-controlled local CLI, any cap value is arbitrary, so skipping it is correct
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_critique_artifacts.py:186 | action: defer | note: artifact validators `glob("*.md")` over all checked-in artifacts, so a future stricter grammar could retro-fail history; empirically clean today, guard is speculative

## Deliberately Not Doing

- A shared `parse_issue_number()` helper or argparse type validator: rejected as
  premature abstraction; revisit only at a third positivity call site.
- A selector range-width cap: rejected; operator-controlled local input, no
  untrusted source, arbitrary cap value.
- A changed-paths-only guard for the artifact validators' glob: deferred; real
  premise but no artifact fails today and the guard is unrelated to this sweep.

## Next Move

- Verify the read-only quality gate, then commit all four fixes + tests + synced
  exports in one commit. No GitHub issues to close (these were undocumented latent
  bugs); only #184/#185 (deferred ideation) remain open.
