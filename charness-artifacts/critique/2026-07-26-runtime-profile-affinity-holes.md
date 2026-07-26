# Runtime profile: closing two affinity holes without shipping a bar that cannot fail
Date: 2026-07-26
Fresh-eye satisfaction: parent-delegated

## Decision Under Review

The two open holes the handoff named as blocker 1, plus the friction that created
the second one:

1. [runtime_profile_lib.py](../../skills/public/quality/scripts/runtime_profile_lib.py)
   caught only `AttributeError` around `sched_getaffinity`, so a host whose kernel
   *refuses* the query crashed every gate that derives a profile — where the
   `os.cpu_count()` call it replaced could not fail at all.
2. `local-linux-x86_64-4cpu` had recorded samples and no budgets block, which is
   the one combination the gate treats as a hard configuration error. `taskset -c
   0-3 ./scripts/run-quality.sh --read-only` exited 1 on this box for reasons that
   had nothing to do with runtime.
3. The only fix for (2) was ~18 bars hand-read out of `runtime-signals.json` —
   the same transcription step that shipped eight aarch64 bars *below*
   already-observed runs. So the gate now derives the block: `--suggest-budgets`.

Both violations were reproduced before either fix: `usable_cpu_count()` raised
`PermissionError` under a patched `sched_getaffinity`, and the budget gate printed
`not configured in runtime_budget_profiles` and returned 1 under the real
`taskset -c 0-3`. Post-change both return cleanly, the latter proven under
`taskset` rather than under a simulated profile id.

## Failure Angles

Two bounded read-only reviewers, spawned per the repo delegation contract, on
disjoint scopes:

- **Correctness / seam design** — completeness of the widened `except`, the ceil
  arithmetic in the new sizing function, import direction after the 360-line
  split, every one of the 18 new bars against the recorded samples, plugin mirror
  fidelity, and whether the new tests can actually fail.
- **Policy / north-star fit** — whether each new bar earns its teeth, whether the
  label scope is an honest decision or an unstated gap, whether an advisory
  suggestion can escape into a committed bar that cannot fail, and whether the
  change creates a new way to mistake a measurement for a verdict.

Parent-side worktree+index integrity was fingerprinted around both reviews
(`reviewer_boundary_fingerprint.py` snapshot/verify): `{"ok": true, "drift": []}`,
verified before any fix was applied.

## What The Reviews Changed

**The aarch64 aggregate was reverted, not shipped.** The draft added
`run-quality-read-only: 270000` to `local-linux-aarch64-4cpu`, justified as "2x
the measured 4-core wall, the same precedent `run-quality-read-only-release`
set". The reviewer did the arithmetic the citation invited: that precedent's
operative rule, written 100 lines above in the same file, is `bar < 2x MEDIAN`,
and `270000 / 130279 = 2.07x median`. **The bar could not trip the 2x regression
its own comment promised** — the exact anti-pattern the surrounding block exists
to prevent, with the precedent's name attached to it. Two further disanalogies:
the precedent was sized from the profile it enforces, this one from a *different*
profile's samples; and the two failure directions are mutually exclusive — if the
block's slowdown assumption is wrong the bar cannot fail, and if it holds strongly
the bar cannot pass, which is a guaranteed blocking pre-push false red. Nothing
would have caught it: every label on that profile reports `no-sample` until the box
runs, and `BUDGET_SLACK_FACTOR` is 3.0, so a 2.0x bar is invisible to the one
advisory built to find bars that cannot fail.

No single number is honest for a profile with **zero recorded samples**. The hole
stays open, but it is now one command wide — `--suggest-budgets` emits the whole
block from that machine's own samples on first run — and the comment records the
failed attempt so the next reader does not re-derive it.

**"Sizing lives in one place" was false when written.** Only the *constant* moved
in the split. `budget_slack_findings` still computed `int(worst * HEADROOM)`
unrounded, so for this repo's own `check-coverage` the advisory said "consider
10969ms" while `--suggest-budgets` said `11000` for the identical sample — on the
one path an operator is instructed to act on. The advisory now calls
`suggested_bar_ms`, and the tests pin `11000` as a **literal**: they previously
restated production's own expression, which passes for any headroom value and is
precisely why the divergence was invisible.

**The error-message pointer named the wrong profile.** `--suggest-budgets` alone
re-derives the profile from the *machine*, so an operator investigating
`--runtime-profile local-linux-aarch64-4cpu` on the 36-core box would paste the
suggested command, get a block sized from 36-CPU samples, and commit it under the
aarch64 heading — bars 3-6x too tight, the exact false-red class the message
exists to end. The message now interpolates the profile it just rejected, and the
test asserts the full string rather than the flag name.

**Label scope was stated as one criterion and applied as another.** The draft
said "cost centers" and applied sibling-profile parity. Parity left
`check-export-safe-imports` — 27.3s, the largest unbudgeted gate on this machine —
with no bar on *any* profile, while spending bars on 600ms inventory gates. The
aggregate does not backstop that, and the file itself supplies the reason: since
the barrier removal `pytest` at 130.8s essentially *is* the 134.8s wall, so a
standing gate could go 27s → 110s, finish inside `pytest`, and move no bar. Scope
is now by observed cost: 13 labels added on the 4-core profile, and the three
largest unbudgeted gates on the 36-core profile the maintainer actually runs
(windows n=20, entirely post-barrier-removal). `check-duplicates` and
`dead-code-advisory` stayed unbudgeted with the reason recorded — their windows
hold no post-barrier-removal samples, so a bar would be sized from a regime this
profile no longer runs in.

**Provenance: one of the "three measurement runs" was red.** The middle run
failed (`pytest` 126440ms status `fail`, and therefore the aggregate at 130279ms).
The bars are still arithmetically as claimed — they derive from `max_recent`,
passing in both cases — but the comment presented the window as three clean
measurements. A failing run can exit early and read fast. The caveat is now in the
block.

**A test that proved nothing.** The single-sample `latest` fallback in
`suggested_bar_ms` was uncovered: deleting it left every test green while the
docstring's promise silently stopped holding, dropping one-sample labels out of
the emitted block entirely. The fixture now carries a `specdown` label with one
sample and no window.

**Two new measurement-as-verdict paths, both closed.** The header said "Derived
from 84 recorded label(s)" — that is *breadth* reading as *depth*, and a fresh
runner would paste 84 enforcing bars each sized from one sample with no
provenance anywhere. Each line now carries `n=` and worst-observed, with `n<3`
listed separately as thin evidence. Separately, sizing silently falls back to a
declared `command_timing_log`, and such a log with no `profile` field matches
*every* profile — so the header now names the source, not just the profile id.

Also from the reviews: the unreachable `max(..., ROUNDING)` clamp is gone (it was
a guaranteed surviving mutant), `evaluate` reads through its own public
`load_signals` so the one-path claim holds by construction rather than by
inspection, and `--suggest-budgets` now rejects `--json/--summary/--detail`
instead of handing commented YAML to a caller that parses JSON.

## Counterweight Pass

Not everything the reviewers raised was worth acting on:

- **Silent fallback when affinity is refused.** Real: a container that limits CPUs
  *and* blocks the syscall files its slow samples into the unrestricted profile
  again. But fail-open is the right call for profile detection, the case requires
  a seccomp policy blocking a read-only query, and threading a warning channel
  through a pure two-line function costs more than the exotic case is worth. Left
  as-is, deliberately.
- **`OverflowError` on an absurd JSON integer**, and a JSON `true` yielding a
  500ms bar. Both require a hand-corrupted machine-written file. Not defended.
- **Two module instances of the sizing lib** under the skill loader. Same file, so
  the values agree; only a future runtime monkeypatch would notice. Noted, not
  restructured.
- **Asymmetric injection** (`load_signals` injected while `evaluate_timing_log` is
  imported). Correct observation, but the asymmetry buys the one thing that
  matters — no second `SIGNALS_PATH` constant — and collapsing it either way
  creates an import cycle or a duplicate path.
- The aarch64 block keeps `check-coverage: 60000` while the new 4-core block
  refuses to invent it from the same fact. Real inconsistency, pre-existing, and
  resolving it means touching floors this slice deliberately did not re-derive.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml aarch64 block | action: fix | note: drafted 270000 aggregate is 2.07x median, above the 2x its own cited precedent requires; reverted to a recorded hole
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py budget_slack_findings | action: fix | note: advisory derived its own bar (10969) diverging from --suggest-budgets (11000) on the path operators act on
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/runtime_profile_lib.py profile_budgets | action: fix | note: error pointer omitted --runtime-profile, so a paste re-derives from the machine and files wrong-hardware bars
- F4 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml 4cpu block | action: fix | note: sibling-parity scope left the largest gate on the machine unbudgeted; aggregate cannot backstop it when pytest is the critical path
- F5 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_runtime_budget_gate.py | action: fix | note: single-sample latest fallback untested (deletable while green); slack expectations restated production's own expression
- F6 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/scripts/runtime_budget_sizing_lib.py format_budget_suggestion | action: fix | note: label count read as evidence depth, and timing-log provenance was unstated; both now in the header
- F7 | bin: bundle-anyway | evidence: strong | ref: .agents/quality-adapter.yaml 4cpu window comment | action: document | note: the middle of the three "measurement" runs was red; caveat recorded
- F8 | bin: over-worry | evidence: moderate | ref: skills/public/quality/scripts/runtime_profile_lib.py usable_cpu_count | action: defer | note: silent fallback re-enables profile contamination under a seccomp policy blocking a read-only query; fail-open is still correct
- F9 | bin: over-worry | evidence: weak | ref: skills/public/quality/scripts/runtime_budget_sizing_lib.py suggested_bar_ms | action: defer | note: OverflowError / JSON-true inputs require a hand-corrupted machine-written file
- F10 | bin: valid-but-defer | evidence: moderate | ref: .agents/quality-adapter.yaml aarch64 check-coverage | action: defer | follow-up: deferred docs/handoff.md `## Next Session` item 1 | note: aarch64 keeps check-coverage: 60000 while the new block refuses to invent it from the same fact

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` typed read-only subagent, two disjoint scopes.
- Requested spawn fields: `subagent_type: bounded-reviewer`, per-scope prompt, session-model inheritance (per the Claude-host branch of the per-host subagent contract; no Codex model/effort request applies here).
- Host exposure state: applied
- Application state: host-confirmed: both reviewers reported `envelope-unbound`/`envelope bound` with only Read/Grep/Glob visible and no Bash/Edit/Write/Agent, and each independently noted it could not execute tests or gates.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded read-only reviewers ran in the shared parent
worktree; `reviewer_boundary_fingerprint.py` snapshot/verify returned
`{"ok": true, "drift": []}` and was run BEFORE any fix was applied, so neither
review's boundary proof is contaminated by the parent's own edits.

## Reviewed Input Identity

<!-- No prepared packet was consumed: reviewers were pointed at the uncommitted worktree diff directly, with the changed-file list enumerated in each prompt. -->

## Boundary Ownership

- Producer: the standing-gate runner, which records per-label elapsed samples into `.charness/quality/runtime-signals.json` under a machine-derived profile id.
- Consumer: `check_runtime_budget.py`, which reads committed bars from the quality adapter and turns an exceeded median into a non-zero exit.
- Owning surface: the quality skill's runtime-budget surface (`skills/public/quality/scripts/` plus the repo's `.agents/quality-adapter.yaml` bars), with the profile id as the writer/reader contract.
- Verdict: owned-correctly

## Non-Claims

- **The aarch64 profile is still unmeasured.** Its per-gate bars remain
  x86_64-derived floors and it still has no aggregate bar. Nothing here changed
  that; the change is that the hole is recorded with its failed fix and is now one
  command wide.
- **The 4-core window is n=3 with one red run in it.** These bars absorb variance
  by construction (1.4x worst), but they are not a characterized window the way the
  36-core profile's n=20 bars are.
- **`--suggest-budgets` output is unproven as *good* bars.** It is proven to be
  derivable, paste-parseable, depth-annotated, and refusal-on-no-samples. Whether
  1.4x-of-worst is the right policy for a given repo is the operator's judgment,
  which is why the mode never edits an adapter. It exits 0 on a derived block and
  **1** when the profile has no samples — the release critique caught this paragraph
  claiming "exits 0" flatly, which is the checked-in-text class the previous
  release's own central finding came from.
- **The mutation strength of the new tests is not measured.** They are proven to
  fail against the pre-fix code for the two reproduced violations; the sizing
  module has not been through a mutation run.

## Next Move

Committed with the slice. The named residual is the aarch64 profile's first real
run, which now replaces its whole block in one command instead of being
hand-derived a second time.
