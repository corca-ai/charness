# Quality runner barrier removal and runtime relevel
Date: 2026-07-26

## Decision Under Review

Making `./scripts/run-quality.sh` faster by two independent moves, plus the
runtime-budget relevel the first move forced:

1. Dropping the two `flush_phase` barriers that separated independent gates, and
   queueing `pytest` first, so the 44s critical-path gate overlaps the ~9s of
   validators it has no dependency on. This is the `active move` the
   [prior quality review](../quality/latest.md) ranked as the largest remaining
   speed lever.
2. Batching per-gate runtime samples into one recorder invocation per phase
   ([`--batch`](../../scripts/record_quality_runtime.py)) instead of one Python
   process per gate. Measured directly before the change: ~68ms per invocation
   x ~81 gates, all of it strictly serial inside `flush_phase`, and visible in a
   timestamped trace as a 5.0s gap between the first and last printed gate line
   of a phase.
3. Re-leveling nine per-gate runtime budgets in
   [`.agents/quality-adapter.yaml`](../../.agents/quality-adapter.yaml), because
   move 1 changed what a per-gate bar measures.

Measured result across three timed runs per state, same machine, same commit
base: `--read-only` 62.4 / 63.0 / 64.1s -> 50.8 / 53.8 / 53.8s. `--full` 62.7s ->
52.0s. `--read-only --release` 86.4s -> 60.1s.

## Failure Angles

- A gate that looked independent but actually depended on an earlier phase's side
  effect — the class the barrier layout was hiding.
- Batch-mode divergence: does one recorder call leave the state that N sequential
  calls would, including archive rotation, `updated_at`, and key order?
- Blast radius of a malformed batch line: one bad record now travels with ~80
  good ones.
- Whether the budget relevel produces bars that cannot fail — the exact
  anti-pattern the 2026-07-25 retune comments in the adapter were written to fix.
- Whether the mixed sample window (pre-change isolated samples aging out against
  post-change contended ones) plants a delayed false red.
- The unmeasured `local-linux-aarch64-4cpu` profile, which runs the same modified
  script on a quarter of the cores.

## Counterweight Pass

Two bounded reviewers, one per risk boundary. Both graded down as often as up and
both refuted something the parent believed.

The layout reviewer found the dependency the parent had checked for and missed.
`check-seed-fixture-budget` scans `$PYTEST_DEBUG_TEMPROOT/pytest-of-<user>` — the
same tree the `pytest` gate fills and then `rmtree`s — and its own failure mode is
fail-OPEN (`advisory_only_no_pytest_temp_yet`, exit 0). Run alongside pytest it
either measures a half-built tree or hits `du`'s vanishing-file error and silently
stops being a gate. The parent did not take this on the reviewer's word: polling
the gate every 4s during a standing pytest run returned `available scanned` nine
times and then `unavailable advisory_only_no_pytest_temp_yet` at the moment pytest
tore its basetemp down. Confirmed, then fixed by moving the gate behind the
pytest barrier.

It also refuted the parent's own comment. `run-quality.sh` claimed "the two
barriers that stay are the ones that carry a real dependency" — false as written,
since a third real dependency existed and the comment had just been used to
justify removing the barrier that enforced it.

The budget reviewer refuted the completeness of the relevel rather than its
arithmetic. It confirmed none of the nine raised bars crosses 2x median, and that
both tightened bars have ~45% headroom against a median-based rule so neither will
flake — but it found `check-coverage` left out of the hand-written relevel list,
sitting 259ms above an already-observed contended run. It also showed the parent's
`inventory-ubiquitous-language` raise was unsupported by any observation, and that
every cited max in the parent's comments was stale relative to the signals file the
comments claimed to derive from.

The parent's one measured refutation of its own hypothesis: a concurrency cap was
implemented, measured, and reverted. It did not reduce per-gate contention
(`check-markdown` 11.3s -> 10.2s), because the contention source is pytest's 16
xdist workers, not queue depth. Reverting it rather than keeping a plausible-looking
knob is the counterweight the parent owed itself.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: `check-seed-fixture-budget` scans the same temp root `pytest` builds and tears down, and fails OPEN on a scan error, so the barrier removal silently converted a gate into a no-op; reproduced by polling it during a live pytest run (`unavailable` the moment the basetemp was removed) and fixed by queueing it after the pytest barrier, where the tree is settled
- F2 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml | action: fix | note: `check-coverage` was omitted from the relevel and sat at 12000 against an already-observed contended 11741ms; because it is queued conditionally its sample window turns over slowly, so the false red would have landed weeks later on an unrelated change with the causal event long out of context — raised to 16500 with the same `(contended)` derivation as its siblings
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/record_quality_runtime.py | action: fix | note: the first malformed batch line aborted the whole batch while the runner truncated the file regardless, so one killed gate subshell would discard every gate's sample for that phase and leave `check-runtime-budget` grading a stale store as green; `--batch` now applies every valid record, reports each bad line on stderr, and still exits nonzero
- F4 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh | action: fix | note: the runner could itself emit the malformed line F3 describes — a gate subshell killed after its meta path exists but before it is written yields an empty `elapsed_ms` and `{"elapsed_ms":,...}`; the emitter now refuses a non-integer elapsed and warns instead of writing invalid JSON
- F5 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml | action: fix | note: `run-quality-read-only-release: 150000` had drifted above 2x its median (71319), so it could no longer trip the 2x regression its own comment promised — pre-existing, but this change made the release path faster still, and the whole justification for the relevel rests on that policy; retightened to 110000
- F6 | bin: act-before-ship | evidence: moderate | ref: .agents/quality-adapter.yaml | action: fix | note: the aarch64 profile is not merely unverified but a probable BLOCKING false red — its `check-secrets: 8000` sits below the 11639ms this 36-core box already observes contended, on a machine with a quarter of the cores; four bars are raised by the measured x86_64 contention factor and labelled `(contended, derived)`, chosen to fail open rather than block a maintainer whose box is fine, with re-measurement recorded as owed
- F7 | bin: act-before-ship | evidence: strong | ref: scripts/check_seed_fixture_budget.py | action: fix | note: a failed `du` scan and a genuinely absent temp tree both printed "no pytest tmp directory present yet", so the operator was told the gate had nothing to measure when in fact the measurement failed; the two are now distinct classifications and the scan-failure case prints a WARNING saying the run proves nothing
- F8 | bin: act-before-ship | evidence: moderate | ref: .agents/quality-adapter.yaml | action: fix | note: every `(contended)` comment cited a max the signals file already exceeded, so the stated "~1.4x contended max" derivation did not reproduce from its own source; recomputed from post-change samples only (n=13, cut 2026-07-25T15:34) and restated, since these comments are the only record of why the bars moved
- F9 | bin: bundle-anyway | evidence: strong | ref: .agents/quality-adapter.yaml | action: fix | note: the `inventory-ubiquitous-language` raise 1200 -> 2000 was justified as contention damage but no run, contended or not, ever came within 10% of the old bar; corrected to 1500 and the comment now says plainly that this one is headroom, not contention
- F10 | bin: bundle-anyway | evidence: strong | ref: scripts/record_quality_runtime.py | action: fix | note: `--batch` silently ignored a stray `--timestamp`, contradicting the sibling check that refuses `--label`/`--elapsed-ms`/`--status`, and `dict(empty_store)` aliased the caller's nested literals so hoisting those obviously-constant dicts to module constants would have leaked one run's commands into the next; both closed
- F11 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/support.py | action: fix | note: the seeded recorder stub still did an unconditional `args.index('--label')`, which raises on a `--batch` invocation; it survives today only because a `bin/python3` shim short-circuits it first, so it was a trap for the next test that bypasses the shim
- F12 | bin: over-worry | evidence: strong | ref: scripts/run-quality.sh | action: document | note: the parent's own hypothesis that queue depth caused the per-gate inflation was wrong — a 12-way concurrency cap was implemented and measured and moved `check-markdown` only 11.3s -> 10.2s, because pytest's xdist workers are the contention source; the cap was reverted rather than kept as a plausible-looking knob
- F13 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/standing_test_economics_lib.py | action: defer | note: `check-seed-fixture-budget` fails open on ANY scan error, which is defensible on a shared box but means a permanently broken `du` reads as a passing gate forever; ordering fixed the live instance, and turning fail-open into a bounded-retry-then-fail is a separate design decision recorded in the handoff
- F14 | bin: valid-but-defer | evidence: moderate | ref: .agents/quality-adapter.yaml | action: defer | note: per-gate wall-clock budgets now measure co-scheduling as much as gate cost, so they must be re-derived on any future parallelism or core-count change; recording per-gate CPU time would keep both the wall win and scheduler-independent teeth, and is the right fix rather than repeated hand relevels

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (the change alters the gate every push runs, and loosens nine enforcement bars).
- Requested spawn fields: none sent — per the repo's per-host subagent split, Claude Code hosts use the host's own typed-agent controls (`bounded-reviewer`) with session-model inheritance, and no host addressing `name` was passed.
- Host exposure state: host-defaulted
- Application state: both reviewers ran on the session-inherited model; no host tier-application signal exposed.
<!-- allowed Delivery state: findings-received | findings-recovered-from-transcript | spawn-accepted-no-delivery | pending-parent-spawn. Boundary cleanliness is a separate claim and does not imply delivery. -->
- Delivery state: findings-received — both reviewers returned findings inline.

## Fresh-Eye Satisfaction

`parent-delegated`. Two bounded reviewers spawned as `bounded-reviewer` with no
host addressing `name`, one per risk boundary (runner layout + batch equivalence;
budget relevel). Both self-reported the read-only envelope bound. Rail-1 boundary
snapshot taken before the spawns and verified `{"ok": true, "drift": []}` on
return, before any fix was applied — the parent made no edits while they ran, so
the drift set could not be its own work.

The parent verified the highest-priority finding independently (the polling
experiment above) rather than taking it on the reviewer's word, and rejected one
reviewer suggestion on measurement: the cap in F12.

Non-claim: neither reviewer had `git` access, so both read working-tree state
rather than a diff. The layout reviewer flagged that its statement about which
phase a gate *used to be* in is inferred from the change description and the
current file, not from `git show HEAD:scripts/run-quality.sh`. The parent, which
made the change, is the source of that ordering fact — same-agent evidence,
recorded as such.

Non-claim: the `local-linux-aarch64-4cpu` profile was not run. Its four raised
bars are derived from this machine's contention factor, not measured on that box.

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: `scripts/run-quality.sh` owns gate scheduling and what each timing sample measures; `scripts/record_quality_runtime.py` owns how samples are persisted.
- Consumer: `check_runtime_budget` and the `.agents/quality-adapter.yaml` bars that grade those samples, plus every gate whose measured cost is now co-scheduled.
- Owning surface: the runner for the ordering contract, the adapter for the bars, and the per-gate comment at each moved bar for the derivation.
- Verdict: owned-correctly — the scheduling change legitimately belongs to the runner, and the budget consequence was pushed to the adapter that owns bars rather than absorbed silently. The seam the change exposed (a gate whose correctness depends on scheduling, stated nowhere) is now stated at the gate's own queue line instead of living in a barrier's implicit meaning.
