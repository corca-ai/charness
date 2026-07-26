# session retro
Date: 2026-07-26

## Context

One session under the standing operator direction (bug fixes, friction/rework,
test/code speed) that closed the handoff's blocker 1 — two holes in the
runtime-profile affinity switch — and published `v2.11.0`. Three bounded
reviewers ran; two changed the design materially. The release-triggered
auto-retro (`2026-07-26-v2-11-0-release-auto-retro.md`) covers only the release
helper's own trigger surface, so the session's actual waste had no home. This
artifact is that home, written because the operator asked whether the waste was
recorded and it was not.

## Evidence Summary

- Shipped: 4 commits (`cfebe91f`, `f20ad861`, `6177632c`, `f2684757`), release
  `2.11.0` verified via HTTPS 200 plus installed readback `version: 2.11.0`.
- `./scripts/run-quality.sh --read-only` run 6 times at ~49-55s each (~5 min
  total wall); 82 gates green on the final run.
- `tests/quality_gates/test_runtime_budget_gate.py`: 33 tests before, 37 after.
- Both starting violations were reproduced before their fixes:
  `usable_cpu_count()` raised `PermissionError` under a patched
  `sched_getaffinity`; the budget gate exited 1 under real `taskset -c 0-3`.
- Reviewer boundary fingerprints: `{"ok": true, "drift": []}` on both snapshot
  pairs, each verified BEFORE applying any reviewer fix.

## Waste

**The design error is the expensive one.** A `run-quality-read-only: 270000`
aggregate was written for `local-linux-aarch64-4cpu`, justified in its own
comment as matching the precedent `run-quality-read-only-release` set. A reviewer
did the arithmetic the citation invited: `270000 / 130279 = 2.07x median`, above
the `bar < 2x median` rule — and that rule is written **100 lines above in the
same file**, as the reason that very precedent had been retightened one day
earlier. The citation was made without checking the cited thing. Cost: one
reviewer round-trip plus a full revert. This is the handoff's own "ask what the
measurement measured" trap, hit while editing the file that records it.

**Fighting a line-cap by hand.** `docs/handoff.md` exceeded its 70-line
validator, and it took six edit rounds to get under — one of which *added* a
line, moving away from the target. The validator prints the exact deficit
(`cut ~N lines`) every run; the deficit was never used to plan a single edit.

**Ignoring a hint the tool printed.** The critique artifact was hand-authored,
and `validate_critique_artifacts.py` rejected it three times in sequence
(`Fresh-eye satisfaction:`, then `## Boundary Ownership`), each round revealing
one more required section. Its very first failure message said: *"start from the
owning scaffold instead of hand-authoring — `scaffold_critique_artifact.py`."*
The scaffold ran on round four and emitted the complete required shape at once.

**Guessing CLI flags.** `reviewer_boundary_fingerprint.py` was invoked with
`--output`, then `--snapshot`, then `--in` before the actual `--out` / `--before`.
Three failed calls; `--help` first would have cost one.

**Two smaller ones.** `export_plugin.py` was called before finding the correct
`sync_root_plugin_manifests.py`. And `pytest tests/quality_gates/` was launched
separately and hit a 2-minute timeout, duplicating work `run-quality.sh` already
does — the read-only run includes the `pytest` gate.

**Not waste, worth recording as such:** the 360-line cap firing mid-slice. It
named a real seam (proposing a bar vs deciding an exit code), which is exactly
what the handoff says a mid-slice gate block is.

## Critical Decisions

- Reverting the aarch64 aggregate rather than repricing it. No number is honest
  for a profile with zero recorded samples: too tight is a guaranteed blocking
  false red if the block's slowdown assumption holds, too loose is a bar that
  cannot fail if it does not. Leaving the hole open and making it one command
  wide beat shipping either.
- Splitting sizing from enforcement when the cap fired, instead of trimming lines
  to clear it. The cap was treated as a question about cohesion, not a budget.
- Scoping budget bars by observed cost on the profile rather than by parity with
  a sibling profile's label list — parity had left the largest gate on the
  machine (27.3s) unbudgeted on every profile.
- Fixing the reviewers' findings before publish rather than filing them, because
  release is an irreversible boundary and four of the six were one-line changes.

## Expert Counterfactuals

- **Richard Cook** ("failure is the absence of a defense that was assumed
  present") would have asked, before writing the aarch64 bar, which mechanism
  would catch it if wrong. The honest answer was *none* — every label on that
  profile reports `no-sample` until the box runs, and `BUDGET_SLACK_FACTOR` is
  3.0, so a 2.0x bar is invisible to the one advisory built to find bars that
  cannot fail. That question alone kills the bar before a reviewer sees it.
- Direct counterfactual on the mechanical waste: reading a tool's own remediation
  text before the second attempt would have removed three of the four rework
  loops (scaffold hint, `cut ~N lines`, `--help`). Nothing about these needed
  judgment; they needed reading the output already on screen.

## Sibling Search

- axis: other bars in `.agents/quality-adapter.yaml` citing a precedent without
  restating its ratio | decision: valid follow-up outside the slice | proof: the
  x86_64 `run-quality-read-only-release` comment states its ratio explicitly and
  survives the check; the aarch64 per-gate floors state a derivation but no
  ratio against any median | follow-up: deferred docs/handoff.md `## Next
  Session` item 1
- axis: other artifact validators with a scaffold script that hand-authoring
  skips (`retro`, `handoff`, `quality`, `debug`) | decision: valid follow-up
  outside the slice | proof: `scaffold_retro_artifact.py` exists and was used for
  THIS artifact on the first attempt, costing zero validator rounds versus the
  critique artifact's three | follow-up: no repo change needed; the behavior
  change is the `## Next Improvements` workflow entry below

## Next Improvements

- workflow: when an artifact has an owning `scaffold_*.py`, run it before writing
  a line. Two artifacts this session, hand-authored: 3 validator rounds. One
  scaffolded: 0. The validator prints the scaffold command in its first failure.
- workflow: when a comment cites a precedent's rule, recompute the rule against
  the new number in the same edit. The citation is the claim; the arithmetic is
  the evidence, and this session shipped the citation without the evidence.
- capability: the standing direction's third clause — **test/code speed** — went
  unaddressed. Budget bars are regression *detection*, not speed; nothing this
  session made a gate or a test faster. Recorded as a handoff item so the gap is
  a tracked choice rather than a silent omission.
- memory: a counted limit (line caps, size budgets) is a planning input, not a
  retry loop. Read the reported deficit and make one edit.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-26-session-retro.md
