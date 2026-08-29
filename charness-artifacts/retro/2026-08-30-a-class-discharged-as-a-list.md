# A class discharged as a list

Date: 2026-08-30

## Mode

pattern analysis (operator-prompted, mid-session)

## Context

The operator, watching a session accumulate small failures, asked for patterns
and patterns-of-patterns rather than incident response, and for structural
repair regardless of who authored the defect. This records the analysis and the
one structural change made from it. It is not a session retro; the session's own
work is `charness-artifacts/spec/repograph-tool-control-plane.md`.

## The incidents

Eleven failures in one session, all found by RUNNING, none by reading:

| # | Failure | Found by |
| --- | --- | --- |
| 1 | Bare `pytest tests` instead of `run_standing_pytest.py`; 8400 tests, ~110s vs >30min | the clock |
| 2 | Three bounded-reviewer subagents went idle without delivering | waiting |
| 3 | Export mirror not resynced after later source edits; 11 test failures | the battery |
| 4 | `package_managers.cargo` would derive `cargo install repograph --force` against crates.io | a contract test, then reading the deriving function |
| 5 | `PYTEST_DEBUG_TEMPROOT` as a guard marker: already live in the authoring shell, exempting every bare run | printing the guard's inputs |
| 6 | `raise pytest.UsageError` in `pytest_collection_modifyitems` is absorbed; hook entered, raised, 5935 tests still collected | instrumenting the hook |
| 7 | `detect_binary_name` reported `binary_name: PATH=${CARGO_HOME:-$HOME/.cargo}/bin:$PATH` | running `charness tool doctor` |
| 8 | `cargo install --path <crate>` from elsewhere ignores `rust-toolchain.toml`; 1.93.0 in `/tmp`, 1.96.0 in the crate, crate needs 1.96 | running `cargo --version` in two directories |
| 9 | Backticked doc path where the gate requires a markdown link | the doc-links gate |
| 10 | Changed-line coverage reported `native_gate_lib.py` all-lines-missing; direct measurement says 89% | running `coverage report` |
| 11 | (the session's subject) A native-artifact refusal demanding a sidecar whose contents were discarded on the next line | one grep for the consumer |

## The pattern

Every one is the same shape: **a mechanism returned a verdict it had not
computed.** The guard "refused" while the run continued. The gate reported "0%
covered" for 89%-covered code. The manifest declared a safe install and derived
an unsafe one. The marker meant "the runner owns this session" and was true in
any shell descended from one. The refusal demanded a value nobody consumed.

The failure mode is invisible in every case: output, exit code, and green gates
are indistinguishable from the mechanism having worked.

## The pattern of patterns

The repo already knows this class, and knows it well. `test_empty_scope_refusals.py`
states the rule outright — *"a gate that compared nothing must say so, and must
not exit 0"* — and `test_a_declaration_is_not_its_own_corroboration.py` and
`test_a_refused_verdict_states_its_refusal.py` cite numbered sweep rows (S2, S9,
S10, S23). "silent pass" and "vacuous" appear with careful prose in a dozen
modules.

So the meta-pattern is not ignorance. It is this:

> **This repo repeatedly converts a CLASS of defect into a LIST of its known
> instances.** The list is then pinned by excellent tests, and the class goes on
> producing instances that nothing detects.

The same move, three times, at three scales:

- `2026-07-19-runner-reuse-retro.md` migrated every checked-in raw-pytest call
  site and verified with `rg` that none remained. A scan over files cannot see a
  command an agent types, so the largest caller was outside the audit **by
  construction** — incident #1.
- `2026-07-26-lesson-recurrence-mechanism.md` measured that lesson dedup keys on
  normalized SURFACE TEXT, so a re-worded instance resets recurrence to 1:
  1594 of 1596 candidates sit at multiplier 1.0. A class can never accumulate
  weight, only its spellings can.
- The native-core distribution layer proved *this* artifact matched *this*
  digest across 1,900 lines, and never that the producer and consumer agreed —
  which is exactly where it was broken the whole time.

Incidents #4, #5, #6, #7 are new instances of the already-swept class, authored
after the sweep, in files the sweep never had to consider.

## Why this is a north-star problem, not a hygiene problem

`charness` exists for *efficient, auditable* software work. Auditing by
enumeration is O(instances) and decays the moment the corpus changes; auditing
by property is O(1) and holds for the file nobody has written yet. Every time a
class is discharged as a list, the repo spends audit budget and buys decaying
evidence.

The sharper version: an enforcement layer with silent no-ops is **worse than no
enforcement**, because it consumes the audit budget and returns something that
reads as evidence. Every defect above passed all 80+ gates. The gates were green
while the thing they existed to prove was false.

## What changed

One list became a property:
`tests/quality_gates/test_a_manifest_field_is_not_what_the_control_plane_derives.py`.

It asserts, over **every** manifest in `integrations/tools/` rather than the two
observed broken, the values the control plane DERIVES rather than the fields
authored:

1. `detect_binary_name(manifest)` is a bare executable (pins #7).
2. A manifest installing from a local source path declares no `package_managers`,
   because the derivation is a registry install-by-name of a different artifact
   (pins #4).
3. Every declared package manager actually derives an update action, so a
   decorative block cannot imply an update path that does not exist.

Each property carries a **negative control** that reinjects the exact defect and
asserts the property fires, plus one clean manifest asserting it does not fire
spuriously. A gate nobody has watched fail is not known to be a gate — which is
incident #6 stated as a rule.

Two earlier repairs in this session were the same move at smaller scale:
`tests/conftest.py`'s bare-run guard (the runner rule moved from prose into the
channel that acts) and its regression file, which pins both the ambient-marker
defect (#5) and the absorbed-exception defect (#6).

## The finding that arrived while writing this

Regenerating `recent-lessons.md` to accommodate this artifact surfaced the
following, already in the active digest's Next-Time Checklist, sourced from
`2026-08-22-proof-cost-portability-cadence-retro.md` with **3 independent
sources**:

> **workflow — prefer a structural property over an enumerated refusal.** […]
> The repair that worked is structural and positional […] **I committed the
> enumerated form first.**

The lesson above was already written down, already ranked, already carrying
three sources. This artifact is its fourth or fifth independent observation. Per
`2026-07-26-lesson-recurrence-mechanism.md`, dedup keys on normalized surface
text, so this re-wording will open a NEW row at multiplier 1.0 instead of
incrementing that one — the class fragmenting across its spellings, which is the
same defect one level up.

And the reason it did not reach this session is mechanical, not attitudinal:

**`charness-artifacts/retro/recent-lessons.md` was referenced by no operating
document.** Not `AGENTS.md`, not `CLAUDE.md` (its symlink), not `.agents/*.md`,
not `docs/index.md`. Eight modules produce, validate, gate, rank, dedup, and
score it (`recent_lessons_lib.py`, `record_lesson_score.py`,
`retro_persistence_lib.py`, `validate_retro_artifact.py`,
`check_skill_cut_safety.py`, `check_artifact_surface_preflight.py`,
`retro_output_dir_lib.py`, `.agents/surfaces.json`) and **nothing put it in
front of a session.** The `SessionStart` routing trigger that could have was
retired.

`2026-07-26` concluded that "the prose channel does not change behavior at the
moment of action" — and the channel it kept writing to was one no session read.
`AGENTS.md` now routes to the digest as the first item under "Start here",
because a digest read after the work is a description of the mistake already
made.

## What is NOT fixed, and should be named rather than implied

- **Incident #10 is unresolved.** The changed-line coverage gate reported
  `scripts/native_gate_lib.py` as all-lines-missing while direct measurement
  gives 89%. The gate itself is well built — it distinguishes `no-verdict` from
  `blocked` and says so in comments — so the loss is upstream of its verdict and
  was not located. It is a blocking release gate whose number is currently not
  trustworthy in at least one direction.
- **`charness` maps to ~400 test files.** `build_recommendation` returns nearly
  the whole suite as the "focused" set for that one 6,081-line file, which is
  why the changed-line lane is a 289s hotspot and why 21 files come back
  blocked. Any "focused" or "changed-line" claim that touches the CLI degrades
  to "everything". That is a topology problem, not a gate problem.
- **In-process bounded-reviewer delegation did not work three times**, including
  once with the explicit model override `.agents/claude-host.md` requires. The
  plan had already recorded two prior occurrences. Three sessions of evidence
  and no mechanism.

## The rule worth keeping

> Discharging a class by repairing its known instances leaves the class intact.
> Ask what property the instances violate, and check that instead — over the
> whole corpus, with a negative control proving the check can fire.
