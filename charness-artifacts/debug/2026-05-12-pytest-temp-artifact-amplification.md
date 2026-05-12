# Pytest Temp Artifact Amplification Debug
Date: 2026-05-12

## Problem

Full release validation filled `/home` because pytest temp directories under
`/home/hwidong/.cache/tmp/pytest-of-hwidong` grew to roughly 1.5 TB and more
than five million files. The largest reported directories were pytest
session roots from 2026-05-12, and sampled paths included Cautilus/Charness
eval artifacts containing `codex-home/tmp` payloads.

## Correct Behavior

Given Cautilus run artifacts are useful evidence, when Charness tests seed a
synthetic repo copy, then durable evidence should remain in the real checkout
and artifact pointers while hidden runtime artifact roots are excluded from the
copy. Those roots can contain tool homes, caches, or temp trees.

Given Codex evals need an isolated home, when Charness runs an eval, then the
isolated home should be outside the repo artifact tree, inherit only auth when
requested, and be cleaned up after the runner exits.

## Observed Facts

- The user reported `/home/hwidong/.cache/tmp/pytest-of-hwidong` at about 1.5
  TB with large `pytest-7909`, `pytest-7911`, `pytest-7912`, and `pytest-7913`
  directories.
- The reported path shape included `.cautilus/runs/.../codex-home/tmp/...`. <!-- reproduction-source -->
- Checked-in `.cautilus/runs` entries are 93 small Cautilus evidence files.
  They include prompts, schemas, stderr/stdout, summaries, and `run.json`; they
  do not explain the terabyte-scale payload by themselves.
- `tests/repo_copy.py` copied the whole repo root into a session seed and did
  not exclude `.cautilus`.
- `scripts/check_coverage.py` also copied the repo root for coverage probes
  and did not exclude `.cautilus`.
- Many tests clone or copy the seeded Charness repo from the pytest temp root,
  so one oversized hidden artifact tree can be multiplied by later fixtures.
- The 2026-05-12 Codex eval runner fix now creates isolated Codex homes under
  system temp via `mkdtemp`, passes `--ignore-user-config`, copies only
  `auth.json`, and cleans the temp home unless a custom home was supplied.

## Reproduction

The exact terabyte payload was already being deleted during this investigation,
so the reproduction is structural:

```bash
pytest -q
```

Before this fix, if the working checkout contained
`.cautilus/runs/<run>/.../codex-home/tmp/...`, the session-scoped
`seeded_charness_repo` fixture copied that tree into pytest temp. Downstream
fixtures then copied or git-seeded from that already oversized seed.

## Candidate Causes

- A Cautilus or Codex eval runtime wrote `codex-home/tmp` payloads under a
  repo-local `.cautilus/runs` artifact directory.
- The pytest repo-copy fixture treated hidden runtime artifacts as normal repo
  input and copied `.cautilus` into the session seed.
- Coverage probes used a separate root-copy ignore list with the same missing
  `.cautilus` exclusion.
- Repeated release/pre-push quality runs amplified the same oversized seed
  before pytest temp cleanup could reclaim it.

## Hypothesis

If Charness excludes `.cautilus` from all repo-root copy fixtures and keeps the
Codex isolated home outside the artifact tree, then useful checked Cautilus
evidence can remain in the repo while runtime homes and caches cannot be
multiplied into pytest temp.

## Verification

Executed verification:

```bash
pytest -q tests/quality_gates/test_repo_copy_invariants.py  # passed
python3 scripts/check_test_repo_copy_invariants.py --repo-root .  # passed
python3 scripts/check_coverage.py --repo-root .  # passed
python3 scripts/validate_debug_artifact.py --repo-root .  # passed
python3 scripts/build_debug_seam_risk_index.py --repo-root . --check  # passed
```

The earlier Codex isolation proof remains the Cautilus run recorded in
`charness-artifacts/cautilus/latest.md`.

`./scripts/run-quality.sh --read-only` also found unrelated release-probe
timeout and runtime-budget closeout blockers; those were handled before
release closeout.

## Root Cause

The root cause was not the existence of Cautilus run evidence itself. The
failure was a boundary leak between runtime artifacts and test repo fixtures:
pytest and coverage copied `.cautilus` wholesale from the working checkout, so
any untracked eval runtime payload under `.cautilus/runs` became part of the
session seed and was then copied repeatedly by downstream tests.

The terabyte scale required both sides: a large runtime/cache payload under a
repo-local Cautilus artifact root, and copy fixtures that did not treat that
root as volatile.

## Seam Risk

- Interrupt ID: pytest-temp-cautilus-artifact-amplification
- Risk Class: operator-visible-recovery
- Seam: checked evaluation evidence versus untracked runtime/cache payloads
- Disproving Observation: a focused invariant test fails if `.cautilus` is
  removed from either repo-copy ignore set
- What Local Reasoning Cannot Prove: which exact Cautilus/Codex wrapper layer
  produced every deleted `codex-home/tmp` path
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep checked Cautilus evidence separate from runtime payloads. Repo-copy and
coverage-copy helpers must exclude `.cautilus`, and the Codex eval runner must
continue using a temp `CODEX_HOME` outside repo artifacts with cleanup. Future
copy helpers should expose their ignore names as constants so volatile artifact
roots can be asserted directly instead of inferred from a closure.

Fresh-eye critique satisfaction: parent-delegated. Reviewers agreed the fix
should exclude `.cautilus` from synthetic copy surfaces without deleting or
banning checked Cautilus evidence.
