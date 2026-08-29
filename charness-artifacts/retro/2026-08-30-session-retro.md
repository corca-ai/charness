# Session Retro

Date: 2026-08-30

## Context

Picked up the 2026-08-29 next-session plan. Step 0 (main red for consumers) and
Step 1 (`#759`, a removal slice being undeclarable) closed. The operator then
asked why the `#759` sibling pattern surfaced only by accident and directed a
full sweep, which found eight more instances and turned into seven review rounds.

This retro exists because the session's most transferable finding is not any of
the repairs. It is that I produced defects of the class I was repairing, at a
rate of roughly one per repair, and caught none of them myself.

## Evidence Summary

- Main green: Quality Core success on `029b2c6e6`, `eda0622b5`, `67555154e`
  after failing on `030aa8262`. Measured on three fresh clones: 94 failed / 16
  errors without the plugin mirror, 8468 passed with it.
- `charness-artifacts/quality/2026-08-29-plugins-mirror-absent-in-ci.md` — Step 0.
- `charness-artifacts/quality/2026-08-30-declaration-intersection-sweep.md` —
  the class, its four root causes, the deliberate non-repair.
- `charness-artifacts/release-review/2026-08-30-8.0.0-real-host-removal-surface-lock.md`
  — Step 2's inventory and the honest ledger.
- Seven `code-critique` / `release-safety` rounds, every one `block`, every
  finding reproduced before repair. Filed `#760`, `#761`, `#762`.
- Final: standing 8491 passed, broad gate 79 passed / 0 failed, pushed
  `030aa8262..dc77742f2`.

## Waste

- **Symptom repair instead of class repair.** I fixed `#759` as "deletions in
  committed-ref mode" without characterizing the class. Naming it first makes the
  opening move obvious — diff the git invocations of every path-enumerating
  function — and that one move would have produced three of the eight findings
  immediately. The repo's Sibling Search discipline exists for exactly this and I
  skipped it. Cost: the entire sweep was rework that a five-minute discipline
  would have front-loaded.
- **Ten defects of the repaired class, introduced by the repairs.** Too-broad
  symlink exclusion; an unqualified contract claim; an import-time alias; two of
  four symlink-policy owners reconciled; `.resolve()` renaming a declared
  pointer; gitlink field-order; index-vs-checkout; superproject walk-up; consumer
  module substitution; import-order dependence. Each cost a review round.
- **Three tests that shared a premise with the defect they guarded.** The
  submodule test asserted `captured` and never that the digest tracked the
  commit, so it passed over the constant `0`. The next one asserted the digest
  matched the INDEX entry — the very thing that was wrong. The symlink test
  asserted the exclusion that was itself the defect. Writing a test is not
  evidence; writing one that fails against the wrong answer is.
- NOT waste: the seven review rounds. Every round produced a reproduced defect.
  Rounds 5–7 were narrower but still real, and round 7 found a superproject
  HEAD being bound as a submodule's.

## Critical Decisions

- **Regeneration over re-tracking for `plugins/`.** The producer reconstitutes
  1,045 files from a bare clone in one call, and `6e05e026e`'s cost case (11 MB,
  37% of commits as churn) stands. CI provisions it; nothing reverts.
- **Binding the current pointer rather than excluding it.** My first cut dropped
  it from the sweep; `auto_excluded_paths` is never digested, so a retarget could
  not stale a verdict. Binding also makes the `latest.md` basename proxy safe to
  be imprecise — a misclassified path is bound, not dropped.
- **Not fixing the exec bit.** Folding mode into the ref-mode per-path hash would
  stale EVERY ref identity ever captured to fix a field the patch hash already
  covers. Recorded with reasoning rather than left as an unknown.
- **Stating the symlink substrate split instead of forcing uniformity.** A
  committed blob is immutable; a live link can move. The contract says so now.
- **Stopping at seven rounds.** Rounds 5–7 were each my own previous repair.
  Charness has no submodules, so the remaining precision has zero live impact
  here; it went to `#761` instead of an eighth round.

## North Star Alignment

Purpose is reducing rework in CONSUMING repos, and three findings were the same
consumer-facing shape: green on this machine, broken elsewhere. The plugin mirror
(local `charness init` hid it), `core.quotepath` (this machine's gitconfig sets
`false`, git's default is `true`), and the retro test that passed only on the day
it was written. P-channel discipline held where it mattered — every finding was
reproduced by RUNNING, and the two hand re-reproductions of sweep results were
the right instinct given zero refutations across ten agents.

Where it did not hold: I repeatedly treated my own reading as a check. The
`--all` vacuous-binding defect and the two dead plugin detectors were both found
by running with/without, never by reading.

## Expert Counterfactuals

- **Gary Klein (premortem):** "assume this repair is subtly wrong — where?" asked
  once per repair would have caught the class-reproduction. The answer was
  available every time: *who else answers this question?* Four owners answered
  the symlink question and I reconciled two; two halves answered the merge
  question and I aligned one. A premortem naming the OWNER SET, not the code
  path, is the cheap discriminator.
- **Engelbart (system-improving-itself):** the tooling improved (T) while my
  process did not (H). Seven rounds of the same correction produced seven
  repairs and zero transfer — I did not get better at self-detection, I only
  accumulated memory of two specific traps, which is why the third by-path module
  was guarded up front and nothing else was. The durable move is a gate, which is
  why `#760` exists.

## Trends vs Last Retro

Against `2026-08-29-session-retro.md`: its "run the disconfirming probe FIRST at
integration" lesson RECURRED in a new costume — I ran probes, but wrote three of
them to confirm what my code did rather than to discriminate against the wrong
answer. Its `--scope` glob trap also recurred exactly: I removed a CLI flag and
checked two call sites, and the gate found a third.

## Sibling Search

Transferable pattern: two components answer one question and drift, or two
correct rules intersect to refuse a legitimate input.

- same layer: other reviewed-input consumers (`critique_packet_lib`,
  `reviewer_worker_*`) | decision: diagnostic-only | proof: the sweep's
  narrative-vs-binding lens covered them; findings were in the two enumerators.
- abstraction up: any repo-wide "what changed" consumer — `classify_push_diff_lib`,
  `prepush_close_keyword_scan`, `publish_release_resume_closeout` | decision:
  fix now, not done | proof: all three run their own `diff`/`diff-tree` with
  distinct flags and none passes `-z`; filed as `#760`.
- specialization down: submodule states | decision: same waste, deferred with
  evidence | proof: `#761`.
- mental-model siblings: gates that pass over an absent subject — the two plugin
  detectors this session re-armed | decision: fixed | proof: bucket 13 → 11,
  both now `refused`.

## Next Improvements

- workflow — **name the OWNER SET before repairing.** "Who else answers this
  question?" is the discriminator that would have prevented most of the ten
  self-inflicted defects. Destination: this artifact; the triggering instances
  are the four symlink owners and the two merge halves.
- workflow — **a test must fail against the wrong answer, not pass against the
  implementation.** Three tests here shared a premise with their defect.
  Destination: this artifact; assert the negative explicitly, as the gitlink test
  now does with `!= sha256("gitlink\0" + "0")`.
- capability — **an enumerator-agreement gate.** The only durable fix for the
  drift; hand-alignment is what decayed. Destination: `#760`.
- memory — reviewer rounds are NOT optional on this path. Seven rounds, seven
  blocks, seven reproduced defects, zero self-caught.

## Packet Consumed

n/a (no adapter sections consumed for this retro)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-30-session-retro.md
