# Quality Critique Sweep Bug Fixes Debug
Date: 2026-05-24

## Problem

The sweep found one active mutation regression (#211) and four self-fixable
sibling defects: RCA impossible timestamps passed validation, constant-derived
current-pointer writes were missed, advisory `sync-support` gaps returned
failure, and standing-test economics could crash on disappearing pytest temp
paths.

## Correct Behavior

Given the RCA ledger slice is in a scheduled mutation window, when the sampler
builds coverage and mutation-line eligibility, then changed RCA scripts must not
be excluded by uncovered changed lines or mutation-line coverage false
negatives. Given an RCA event declares `ts`, the validator must reject malformed
date-times and impossible calendar values. Given a current pointer filename is
hidden behind a simple constant, the scanner must still flag direct writes.
Given support sync succeeds and the remaining doctor finding is advisory, the
sync-support command should report the finding but return success. Given pytest
temp roots are volatile during xdist runs, standing-test economics inventory
should skip paths that disappear mid-scan instead of failing the caller.

## Observed Facts

- `gh issue view 211 --json body` reported changed-line blockers for
  `scripts/rca_ledger_lib.py` and `scripts/record_rca_event.py`, plus
  mutation-line exclusions for `scripts/validate_rca_ledger.py`.
- Reproducing the sample locally against `ad0f233..HEAD` initially produced
  `changed_line_uncovered_changed_files = ["scripts/rca_ledger_lib.py",
  "scripts/record_rca_event.py"]` and mutation-line exclusions for all three RCA
  scripts.
- A temp ledger containing `ts: "2026-99-99T99:99:99Z"` returned valid before
  the fix because `jsonschema.FormatChecker()` was not used and the schema regex
  only checked shape.
- A temp repo with `CURRENT = "latest.md"; target = Path(...) / CURRENT;
  target.write_text(...)` returned clean from `check_current_pointer_writes.py`.
- `./charness tool sync-support --dry-run --json` returned 1 when `defuddle` was
  missing, even though that doctor disposition is advisory-install-needed.
- `./scripts/run-quality.sh --read-only` later failed inside
  `test_standing_test_economics_ignores_generated_mutant_tree` because the
  inventory subprocess raised `FileNotFoundError` for a concurrently removed
  `/home/hwidong/.cache/tmp/pytest-of-hwidong/garbage-*` path.

## Reproduction

- Mutation sample before fix: temp `cosmic-ray.toml`, `MUTATION_BASE_SHA=ad0f233`,
  `MUTATION_HEAD_SHA=HEAD`, full coverage probe.
- Timestamp/current-pointer/sync-support: use focused temp-ledger, temp-repo, and
  missing-manual-binary checks.
- Pytest-temp race: full read-only quality while xdist workers create and clean
  temp roots.

## Candidate Causes

- RCA tests did not cover several optional and error branches in the new scripts.
- Mutation-line coverage treated coverage as line-exact, so mutations on
  continuation lines of an executed multiline statement looked uncovered.
- The first continuation-line fix over-propagated across enclosing `FunctionDef`
  bodies; counterweight review caught this before closeout.
- RCA timestamp validation trusted JSON Schema `format` without a format checker
  or explicit calendar parse.
- Current-pointer scanning looked only for literal `latest.*` strings or names
  assigned from such expressions, not simple filename constants.
- `sync-support` checked raw `doctor_status` instead of the already-normalized
  `doctor_disposition` used by `tool doctor`.
- Standing-test economics caught `OSError` when opening a directory but still
  used traversal paths that could raise after iteration had already started.

## Hypothesis

If RCA optional/error branches are covered, timestamp validation uses both
`FormatChecker` and a calendar parse, mutation-line coverage propagates only
within executed multiline simple statements, current-pointer scanning resolves
module-level filename constants while respecting local shadowing, and
sync-support exits on blocking doctor dispositions only, then #211's sampler
blocker disappears and the sibling defects get deterministic tests. If pytest
temp inventory uses tolerant iterator/stat helpers, volatile cleanup cannot
crash the standing economics scan.

## Verification

- Targeted tests for current-pointer writes, mutation sampling, RCA ledger, and
  sync-support passed (56 passed).
- `ruff check ...` over touched scripts/tests passed.
- `python3 scripts/check_python_lengths.py --repo-root .` passed.
- `python3 scripts/validate_packaging.py --repo-root .`,
  `python3 scripts/validate_packaging_committed.py --repo-root .`, and
  `python3 scripts/check_current_pointer_writes.py --repo-root . --require-empty`
  passed after plugin sync.
- After the temp-scan race fix, standing-test economics tests passed (5 passed)
  and touched-file `ruff check` passed.
- Pre-commit sample caveat: before commit, `MUTATION_HEAD_SHA=HEAD` cannot see
  uncommitted changes; after commit, rerun the sampler against a window that
  includes the committed fix.

## Root Cause

#211 was not one bug. It was a bundle of proof-boundary mistakes in the new RCA
ledger slice plus sibling gate holes:

- The RCA ledger scripts were behavior-tested but not branch-covered enough for
  a changed-line gate that treats every newly-added statement as in scope.
- Mutation-line coverage used physical mutation line membership rather than
  executed statement membership, so continuation lines in executed multiline
  statements were false negatives.
- Timestamp schema validation declared `format: date-time` but did not enable a
  format checker and did not parse the calendar value.
- Current-pointer write detection assumed the filename literal stayed visible at
  the write expression.
- `sync-support` interpreted advisory install gaps as command failure by looking
  at raw status instead of the disposition contract.
- Standing-test economics assumed retained pytest temp directories were stable
  for the duration of a scan, but xdist and pytest cleanup can remove sibling
  directories while an inventory subprocess is traversing the same temp root.

## Detection Gap

- mutation sample | continuation lines of executed multiline statements looked
  uncovered | add statement-span continuation coverage, with a negative test
  proving function-body over-propagation does not occur.
- RCA ledger validation | impossible date-time accepted | add FormatChecker,
  calendar parse, and impossible timestamp regression.
- current-pointer scanner | simple constant-derived `latest.*` writes missed |
  add module constant propagation plus local-shadowing regression.
- sync-support CLI | advisory doctor status failed support sync | align exit
  code to `doctor_disposition` and test both advisory and blocking paths.
- standing-test economics | volatile pytest temp roots crashed scan | replace
  fragile traversal with tolerant iterator/stat helpers and add a disappearing
  temp-dir regression.

## Sibling Search

- Mental model: "shape-valid and behavior-tested is enough for new helper
  scripts." Decision: false for changed-line/mutation-line gates; proof: #211
  reproduction and targeted branch coverage.
- Same layer: mutation changed-scope incidents
  `2026-05-24-mutation-changed-line-uncovered-guard-recurrence.md` and
  `2026-05-24-mutation-changed-scope-gap-whole-file.md`. Decision: same family;
  proof: both involve changed-window proof boundaries.
- Abstraction up: current-pointer writer safety. Decision: fixed now for simple
  constants; proof: new scanner tests and clean repo scan.
- Specialization down: RCA recorder duplicate appends by `class_key`. Decision:
  defer to spec because metric semantics change; proof: filed #212.
- Adjacent operator seam: validators needing implicit `PYTHONPATH`. Decision:
  defer; proof: filed #213.
- CLI review depth: structural CLI ergonomics inventory inputs missing.
  Decision: defer; proof: filed #214.

## Seam Risk

- Interrupt ID: quality-critique-sweep-bug-fixes
- Risk Class: contract-freeze-risk
- Seam: scheduled mutation changed-window proof, RCA metric validation,
  current-pointer writer detection, external-tool command exit semantics, and
  volatile pytest temp inventory
- Disproving Observation: targeted tests and local validators pass; post-commit
  mutation sampler still needs to run with the fix included in `base..HEAD`.
- What Local Reasoning Cannot Prove: hosted scheduled mutation run after push.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: this file

## Prevention

Keep proof boundaries explicit: changed-line gates need committed-window proof,
mutation-line coverage must not confuse physical continuation lines with
unexecuted statements, JSON Schema `format` needs a checker or explicit parser,
scanner heuristics need negative tests for both misses and false positives, and
CLI lifecycle commands should exit on disposition contracts rather than raw
status names.
