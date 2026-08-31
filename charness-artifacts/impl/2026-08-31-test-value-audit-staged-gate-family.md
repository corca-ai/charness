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
**advisory only, never blocks** — not because nothing could see them.

**Corrected after review.** The heading above answers *detection* where the retro
proposed *enforcement*, and the paragraph's own next sentence concedes it: a
detector that is off by default and cannot block is not the capability a gate is.
As written the argument would prove no gate is ever worth building over any tool
that can print the same fact. Two further gaps: the sweep prints every 60%
finding and this artifact never reported the denominator, so "reports all 8" is
not evidence a human would find 8 among N; and the scan being dismissed also
measures *unreachable assertions*, which vulture cannot do at all — so
non-novelty was established for one of two dimensions and asserted for both.

The conclusion this evidence actually supports: **do not build a second detector;
make the existing one blocking, or at least non-opt-in.** That is the open move,
and it is filed here rather than closed.

## Question 3 (production duplication): confirmed, with realized drift

The env-bypass truthiness contract was restated **five times**, under four
different names, each a copy of
`os.environ.get(NAME, "").strip().lower() in {"1","true","yes","on"}`:

| copy | constant | folded in? |
|---|---|---|
| `scripts/check_staged_reversion.py:70` | `_TRUTHY` | yes |
| `scripts/check_staged_router_change.py:55` | `_TRUTHY` | yes |
| `scripts/check_staged_worktree_consistency.py:40` | `TRUE_VALUES` | yes |
| `scripts/helper_provenance_lib.py:41` | `OVERRIDE_TRUE_VALUES` | yes |
| `charness:428` (root CLI) | `bool_env` | **no — cannot import** |

The fifth was found by fresh-eye review, after the first version of this artifact
said "four times ... pinned ONCE". That was a count of copies inside the chosen
surface presented as a repo-wide count, and it told the reader the class was
closed when it was not.

That copy has to stay: `charness` is the installed standalone entry point and its
source-root probe returns `None` when no charness tree is present, so `scripts`
is not importable in the case that entry point exists to serve. It is bound to
the owner by a test that drives both implementations over every spelling, rather
than by a comment asking a future editor to remember — the same shape the repo
already uses where a portable script cannot import across its boundary.

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

Confirmed against the whole standing suite in a detached worktree, baseline
subtracted. **The first version of this evidence compared failure COUNTS**
(`95 failed, 8314 passed, 18 errors` both runs) — which is not the claim. Equal
counts are consistent with one test dying and another flipping green. Redone on
failing SETS:

```
baseline failing set : 96
mutant   failing set : 95
overlap              : 95
mutant-only (KILLED) :  0   ← the claim
baseline-only        :  1
```

The one baseline-only test is
`test_a_refused_verdict_states_its_refusal.py::test_s2_the_checkers_own_scope_carries_no_odd_backtick_count`.

What is established: it is **not mutant-attributable** (the mutation changes no
backtick and no `.md`), and the suite is **nondeterministic** here — 95 failures
in one run and 96 in another over byte-identical source.

What is NOT established, and was overclaimed as "flaky under xdist" in the first
version: the mechanism. The test is a pure scan of every `*.md` in the live tree,
so it has no ordering coupling to be flaky *through*; its result is a function of
the bytes on disk at scan time. A run-to-run difference therefore means the tree
differed, which the "3/3 standalone" evidence cannot speak to — standalone is
precisely the condition under which nothing else is writing files, so that
instrument shares the blind spot of the hypothesis it was used to test.

A follow-up measured `git status` before and after a full run: **no persistent
change, no untracked `.md` left behind**. That does not close it either, because
a file created and deleted *during* the run is invisible to an end-state check —
the same blind spot a third time. Recorded as an open question, not a resolved
one. It does not affect the 0-kill conclusion, which is about the mutant-only set.

So the conclusion survives and is now proven on sets, but the count-based
reasoning that first supported it was unsound — the counts matched by
coincidence of a flake, not because the sets were equal. Recorded because the
conclusion being right is not the same as the evidence being right.

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

### Honest line accounting

The `+14 / −9` above is scoped to the three gate bodies and is the number a
reader would otherwise carry away as the size of the change. The session's actual
footprint:

| | lines |
|---|---|
| `scripts/env_bypass.py` (new) | 34 |
| `tests/quality_gates/test_env_bypass.py` (new) | ~128 |
| `tests/script_closure.py` (new) | ~150 |
| `tests/test_script_closure.py` (new) | ~130 |
| dead helpers deleted | −110 |

The commission said "report measured numbers only", and a scoped `+14/−9` at the
headline understates the change by an order of magnitude.

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

## Question 1 (does it catch what nothing else catches): per-test disposition

Per-mutant killer attribution, 618 mutants over the four gate scripts plus
`env_bypass.py`, against the 108 collected tests. 308 killed, 310 survived.
67 tests killed something; 26 are the sole killer of at least one mutant.

| test file | irreplaceable | contributing | silent |
|---|---|---|---|
| `test_staged_test_boundaries.py` | 8 | 0 | 0 |
| `test_check_staged_worktree_consistency.py` | 6 | 7 | 3 |
| `test_check_staged_reversion.py` | 6 | 5 | 1 |
| `test_check_staged_router_change.py` | 5 | 4 | 1 |
| `test_env_bypass.py` | 0 | 22 | 3 |
| `test_staged_commit_gate_plan.py` | 0 | 1 | 36 |

**Disposition: KEEP 72, UNMEASURED 36, SUBSUMED 0, STRUCTURAL 0, MERGE 0.**

The single highest-value test is the sole killer of 20 mutants
(`test_batch_blob_reader_uses_one_git_process_for_all_paths`) — the batching
plumbing the efficiency campaign added, which the commission expected to be the
*least*-guarded code in the module.

`silent` needed a hostile pass before it could be quoted, and it did not survive
as a deletion list:

- **36 of the 44 are out of scope, not low value.** They live in
  `test_staged_commit_gate_plan.py`, whose subject
  (`staged_commit_gate_plan{,_helpers}.py`) is not among the mutated modules.
  Silence there measures my module selection, not their worth.
- **The remaining 8 are all explicable and all KEEP.** Three are the new
  argv/import-shape tests, whose subject is not expressible as a mutant of a
  module's expressions at all. Two are the whitespace spellings `"  "` and
  `" on "`, which a `.strip()`-removal operator would kill — my operator set
  (comparison/boolop/`not`/constant) has no statement- or call-deletion
  operator, so this is operator coverage, not test value. One guards a
  git-unavailable state the operators cannot produce, one guards the pre-commit
  hook file, and one drives the root CLI, which was never mutated.

So the value question, asked of tests alone, returns "they earn it" for the third
audit running. **No test in this surface is a deletion candidate on this
evidence.** The bounding fact stated plainly: a survivor here means *no mutant I
generated distinguishes it*, which is weaker than "it guards nothing".

## Critique — counterweight disposition

Two bounded fresh-eye reviewers, materially different angles (Weinberg
diagnostic + boundary ownership; Jackson problem framing), on the four commits
that had no prior critique. Both delivered `block`-weight findings. Every finding
below was verified in code before it was acted on; two were disproved.

Fresh-eye satisfaction: `parent-delegated`. Packet
`charness-artifacts/critique/2026-08-31-131926-packet.json`
(identity `c7e4c0bb…`). A first pair of reviewers completed but their reports
never reached this context; they were re-run rather than reported as delivered.

### Act Before Ship — all fixed

| finding | disposition |
|---|---|
| `check_staged_worktree_consistency` dies at import through its own scheduled argv (`ModuleNotFoundError: No module named 'scripts'`) | fixed `1d0993a34`; real-process test added, fails on the pre-fix file |
| `script_closure` misses `import x` and `from scripts import x`; `task_run.py` closure silently omitted `task_run_completion.py` | fixed `ba284321d`; deriver had no test of its own, now does |
| `pytest_configure` turned the new seed-cache refusal into INTERNALERROR / zero tests collected on any dubious-ownership checkout | fixed `c75bfe7cd`; degrades instead, message names both remedies |
| Two more unknown-is-not-empty collisions plus NUL-framing ambiguity in the seed digest | fixed `c75bfe7cd`; length-prefixed, pinned |
| Fifth bypass copy in the root CLI, unmentioned; "pinned ONCE" false repo-wide | fixed `17bbcedf8`; bound by test, drift-verified |
| `helper_provenance_lib` spent its stdlib-only property with no analysis | fixed `17bbcedf8`; dual-path restored |
| My negative-control test asserted the mechanism twice, not the property | rewritten `c75bfe7cd` |

### Bundle Anyway — done in place

Vulture argument corrected (detection ≠ enforcement); "four copies" → five;
scoped `+14/−9` given honest accounting; "flaky" downgraded to an open question
with its instrument's blind spot named.

### Over-Worry — rejected with evidence

- *`source_env_present` (`charness:446`) is the historical bare-truthiness bug.*
  It answers PRESENCE, a legitimately different predicate, and its one caller
  wants exactly that.
- *`script_closure` drops three-segment `scripts.a.b` paths.* No such subpackage
  or import exists in this repo; the two directories under `scripts/` hold no
  importable modules.
- *The 8 deleted helpers may be reachable by a spelling AST+grep misses.*
  Independently checked against `getattr`, pytest hook/fixture names, toml/yaml
  strings, doctests and entry points. Zero live references.

### Valid but Defer — real, not this slice

- `check_current_pointer_writes` cannot see a pointer name built from a variable
  stem (`stem = "latest"` then `f"{stem}.md"`). **The reported defect was one
  layer off**: widening the prefilter changes nothing, because the SCANNER has no
  constant propagation — measured, and the attempted fix was reverted rather than
  shipped as cosmetic.
- `reviewed_input_verification` does not recompute the digest of recorded
  components. Downgraded on inspection: the packet bytes are already pinned by
  `packet_sha256` and the identity lives inside the packet, so components are
  pinned transitively. Defense-in-depth, not an exploitable hole.
- Making the dead-code advisory blocking or non-opt-in.
- The four restatements of the "git failed ≠ empty answer" error contract across
  the gates — real duplication, but consolidating changes pinned message text.
