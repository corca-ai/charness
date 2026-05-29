# Achieve Goal: Capability (closeout retro): make `check_python_lengths` a pre-commit gate

Status: complete
Created: 2026-05-29
Activation: `/goal @charness-artifacts/goals/2026-05-29-n-length-precommit-gate.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Goal

Capability (closeout retro): make `check_python_lengths` a pre-commit gate

**Source handoff entry #1: Capability (closeout retro): make `check_python_lengths` a pre-commit gate**

> (warn ~330 / fail 360 for `skills/public/*/scripts/*.py`). The
>    silent-lib-growth trap recurred twice this session — the recurrence is the
>    trigger.

## Non-Goals

- Not a release: no plugin version bump expected.
- No threshold retuning: hard limits (skill-helper 360 / repo-script 480 / test
  800), warn bands (330 / 432 / 720), and function limits stay exactly as-is.
  The handoff's "fail 360" already holds; this work is wiring only.
- Do not change or weaken the existing pre-push whole-repo run in
  `run-quality.sh`; the pre-commit gate is purely additive.
- Do not absorb adjacent handoff entries (#250, #243, #219, ...).

## Boundaries

- In scope: `scripts/check_python_lengths.py` (new `--paths` mode),
  `plugins/charness/scripts/check_python_lengths.py` (export sync),
  `.githooks/pre-commit` (staged-`*.py`-conditional invocation),
  `tests/quality_gates/test_python_and_security_gates.py` (new `--paths`
  coverage).
- Pre-commit scope is **staged-only** by decision (see Interview Decisions):
  block only on Python files in the commit; show WARN only for staged in-band
  files. Pre-existing over-limit files not in the commit stay covered by the
  pre-push whole-repo run.
- Portable per implementation-discipline: the hook is repo-local (`.githooks/`),
  no host-specific assumption; `--paths` is additive and backward-compatible
  with the glob default `run-quality.sh` uses.
- Canonical script is `scripts/check_python_lengths.py` — some shell output
  renders it as `n.py` (a display-layer rewrite); never write `n.py`.
- Stop conditions: if sharing limit logic between glob and `--paths` modes would
  push `check_python_lengths.py` past its own warn band (145 lines today — ample
  headroom), name it rather than silently growing the file.

## User Acceptance

After activation, the user can confirm:

1. Staging a Python file that **exceeds** its hard limit (e.g. a skill-helper
   script > 360 lines) and committing → pre-commit **blocks** with the exact
   `... exceeds limit ...` error and exit 1.
2. Staging an in-band file (e.g. 355 lines, band [330, 360]) → commit succeeds
   (exit 0) and prints the single `WARN:` line for that file.
3. Staging a Python file comfortably under the warn band → commit passes with
   no length noise.
4. A commit staging no `scripts|skills|tests` `*.py` files → length check is
   skipped entirely.
5. The pre-push full gate (`run-quality.sh` whole-repo length check) is
   unchanged and still catches pre-existing over-limit files.
6. `plugins/charness/scripts/check_python_lengths.py` is byte-identical to the
   source script.

## Agent Verification Plan

- **Low-cost (per slice, deterministic, sub-second):**
  - `python3 -m py_compile scripts/check_python_lengths.py`; `ruff check` on
    changed files.
  - New `--paths` unit tests: over-limit file → exit 1 with exact message;
    in-band file → WARN + exit 0; under-band → quiet exit 0; mixed list.
  - Regression: existing glob/default-mode tests still green;
    `check_python_lengths.py --repo-root .` (whole-repo default) still exit 0
    (29 WARN, no fail).
  - Export parity: `diff` source vs `plugins/charness/scripts/...` identical
    (or `export_plugin` sync + clean diff).
- **High-confidence (bundle boundary):**
  - Full `pytest tests/quality_gates/test_python_and_security_gates.py` green.
  - End-to-end hook proof: create a temp over-limit file under
    `skills/public/<x>/scripts/`, `git add`, run `.githooks/pre-commit`,
    confirm `HOOK EXIT=1` with the exact error; then in-band staged → WARN +
    exit 0; then no-py commit → skipped. Unstage/cleanup after.
  - `shellcheck .githooks/pre-commit` clean.
  - `check_duplicates.py --json` sample after adding tests.
- **External / live:** none applicable — no network, host runtime, or release.
  Provider/live/release proof will be stated N/A in the final report.
- **Expected proof cost:** low (all local, seconds total).
- **Expected test-duplication pressure:** low–moderate. New `--paths` tests
  parallel the existing glob-mode tests in
  `test_python_and_security_gates.py` (659 lines now; warn band starts 720 —
  ~60 lines headroom). Keep additions tight; record a `--test-pressure` sample
  at the slice that adds tests.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add `--paths FILE...` mode to `check_python_lengths.py` (explicit file list, same per-class limits + warn bands; takes precedence over glob / `--require-git-file-listing`) + unit tests + export sync | The hook depends on this surface; it is the foundation and the only script change | New `--paths` tests green; glob-mode regression green; `py_compile` + `ruff` clean; source/plugin export byte-identical; whole-repo default still exit 0 | done |
| 2 | Wire `.githooks/pre-commit`: gather staged `scripts\|skills\|tests` `*.py`, pass via `--paths`; update any doc that enumerates pre-commit gates | Depends on slice 1; realizes the gate placement and closes the silent-lib-growth trap | E2E: staged over-limit → HOOK EXIT=1 (exact error); staged in-band → WARN + exit 0; no-py commit → skipped; `shellcheck` clean | done |

## Slice Log

### Slice 1: Slice 1: --paths mode + tests + export sync

- Objective: Add a --paths FILE... mode to check_python_lengths.py that restricts the check to the subset of given paths the whole-repo glob would also gate (same per-class limits/bands), so a pre-commit hook can run it staged-only.
- Why this approach: Reused the existing target universe via set intersection (select_targets helper) rather than reimplementing per-path classification: guarantees --paths can never gate a file the whole-repo run wouldn't (export mirrors, top-level files excluded), and keeps all limit logic single-sourced. Kept it as a small helper so main() stays under the function-length limit.
- Commits:
- What changed: scripts/check_python_lengths.py (+select_targets helper, +--paths arg; 145->178 lines); plugins/charness/scripts/check_python_lengths.py (synced via sync_root_plugin_manifests.py, byte-identical); tests/quality_gates/test_python_and_security_gates.py (+3 --paths tests: over-limit blocks, in-band warns, checks-only-listed-paths/staged-only).
- Alternatives rejected: Rejected classifying each --paths file directly without the universe walk (cheaper, but would duplicate the glob's class/match rules and risk gating out-of-universe files like the plugins/ mirror). Rejected a --no-warn/hard-only flag (the staged-only choice makes WARN naturally minimal — only staged files' bands surface).
- Targeted verification: py_compile + ruff clean; pytest -k python_lengths => 11 passed (3 new + 8 regression); whole-repo default mode exit 0 (591 files, 29 WARN unchanged); source/mirror diff IDENTICAL.
- Test duplication pressure: test_python_and_security_gates.py 659 -> 715 lines, still UNDER the 720 test warn-band floor (no new warn-band file). check_duplicates.py --json => 0 near-duplicates. 3 new tests parallel existing glob-mode tests but exercise the distinct --paths branch.
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics: when available (host token/time not exposed)

### Slice 2: Slice 2: wire .githooks/pre-commit

- Objective: Run check_python_lengths.py --paths on staged .py at commit time, inside the existing STAGED_PY guard, so over-limit files block at commit (not only pre-push).
- Why this approach: Passed ALL staged .py to --paths and let the script's universe-intersection do the filtering, instead of duplicating a scripts|skills|tests regex in bash. Single source of truth for what is gated stays in the script's glob patterns; the bash cannot drift. Placed inside the existing >0 STAGED_PY guard so a no-py commit skips it for free.
- Commits:
- What changed: .githooks/pre-commit (+ check-python-lengths step inside the staged-py block; +6-line rationale comment). Repo-local hook, not part of the exported plugin tree (aa14cad set this precedent), so no export sync.
- Alternatives rejected: Rejected a bash-side scripts|skills|tests filter before --paths (duplicates the script's universe rule, drift risk). Rejected a separate hook stanza outside the STAGED_PY guard (would need its own no-py skip).
- Targeted verification: shellcheck clean. E2E against the real hook: (1) staged scripts/ file 481 lines -> HOOK EXIT=1 'file length 481 exceeds limit 480'; (2) staged 440-line file -> WARN band line + EXIT=0 + 'pre-commit: ok'; (3) staged .txt only -> check-python-lengths NOT run, EXIT=0. No temp-file leak after cleanup.
- Test duplication pressure: No new test file growth this slice (hook E2E proven via live run, not a committed test). Hook behavior is bash; the script-side --paths logic is unit-covered in slice 1.
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics: when available

## Context Sources

- Source: handoff entry #1 (make `check_python_lengths` a pre-commit gate) — see
  [docs/handoff.md](../../docs/handoff.md).
- Gate script: `scripts/check_python_lengths.py` (hard limits + WARN bands;
  currently invoked only by `run-quality.sh`). Export mirror:
  `plugins/charness/scripts/check_python_lengths.py`.
- Target hook: `.githooks/pre-commit` (staged-`*.py`-conditional pattern).
- Tests: `tests/quality_gates/test_python_and_security_gates.py`.
- Precedent: commit `aa14cad` ("Shift cheap agent-free gates into pre-commit")
  + [recent-lessons](../retro/recent-lessons.md) gate-placement rule.

## Interview Decisions

- **Chunk selection:** chunk-1 from the `/handoff` chunker (ranked #1) — promote
  `check_python_lengths.py` from a pre-push-only gate to a pre-commit gate.
  Recurring silent-lib-growth trap (`chunked_routing_lib.py` reached 875 lines
  before pre-push caught it) is the trigger; the recurrence is the evidence.
- **Pre-commit behavior:** **staged-only, hard-fail + WARN** (user choice,
  2026-05-29). Pre-commit checks only the Python files in the commit via a new
  `--paths` mode; blocks on staged over-limit, shows WARN for staged in-band.
  Accepted tradeoff: pre-existing over-limit files not in the commit are NOT
  caught at commit time — that remains the pre-push whole-repo run's job
  (unchanged). Rationale: the documented trap file is always staged in the slice
  that grows it, so staged-only catches it while keeping commits quiet.
- **Thresholds:** unchanged (no retuning). "fail 360" already holds for skill
  helpers; this is wiring only.
- **Why pre-commit (not pre-push-only):** the repo's own gate-placement rule
  (`aa14cad`, recent-lessons) — cheap + agent-free + hard-fail belongs in
  pre-commit; the length check is sub-second over 591 files and hard-fails, so
  it qualifies. WARN stays a pre-push signal (does not fit pass/block), but a
  staged file's own WARN line is acceptable low-noise early signal.

## Plan Critique Findings

Bounded fresh-eye subagent critique (slice-level, focused on false-block /
intersection correctness, hook integration under `set -euo pipefail`, the
accepted staged-only miss, portability, and self-dogfood).

- **Verdict: safe to commit as-is — no blockers.** The reviewer independently
  re-ran py_compile, ruff, `pytest -k python_lengths` (11 passed), shellcheck,
  and live E2E for over-limit / in-band / no-py, plus probed edge cases:
  symlinked repo root, `./`-prefix / out-of-universe / outside-repo / ghost
  paths, renames (R100 filtered by `--diff-filter=ACM`; rename-with-growth
  surfaces as D+A and the new path is checked), staged-but-deleted (D excluded),
  empty-array under `set -u` (guarded), argv length (~35KB worst case ≪ ARG_MAX),
  `--no-verify` (standard bypass; pre-push re-catches), and export-mirror parity.
- **Known limitation recorded (non-blocker):** the check reads the **working
  tree** (`validate_file_length` → `path.read_text()`), not the staged blob, so
  a file staged over-limit then shrunk in the working tree passes pre-commit
  while the over-limit blob commits. This is **identical to the pre-existing
  `py_compile`/`ruff` staged steps in the same hook** (not a regression) and the
  unchanged pre-push whole-repo run catches it post-commit. Left as-is by design.
- No fixes required; no speculative churn incorporated.

## Off-Goal Findings

- None filed. The `--paths` working-tree-vs-staged-blob behavior is shared by the
  hook's existing staged steps; not worth a separate issue.

## Final Verification

**Self-verification (executed):**

- Slice 1 — `--paths` mode: `py_compile` + `ruff` clean; `pytest -k
  python_lengths` → **11 passed** (3 new + 8 regression); whole-repo default
  mode exit 0 (591 files, 29 pre-existing WARN, unchanged); source/mirror
  `diff` IDENTICAL.
- Slice 2 — hook: `shellcheck` clean; live E2E against the real `.githooks/
  pre-commit`: staged over-limit → **HOOK EXIT=1** (`file length 481 exceeds
  limit 480`); staged in-band 440 → WARN + EXIT=0 + `pre-commit: ok`; no-py
  commit → length step skipped, EXIT=0; no temp-file leak.
- Bundle boundary: full `tests/quality_gates/test_python_and_security_gates.py`
  → **31 passed**; `check_doc_links` exit 0; export mirror IDENTICAL; script
  177 lines / test file 715 lines (both under their warn bands — no dogfood
  violation).
- Gate-framed: targeted `run-quality.sh --read-only`
  (`check-python-lengths,check-python-filenames,check-python-runtime-inheritance,validate-packaging,validate-attention-state-visibility`)
  → **5 passed, 0 failed**.
- Fresh-eye critique: no blockers (see Plan Critique Findings).

**Not run (honest non-claims):**

- Full `run-quality.sh` broad suite (cautilus scenarios/proof, mutation,
  packaging-committed, all ~40 validators) was **not** run — the change is
  scoped to the length gate + hook + tests + export mirror; the relevant labels,
  the full python/security gate test file, and live E2E cover it.
  `validate-packaging-committed` compares git HEAD and is left to the commit's
  own pre-push / CI run.
- No provider, live-host, or release proof — none applicable (no network, no
  host runtime, no version bump).

## User Verification Instructions

1. Stage an over-limit Python file under a gated path and try to commit:
   `python3 -c "open('scripts/_tmp.py','w').write('\n'.join('print(%d)'%i for i in range(481)))"`
   then `git add scripts/_tmp.py && git commit -m test` → the commit is
   **blocked** with `... file length 481 exceeds limit 480`. Clean up:
   `git restore --staged scripts/_tmp.py && rm scripts/_tmp.py`.
2. A commit that stages no `.py` under `scripts|skills|tests` runs no length
   check (`charness pre-commit: check-python-lengths` does not appear).
3. The pre-push gate is unchanged: `./scripts/run-quality.sh --read-only` still
   runs the whole-repo length check.

## Auto-Retro

Closeout evidence (prescribed-skill gate, bound to goal slug):

- Retro: charness-artifacts/retro/2026-05-29-check-python-lengths-precommit-gate-closeout.md
- Host log probe: charness-artifacts/retro/2026-05-29-n-length-precommit-gate-host-log-probe.json

Session retro (auto-triggered: plugin-export surface):
[2026-05-29-check-python-lengths-precommit-gate-closeout](../retro/2026-05-29-check-python-lengths-precommit-gate-closeout.md).

Substantive findings:

- **Waste: low.** No reworked commits, no failed-gate retries, no user
  correction exposing a workflow miss. Minor friction: a display-layer rewrite
  renders `check_python_lengths` as `n`/`n.py` in some shell output — confirmed
  the true name via `python repr` and recorded it in Boundaries.
- **Critical decision:** staged-only (user choice) set the whole implementation
  shape; `--paths` = intersection with the glob universe single-sources the
  "what is gated" rule in the script, so the hook safely passes every staged
  `.py` without a drift-prone bash regex.
- **Pre-mortem lens (Gary Klein):** "assume the gate silently fails to block a
  real over-limit commit" surfaced the working-tree-vs-staged-blob limitation —
  accepted (shared with the hook's existing `py_compile`/`ruff` steps, pre-push
  backstops it).
- **Sibling search:** the working-tree-read pattern's siblings are the
  pre-existing `py_compile`/`ruff` staged steps in the same hook; no new sibling
  introduced, no follow-up filed (low severity, pre-push backstop).
- **Memory:** the gate-placement rule is now realized — `check_python_lengths`
  is the third worked example of cheap+agent-free+hard-fail → pre-commit.
