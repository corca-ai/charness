# Test/code value audit — the `check_staged_*` gate family

Status: implementation evidence, uncommitted. Date: 2026-08-31.
Base: `8093a03c8`. Prompt consumed:
`charness-artifacts/impl/2026-08-31-next-session-test-value-audit.md`.

Surface agreed with the operator: the `check_staged_*` gate family
(4 scripts / 1291 lines, 80 tests across 5 files). Chosen because the prompt's
question 3 — *is the production code under these tests duplicated?* — was most
likely to have a real answer there.

## Question 2 (reachability): clean, repo-wide

A scan for module-level test helpers never referenced anywhere (Name loads,
attribute names, string constants, function parameter names for fixture
injection, and `from x import name as alias`) reports:

| | orphaned helpers | unreachable asserts |
|---|---|---|
| before | 8 | 0 |
| after | 0 | 0 |

**Zero unreachable assertions.** The previous retro's claim that all five
`_case_*` dispatch families are now 0-orphaned holds under an independent
instrument.

Two instrument defects were found and fixed before any number was quoted:

1. The scan did not count aliased imports as references, which inflated the
   finding count 16 → 8. Caught by grep-verifying a sample, not by the scan.
2. It was given a negative control — an injected orphan in a scratch tree — and
   it detects the orphan while sparing a fixture and a live helper.

### The 8 dead helpers, all deleted

Each verified unreferenced by AST scan *and* by `grep` across every file type
(exactly one hit: its own `def`).

| helper | site | note |
|---|---|---|
| `bundle_blocker_report` | `tests/quality_gates/support.py:172` | 52 lines |
| `bundle_payload_or_report` | `tests/quality_gates/support.py:141` | 29 lines |
| `_close_issue_publish_context` | `tests/quality_gates/test_release_issue_closeout_preflight.py:127` | 16 lines |
| `write_release_surfaces` | `tests/quality_gates/seeding_support.py:166` | |
| `write_files` | `tests/quality_gates/seeding_support.py:47` | |
| `append_text` | `tests/quality_gates/seeding_support.py:42` | |
| `_verify_default` | `tests/quality_gates/test_reviewer_boundary_fingerprint.py:59` | |
| `_touch_used` | `tests/seed_cache.py:161` | redundant wrapper; line 332 calls `_touch_marker` directly |

The two `bundle_*` helpers are the substantive ones: elaborate, well-commented
diagnostics helpers that outlived their consumers when `f6a64a53e` deleted both
bundle test files. Checked before deleting — the bundle *surface* is gone too
(no `scripts/*bundle*`), so this is leftover, not a coverage hole.

### The instrument is NOT worth making repo-owned

The retro filed "capability — `novel:` add an orphaned-`_case_`-helper gate" as a
Next Improvement. Measured against the repo's existing tooling, it is not novel:

```
vulture <configured paths> --min-confidence 60   # HEAD worktree
→ reports all 8, at 60% confidence, by name and line
```

The repo already owns this via `skills/public/quality/scripts/run_dead_code_advisory.py`,
which runs a primary pass at 80% *and a sweep at 60%*. A first hypothesis that
`min_confidence = 80` in `pyproject.toml` structurally hid unused functions was
**wrong** and was discarded on reading the script: the sweep pass covers them.

They survived because the advisory is opt-in (`CHARNESS_QUALITY_DEAD_CODE=1`) and
**advisory only, never blocks** — not because nothing could see them. Building
the proposed gate would have duplicated vulture, which is the same defect class
this audit was commissioned to find, one level up in the toolchain.

## Question 3 (production duplication): confirmed, with realized drift

The env-bypass truthiness contract was restated **four times**, under three
different constant names, each a copy of
`os.environ.get(NAME, "").strip().lower() in {"1","true","yes","on"}`:

| copy | constant |
|---|---|
| `scripts/check_staged_reversion.py:70` | `_TRUTHY` |
| `scripts/check_staged_router_change.py:55` | `_TRUTHY` |
| `scripts/check_staged_worktree_consistency.py:40` | `TRUE_VALUES` |
| `scripts/helper_provenance_lib.py:41` | `OVERRIDE_TRUE_VALUES` |

This is not a cosmetic duplicate. The repo's own test prose records the drift
already happening — `tests/quality_gates/test_helper_provenance_guard.py:141-147`:

> Bare truthiness read every non-empty spelling as "on", so the escape hatch fired
> for the exact values that ask for the opposite — the same bypass inversion this
> slice repaired in `check_staged_worktree_consistency`, in the file holding the
> hardest refusal the slice added.

The same bug was found and repaired **twice**, in two copies, because a repair to
one restatement cannot reach the others.

### The measured consequence: one copy was guarded by nothing

Targeted mutant — replace each copy's predicate with the historical bug,
`bool(os.environ.get(NAME, ""))` — run against each copy's own tests:

| copy | mutant verdict |
|---|---|
| `check_staged_router_change` | killed (1 failed) |
| `check_staged_worktree_consistency` | killed (2 failed) |
| `helper_provenance_lib` | killed (6 failed) |
| **`check_staged_reversion`** | **SURVIVED (12 passed)** |

Confirmed against the whole standing suite in a detached HEAD worktree, baseline
subtracted:

```
baseline : 95 failed, 8314 passed, 18 errors
mutant   : 95 failed, 8314 passed, 18 errors   → kills ZERO tests repo-wide
```

(The 95 are worktree artifacts — unsynced plugin manifests — identical in both
runs, so they subtract cleanly.)

Test coverage of the four copies of one contract was wildly asymmetric:
worktree_consistency pinned 11 spellings, helper_provenance 8, router_change 2
(`"0"`/`"1"`), reversion **1** (`"1"` only). The unguarded copy is precisely
where the next inversion lands unseen.

## The change

Smallest change that acts on the duplication rather than the symptom:

- **New** `scripts/env_bypass.py` (34 lines) — one owner for `TRUE_VALUES` and
  `env_bypass_enabled(name)`.
- Three in-surface gates route through it; three restatements deleted.
  Net `+14 / −9` across the gates.
- **New** `tests/quality_gates/test_env_bypass.py` — the spelling table pinned
  **once** (11 off-spellings, 8 on-spellings, unset), plus one wiring case per
  gate. The wiring cases are deliberately *not* a fourth copy of the table: each
  asks only "does this gate still route through the shared helper".

`helper_provenance_lib.py`, the fourth copy, was folded in on a second pass. The
bootstrap risk flagged for it was **real and it fired**: see below.

### Verification

- Negative control on the fix — mutate the *consolidated* helper to bare
  truthiness: **0 kills → 13 failures**. The reversion gate is now guarded.
- Standing suite: **8447 passed / 0 failed** (retro baseline 8423 + 24 new tests,
  nothing removed).
- `ruff check` clean on every touched file. Plugin manifests synced.
- Two pre-existing `ruff` findings in `scripts/reviewed_input_nonblob.py` are
  present at HEAD, outside this surface, and were not touched.

## The fourth copy, and the pattern under it

Folding `helper_provenance_lib.py` into the shared helper broke
`test_retro_persistence.py::test_persist_then_repo_checker_accepts_the_repo_producer_index`
with `ModuleNotFoundError: No module named 'scripts.env_bypass'`.

The fixture copies a **hand-listed** set of `scripts/*.py` into a synthetic
checkout. `helper_provenance_lib` is in that copied set, so giving it a new
import silently widened a contract the list restates.

Read as a pattern rather than as a missing filename:

* **Symptom** — one fixture list is short by `env_bypass.py`.
* **Pattern** — hand-enumerated transitive import closures in fixtures, at four
  sites, with nothing binding them to the real import graph. Each drift is found
  by an unrelated test failing, never by a gate.
* **Pattern of patterns** — *a contract restated in a second place with no
  mechanism keeping the restatement in sync with its source.* Identical in shape
  to the bypass-truthiness duplication above (4 restatements, drifted twice) and
  to the previous retro's North Star finding (a portable skill script restating a
  digest framing across a boundary it cannot import across, and the two sides
  drifted).

This was not a first occurrence. `test_prepush_runtime_regime.py` carries a
comment recording the same incident: `classify_push_diff.py` began importing
`emit_yaml`, so `yaml_output.py` had to be added to that list by hand.

**Repair: derive the closure, do not restate it.** `tests/script_closure.py`
computes it from the import graph, covering the four spellings this repo uses —
including the dynamic `import_repo_module(__file__, "scripts.x")` and
`spec_from_file_location(..., "x.py")` forms. Without the dynamic ones the
closure for `build_retro_lesson_selection_index` is short by four files and the
fixture still dies, so a static-import-only closure would have been a second
instrument with the blind spot of the thing it checks.

Converting the two safe sites also surfaced files **both** hand lists had missed
(`script_timeout.py`, `adapter_yaml_parse.py`) — latent, not yet exercised.

Two sites were deliberately **not** converted, and the reason is the interesting
half:

* `test_prepush_close_keyword_guard`'s `guard-lonely` fixture — its list is
  incomplete *on purpose*. The test asserts a PARTIAL install crashes with exit 2
  instead of reporting a verdict, so completing its closure would delete the
  subject of the test. Over-inclusion is not safe there.
* `git_fixture_support` — already declines to install helper closures, and its
  comment says why.

Checking those two before converting them is the only reason this repair did not
become the defect it was fixing.

## Process defects in this session, recorded

- **A file-mutating harness was run in the live working tree.** Mid-run the four
  gate scripts were `ast.unparse`d (comments and shebang stripped), a background
  "completed" notification fired while the process was still running, and the two
  signals together read as a corrupted tree. Recovery was deterministic (restore
  from HEAD, reapply the 2+2+3 edits, re-verify `+14/−9` and 8447 green), but the
  harness now runs against an isolated `rsync` copy. Any future mutation
  instrument must never target the working tree.
- **The harness silently reported everything as SURVIVED** on its first run,
  because `--timeout` is not a recognised pytest flag here: the invocation
  errored, produced zero `FAILED` lines, and every mutant read as unguarded. That
  is the most dangerous possible direction for this instrument — it manufactures
  "your tests guard nothing" claims. Caught only because an `In->NotIn` swap that
  *must* fail came back clean. The harness now asserts tests actually ran and
  that the collected count matches.

A third harness defect belongs with those two: the campaign **aborted at mutant
144/618** when a mutant made `main()` fall back to `sys.argv`, so argparse
consumed pytest's own arguments and no tests ran. The "did tests actually run"
guard fired correctly but was wired as fatal, discarding 144 measured results.
Only a broken BASELINE is fatal now; a mutant that stops the suite is bucketed
as `<unattributable>` (a real behaviour change that no test can be credited
with), and results are written every mutant instead of once at the end.

## Not done

Per-test disposition (KEEP / SUBSUMED / STRUCTURAL / MERGE) for all 80 tests in
the surface, via per-mutant killer attribution over the four gate scripts
(618 mutation sites). Instrument is built, validated, and running against an
isolated copy; results pending.
