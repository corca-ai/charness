# Bug Pattern Sibling Scan Debug
Date: 2026-05-21

## Problem

The repo had recent repeated bug-fix commits and closed issues where rules existed in prose, but sibling code paths still allowed the same class of bug to recur.

## Correct Behavior

Given prior bug fixes, debug notes, retros, and closed issues identify a recurring failure pattern, when a sibling implementation has the same structure, then Charness should either prove the sibling is already guarded or add a low-noise guard before claiming the pattern is handled.

## Observed Facts

- Closed issues #138, #145, #175, #176, #181, #183, #186, and #187 show recurring failures around current-pointer writes, silent advisory states, closeout carrier verification, path/root assumptions, and mutation-scope validity.
- `docs/conventions/operating-contract.md` already names the `latest.md` symlink overwrite hazard from #138 and says other rolling-pointer skills inherit the risk.
- `skills/public/release/scripts/publish_release_artifact.py` wrote `charness-artifacts/release/latest.md` through `Path.write_text`.
- `scripts/check_python_filenames.py` and `scripts/check_test_production_ratio.py` used raw `rglob("*.py")`, so gitignored generated files could still influence standing quality gates after the gitignore-scan hygiene fix.
- Fresh-eye subagents independently identified current-pointer writer safety and gitignore-aware standing gate gaps as likely real sibling risks.

## Reproduction

- Current-pointer shape: create `charness-artifacts/release/latest.md` as a symlink to a prior release record, then call `write_release_artifact`; the old implementation would follow the symlink and overwrite the prior record.
- Gitignore shape: create a git repo with `scripts/GeneratedName.py` or `scripts/generated.py` ignored by `.gitignore`; the old Python filename and test-production-ratio gates would still scan the ignored files.

## Candidate Causes

- The #138 fix was local to gather and debug scaffolding instead of a shared current-pointer write helper used by later writers.
- The gitignore scan hygiene gate checked a selected family of inventory scripts, but older standing gates still had raw `rglob` traversal.
- Quality closeout focused on the latest mutation and release incidents, leaving low-cost sibling scans in adjacent standing gates for the next pass.

## Hypothesis

If the remaining sibling bugs are structural, then replacing direct current-pointer writes with a symlink-safe helper and routing the two standing Python scans through `repo_file_listing` should make targeted symlink/gitignore regression tests pass and keep the new scanner clean.

## Verification

- `python3 scripts/check_current_pointer_writes.py --repo-root . --require-empty` passed.
- `python3 -m pytest -q tests/quality_gates/test_current_pointer_writes.py tests/quality_gates/test_python_filename_convention.py tests/quality_gates/test_test_production_ratio.py tests/quality_gates/test_quality_runner.py -m 'not release_only'` passed with `38 passed, 2 skipped`.
- `python3 scripts/check_python_filenames.py --repo-root . && python3 scripts/check_test_production_ratio.py --repo-root . --json && python3 scripts/check_current_pointer_writes.py --repo-root . --require-empty` passed.
- `./scripts/run-quality.sh --read-only` passed with `65 passed, 0 failed`.

## Root Cause

Prior fixes addressed specific instances but did not fully generalize the enforcement mechanism. Current-pointer safety remained a convention for non-gather writers, and gitignore-aware traversal was promoted for several inventories without moving every standing Python source scan onto the shared git-visible file listing.

## Detection Gap

- current-pointer writer safety | direct `latest.md` / `latest.json` writes were not scanned | add `check_current_pointer_writes.py` to `run-quality`.
- release artifact writer | no symlink regression fixture for `release/latest.md` | add release symlink preservation test.
- Python source scans | no gitignored-file fixture for filename and test/source-ratio gates | add gitignore regression tests.

## Sibling Search

- Mental model: a fixed exemplar means the pattern is fixed.
- Same axis: release/find-skills/Cautilus current-pointer writers | decision: fix now | proof: helper migration and scanner.
- Adjacent axis: standing Python filename and test/source ratio gates | decision: fix now | proof: gitignored-file tests.
- Deferred axis: mutation sample/test-command coupling and release diff failure suppression | decision: monitor/defer | proof: already surfaced by subagent scan, broader than this slice.

## Seam Risk

- Interrupt ID: bug-pattern-sibling-scan
- Risk Class: none
- Seam: repo-local quality and artifact writer behavior
- Disproving Observation: targeted regression tests pass locally.
- What Local Reasoning Cannot Prove: future artifact-family migrations will choose the right history/current classification without per-family tests.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

- Added a shared current-pointer writer that replaces a symlink pointer itself rather than following it.
- Migrated release, find-skills, and Cautilus current snapshot writers to that helper.
- Added a quality gate that rejects direct writes to `latest.md` / `latest.json` outside helper-migrated code.
- Moved two standing Python source scans to `repo_file_listing.iter_matching_repo_files` so `.gitignore` remains authoritative.

## Related Prior Incidents

- `charness-artifacts/debug/2026-05-19-issue-175-advisory-recurrence.md`: exit-zero advisory states recurring after an earlier script-silence fix.
- `charness-artifacts/debug/2026-05-20-mutation-test-command-mismatch.md`: a fixed mutation layer left a sibling sample/test-command coupling gap.
- `charness-artifacts/retro/2026-05-20-quality-treadmill-vs-root-cause.md`: quality recommendations must check existing conventions before adding new gates.
