# Remote CI Changed-Line Reconciliation Debug
Date: 2026-08-09

## Problem

`Quality Core` run `31299978312` failed at `origin/main@18a9a439` because the
changed-line mutation mirror found uncovered lines in
`check_regenerable_facts.py` and `regenerable_facts_lib.py`, while the local
focused lane classified both files as unmapped and `run-quality.sh` rendered the
result `UNPROVEN` without failing.

## Correct Behavior

Given an eligible changed Python file that an existing standing test reaches,
when the local focused selector builds its test set, then it maps that test and
the focused coverage run observes the same changed lines the remote broad mirror
will judge. A real coverage gap blocks locally; an honest covered line passes in
both channels.

## Observed Facts

- `gh run view 31299978312` binds the failure to head
  `18a9a439c51f692d290d2be8765c1d7adcf404d9`; core deterministic gates passed.
- The fresh CI coverage report named six missing changed lines in
  `check_regenerable_facts.py` (20, 63, 102, 106, 107, 122) and two in
  `regenerable_facts_lib.py` (183, 184).
- `suggest_mutation_coverage_command.py --base-sha ec67291e... --detail`
  classifies the range `partial` and names exactly those two files as unmapped.
- `tests/quality_gates/test_regenerable_facts.py` reaches the library through
  `load_local_skill_module(str(SKILL_SCRIPTS / "check_regenerable_facts.py"),
  "regenerable_facts_lib")`; the selector does not resolve that alias-plus-nested
  path expression.
- A focused coverage run of that test passes 26 tests, omits the entry script
  entirely from the report, and leaves library lines 183-184 missing.

## Reproduction

- Remote: `GH_PAGER=cat gh run view 31299978312 --repo corca-ai/charness --log-failed`.
- Selector: `python3 scripts/suggest_mutation_coverage_command.py --repo-root .
  --base-sha ec67291e88c76c45e5604882152bc021a915458b --detail`.
- Coverage: run `coverage` over
  `tests/quality_gates/test_regenerable_facts.py`; 26 pass, the entry script has
  no file row, and the library misses 183-184.

## Candidate Causes

- CI dependency or runner drift changed behavior only remotely — disconfirmed:
  the failure is a fresh source-line coverage report after the shared suite.
- A stale coverage fingerprint attributed old data to the pushed head —
  disconfirmed: CI produced the report in the failing job over the bound range.
- The standing test is absent — disconfirmed: the focused test exists and 26
  cases pass, but its dynamic loader path is outside selector recognition.
- The selector misses a real dynamic-loader dependency and the selected test
  does not exercise entry-script/fallback branches in-process — confirmed.

## Hypothesis

- If the selector recognizes filename literals nested inside the existing
  `load_local_skill_module` boundary, it will map both files through loader
  ancestry to `test_regenerable_facts.py`; if that test directly imports the
  entry script and drives the named fallback branches, focused coverage will
  include all eight CI targets. Disconfirmer: rerun the selector and focused
  changed-line consumer over the same `ec67291e...` range after the repair.

## Verification

- confirmed diagnosis — after the mapper-only repair, the old-range final
  consumer exited 1 and named exactly entry lines 20, 63, 102, 106, 107, 122 and
  library lines 183, 184. After the direct branch tests, focused coverage
  executed all eight targets and the consumer reported no blocking lines, but
  the wrapper exited 3 with `changed_line_proof: unverified-dirty-worktree`.
  Post-commit final-consumer proof and hosted CI remain pending.

## Root Cause

The local accelerator treats textual reachability as test reachability but does
not model filename constants nested inside its supported dynamic loader call.
That false absence activates deliberate non-blocking mapper policy. Separately,
the real test validates the CLI mostly by subprocess and loads only its sibling
library in-process, so the remote broad probe correctly finds entry/fallback
branches uncovered. The local final surface therefore cannot distinguish a
mapper blind spot from an actual coverage gap before the push.

## Invariant Proof

- Invariant: when the focused selector can establish that a standing test reaches
  an eligible changed file, the local pre-push consumer must judge that file's
  changed lines before a push can be presented as covered.
- Producer Proof: the selector currently emits `partial` and the exact two-file
  unmapped list despite the dynamic loader call in the standing test.
- Final-Consumer Proof: local `run-quality.sh` renders the state `UNPROVEN`, while
  remote run `31299978312` blocks the same files from a broad coverage channel.
- Interface-Shape Sibling Scan: `subprocess_only_coverage_advisory.py` consumes
  the same mapper; `tests/test_nose_inprocess_coverage.py` records the same
  subprocess/dynamic-loader opacity class.
- Non-Claims: no repaired local verdict, pushed commit, or green remote CI run
  exists yet.

## Detection Gap

- focused selector | did not map an existing loader-reached test | recognize
  string constants nested in the supported loader call and pin it with a fixture.
- regenerable-facts tests | subprocess/library-only observation omitted eight
  executable lines | load the entry script in-process and drive each fallback.
- local aggregate | correctly said `UNPROVEN` but did not block deliberate mapper
  policy | repair mapper evidence rather than reverse the recorded policy.

## Sibling Search

- Mental model: a test file's existence means both the selector can discover its
  dependency and coverage can observe every process boundary it crosses.
- same layer: `scripts/suggest_mutation_coverage_command.py` dynamic loader
  matching | decision: same bug, fix now | proof: local payload proof.
- abstraction up: `scripts/subprocess_only_coverage_advisory.py` reuses the same
  mapper | decision: same bug, fix now through the shared mapper | proof: static
  import and local payload proof.
- specialization down: `tests/quality_gates/test_regenerable_facts.py` omits the
  entry script and fallback | decision: same bug, fix now | proof: focused
  coverage report.
- mental-model sibling: `tests/test_nose_inprocess_coverage.py` documents the
  same opaque subprocess plus `load_local_skill_module` class | decision:
  intentional existing prevention example | proof: static scan only.
- cross-file: `scripts/subprocess_only_coverage_advisory.py` and
  `tests/test_nose_inprocess_coverage.py`.

## Seam Risk

- Interrupt ID: remote-ci-changed-line-reconciliation
- Risk Class: external-seam
- Seam: local focused test selection and coverage -> local aggregate -> GitHub broad changed-line mirror.
- Disproving Observation: the same fixed base range maps both files locally,
  focused coverage judges all eight target lines, and the broad consumer agrees.
- What Local Reasoning Cannot Prove: GitHub CI on the repaired commit without an
  explicitly approved push.
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: open
- Critique Required: yes
- Next Step: spec
- Handoff Artifact: charness-artifacts/spec/2026-08-09-remote-ci-changed-line-reconciliation-contract.md

## Prevention

Repair the shared selector at the loader boundary, add direct failure-branch
coverage in the owning test, prove the exact old CI range through the focused
consumer and broad changed-line consumer, and keep remote CI as an explicit
post-push non-claim until read back through GitHub.
