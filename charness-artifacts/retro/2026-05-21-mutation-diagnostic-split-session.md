# Session Retro: Mutation Diagnostic Split

Date: 2026-05-21
Mode: session

## Context

This slice continued the mutation regression sibling scan by splitting changed
file exclusions into file-coverage-floor and mutation-line buckets. The change
keeps legacy `uncovered_changed_files` compatibility while making the next #189
repair target visible.

## Evidence Summary

- Full sampler replay: `b882398..HEAD` selected
  `scripts/worktree_doctor_state.py`, reported `6` file-floor exclusions, and
  reported `3` mutation-line exclusions.
- Quality: `./scripts/run-quality.sh --read-only` passed after the length fix.
- Closeout: `python3 scripts/run_slice_closeout.py --repo-root .` completed.
- Fresh-eye critique found no blockers and confirmed plugin sync.

## Waste

- The first implementation exceeded the 480-line Python file limit in
  `scripts/check_mutation_score.py`; the quality gate caught it only after the
  broader run.

## Critical Decisions

- Preserve the legacy union key instead of replacing it, because older score
  checks rely on it as a fatal changed-scope signal.
- Do not relax mutation eligibility policy in this slice; make the next direct
  test target easier to choose instead.

## Expert Counterfactuals

- Gary Klein lens: check known local tripwires like file length immediately
  after adding a formatter to a near-limit script.
- Daniel Kahneman lens: label the legacy bucket as a compatibility union so the
  old mental model does not keep anchoring future debugging.

## Next Improvements

- workflow: after adding diagnostic rendering to a near-limit script, run the
  file-length gate before full quality.
- capability: next mutation repair should add direct tests for the file-floor
  exclusions before broad sampler policy changes.
- memory: keep release proof suppression as the next sibling bug axis after the
  mutation changed-file eligibility path is made closable.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-21-mutation-diagnostic-split-session.md`
