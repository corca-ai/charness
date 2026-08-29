# The detector set nobody audited

Date: 2026-08-29

## Context

The session opened on `2026-08-31-next-session-plan.md`: release 8.0.0 first,
then convert enumerated refusals to properties. It shipped no release. The
operator redirected twice — first to "use Rust where Rust wins; lower CPU, go
faster", then to full autonomy — and the session ended having closed a class of
gate blind spots instead.

That trade was right, but it was not the plan, and the plan's Step 1 is still
open. This retro is about how the session found the class, and about the two
long stretches it spent on premises that measurement then inverted.

## Evidence Summary

- Ratio cap: `source_lines: 144799`, `test_lines: 144800`, passing only on
  `round(ratio, 4)`. Restored to `--advisory` at `scripts/run-quality.sh:1171`
  and pinned by `test_ratio_gate_stays_advisory_in_the_runner`. History:
  `2026-06-19-gate-buy-vs-build-triage.md:36-38` ranked the hard cap the repo's
  strongest DROP; `2026-07-08-issue-420-resolution-critique.md:28` warned nothing
  pinned the flag; `issue-753/lane-A-ratio-surface-brief.md:37` said the posture
  was a later #753 decision; `4122f6cd0` promoted it to blocking the next day.
- Changed-line coverage: 115 lines across 11 files, all covered.
  `release_changed_line_coverage.py` moved `blocked` -> `partial`.
- `native/repograph/parity/run_parity.py` imported `scripts.check_export_safe_imports`,
  deleted by #748 slice 1. The harness that licenses an ownership switch could not
  execute. Repaired; `match-surfaces` parity is `difference_count: 0`.
- `#748` slice 2 measured, not assumed: Python `load_surfaces` + `match_surfaces`
  3.01 ms in-process against 4.31 ms for the native subprocess. `path_matches_patterns`
  survives either way — `boundary_probe_lib.py:112` is a live consumer the plan
  did not record.
- `repo_file_listing.iter_repo_files` 89.2 ms = git 27.1 + `Path` construction and
  sort 24.9 + `is_file()` 13.0 + decode/rebuild. A strings-first Python variant
  measured 53.9 ms; the dominant cost is API shape, not language.
- Test seed carried `native/repograph/target` whole: 1.4 GB of a 1.6 GB fixture,
  of which 3.8 MB is the binary. Seed 1.7 G -> 114 M, per-test clone 1.23s -> 0.28s.
- `test_gate_summary_names_failures.py` cloned the checkout and git-committed
  inside it to prove what `run-quality.sh` prints: setup 7.3s -> 0.04s after
  moving to `make_quality_runner_repo`, which the sibling
  `test_quality_runner_release_order.py` had used all along.
- `check_test_repo_copy_invariants.py` enumerated 3 fixture names and 2 helper
  names, matched only inside `test_` bodies. Made transitive over module-local
  functions; 7 hidden standing tests surfaced immediately in
  `test_standalone_imports.py`.
- Rust: 11,891 lines, files to 1,340 tokei code lines against a 480 Python cap,
  zero gates. `scripts/run-quality.sh` itself is 1,331 lines and
  `check_python_lengths.py` globs `*.py` only. First crate coverage measurement:
  78.46% of 8,010 lines.
- `plugins/`: 1,042 files, 934 of the last 2,498 commits (37%). Moving the tree
  away entirely and re-running the sync regenerated all 1,042 files
  byte-identically.
- Suite across the session: 8,418 / 77.2s -> 8,414 / 73.7s, green.

## Waste

- **Two long stretches built on an unmeasured quantity.** First: the plan's
  "reduce the release machinery for ratio headroom" rests on arithmetic that runs
  the other way — removing production lines RAISES `test/source`. Second: after
  the operator asked for Rust, I framed "Rust transition is the test-speed fix"
  and had to retract it, because native `match-surfaces` is 1.4x SLOWER and
  `repo_file_listing`'s dominant cost is `Path` construction, not Python. Both
  premises were one measurement away. I wrote plans first and measured second.
- **I optimised the fixture before asking whether the test needed it.** I found
  the 1.4 GB seed and made the copy 15x cheaper; the operator had to ask "이 테스트
  자체 jtbd가 뭐지? 너무 과한데?" before I questioned the clone at all. Then the
  answer was a 180x setup win and no repository. This is
  `2026-05-20-quality-treadmill-vs-root-cause.md` exactly — bounding a cost before
  asking the root-cause question — and that retro is in the served digest.
- **I proposed installing `nose` without checking whether it was installed.** It
  was, at 0.20.0, `doctor_status: ok`. I read a static checklist as a work item and
  asked the operator for consent to a step that was already discharged.
- **Message changes chased across pinning tests one file at a time.** Renaming the
  length gate's output to stop lying about `.rs` files broke pins in
  `test_empty_scope_refusals.py` and `test_python_length_gates.py`, found serially
  by re-running. A grep for the literal before editing would have made it one step.
- **Repeated `sleep`-and-poll background jobs** after the harness had already said
  a completing job notifies. Several turns bought nothing.

## Critical Decisions

- ✓ **Restored the ratio cap to advisory instead of deleting release safety
  machinery to fit under it.** A ten-subsystem JTBD audit found no defensible cut;
  the single `oversized` verdict was refuted with live consumers the assessor
  missed. Method caveat, recorded because it weakens the result: the refutation
  pass ran only against cut proposals, so the nine `earns-its-lines` verdicts are
  NOT adversarially verified.
- ✓ **Did NOT take #748 slice 2 after measuring it.** The plan called for it. It
  is slower, adds subprocess plumbing to seven call sites including the pre-commit
  gate, and leaves the matcher duplicated. Reporting that instead of executing the
  plan was the session's best single call.
- ✓ **Made the copy-heavy detector transitive rather than adding the found file to
  `STANDING_COPY_HEAVY_TESTS`.** The exemption ledger was the inviting move — it
  even has a measured-cost contract. Repairing the detector found 7 more.
- ✓ **Untracked `plugins/` only after proving regeneration byte-identically.**
  The premise ("the producer is complete") was checkable in one command and would
  have been catastrophic if wrong.
- ⚠ **Deleted `check_staged_mirror_drift.py` and dropped `--validate-export` from
  `validate_packaging_committed.py`.** Defensible — the boundary each guarded
  ceased to exist — but this is the closest the session came to the P5 failure
  signature, and it deserves a fresh-eye read next session.

## North Star Alignment

**P3 (principle over rulebook) is the spine of the session.** Every finding is
the same shape: an enumeration standing in for a property.
`check_test_repo_copy_invariants` listed five identifiers instead of asking
"can this test reach a copy-heavy source"; one local-fixture hop hid the most
expensive copy-heavy test in the standing lane from the gate built for it.
`check_python_lengths` globbed `*.py` instead of asking "is this executable
source this repo ships"; 1,331 shell lines and 11,891 Rust lines sat outside it
while the ratio gate counted them as production.

**P5 (teeth only for irreversibility and form) was being violated by the ratio
cap.** A whole-repo LOC ratio is a reversible smell, and its own `--advisory`
docstring says a hard cap "pressures AGAINST writing tests as the ratio
approaches it". Restoring the advisory posture and adding a pin that forces the
question is P5 applied, not a cap raised.

**Failure signature nearly walked into: "you cited fewer lines / fewer gates as
success".** 1,042 files untracked and two gates deleted is not the win. The win
is that `check_doc_links`'s uniqueness rule can fire again: every script basename
had existed twice, so the rule had never fired, and untracking the mirror
surfaced 34 real findings across 10 documents. Count is not the metric in either
direction.

**P4 held at the one irreversible boundary the session touched.** The release was
not pushed. Its gates were cleared, but a cleared gate is not a release, and the
session recorded that rather than treating `partial` as done.

## Expert Counterfactuals

- **Douglas Engelbart — treat (H + LAM + T) as one unit; design T alongside LAM.**
  Triggered: the slice changed gates, skill surfaces, and the quality contract.
  The session improved individual tools — a detector here, a length gate there —
  and the real finding is one level up: this repo requires every detector to state
  its own blind class in its docstring, and nothing asks that question of the
  detector SET. Six blind spots were found by accident, in the course of other
  work, not by any process. Engelbart's counterfactual is not "add a meta-gate"
  (that is the treadmill); it is that the C-level activity — improving the
  improving — needs a standing artifact of its own. The next session should
  produce a detector inventory that records, per gate, what it can NOT see, and
  then read the inventory for gaps. That artifact is the deliverable; whether any
  gate follows is a later question.
- **Gary Klein — pre-mortem the premise, not the plan.** Both wasted stretches
  share a shape: a plan whose entire value rested on a quantity nobody had
  measured. "Reducing the release machinery buys ratio headroom" and "the Rust
  transition is the speed fix" are each refuted by a single command. The discipline
  is narrow and cheap: when a plan's value depends on a number, measure the number
  BEFORE writing the plan. Klein's question — "it is a month later and this was a
  waste; why?" — answers instantly for both: because the direction of the
  arithmetic was never checked.

## Sibling Search

- axis: fixture proliferation | location: `tests/quality_gates/support.py`
  (`make_quality_runner_repo`), `tests/quality_gates/test_shell_gate_root_resolution.py:67`
  (`_charness_shaped_repo`), `tests/repo_copy.py` (`clone_seeded_charness_repo`) |
  decision: valid follow-up outside the slice | proof: the fixture sweep found
  `test_python_and_security_gates.py`'s three markdown tests could use
  `_charness_shaped_repo` — a THIRD hand-built repo fixture; the refuting agent
  built it and confirmed all three pass | follow-up: deferred
  fixture-factory-consolidation-handoff
- axis: gate output pinned as a string literal | location:
  `tests/quality_gates/test_empty_scope_refusals.py`,
  `tests/quality_gates/test_python_length_gates.py` | decision: valid follow-up
  outside the slice | proof: one honesty fix to a gate message was chased across
  two test files serially | follow-up: deferred gate-message-pinning-handoff
- axis: Rust has no coverage floor while Python changed lines must be covered |
  location: `scripts/release_changed_line_coverage.py` vs `native/repograph` |
  decision: valid follow-up outside the slice | proof: `cargo llvm-cov` installed,
  baseline 78.46% recorded; a whole-repo percentage is deliberately NOT the answer |
  follow-up: deferred rust-changed-line-floor-handoff
- axis: `scripts/check_python_lengths.py` measures Rust and its name says otherwise |
  location: 73 references | decision: valid follow-up outside the slice | proof:
  measured with grep before choosing to extend in place | follow-up: deferred
  length-gate-rename-handoff

## Next Improvements

- workflow: **when a plan's value rests on a quantity, measure the quantity before
  writing the plan.** Both wasted stretches this session were one command from
  being avoided. Concretely: any proposal containing "this will be faster /
  smaller / cheaper" must carry the measurement in the same message that proposes
  it, not in the message after the operator asks.
- capability: **audit the detector SET, not each detector.** Produce a standing
  inventory recording, per gate, what it cannot see — enumerations it stands on,
  file types it globs, indirection that defeats it. Six blind spots were found by
  accident this session; the repo already demands each detector state its blind
  class individually, which is exactly why the gap is at the set level.
- memory: **a number in prose beside a number in a test is two sources for one
  fact, and only the test goes red.** `.agents/command-dominance.yaml` said 14/8
  while the test pinning it asserted 15/9 — the comment had drifted a full
  measurement behind the thing that pins it. Where both must exist, the prose must
  say "read the test for the truth".

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-29-detector-blind-class.md
