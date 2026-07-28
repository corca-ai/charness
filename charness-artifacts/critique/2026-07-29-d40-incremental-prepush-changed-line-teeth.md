# D40: arming an incremental blocking pre-push changed-line lane
Date: 2026-07-29

## Decision Under Review

Replacing the pre-push changed-line lane's non-blocking skip with an INCREMENTAL
blocking producer, and repairing the mapper that decides which tests it runs.

D40's premise came from the #464 resolution, where two common explanations were
falsified. The gate was not missing: the push-arm CI mirror has been live since
`69941efb` and went RED on all three pushes preceding #464's last comment
(runs 30269197950, 30314842348, 30317036462). The warning was not quiet:
`_surface_skip` already writes a `WARNING (changed-line mutation gate):` line that
`run-quality.sh::print_phase_output` surfaces. What was missing is teeth before the
landing — the lane that could stop a push exited 0 by construction, and the lane with
teeth ran after it, where it cannot unland. A ninth warning was therefore rejected on
its face: the eighth was read and walked past.

The owner chose an incremental local producer over branch protection (direct pushes to
main stay) and over the broad ~10-minute producer (the cost that got the lane defused),
with policy (a) for files the mapper cannot resolve: name them, do not block on them.

## Failure Angles

- **The fix reproduces the class it fixes.** This lane's whole subject is "exit 0 was
  read as proof". A new lane that reports exit 0 when it judged nothing rebuilds the
  defect at the surface that reports the lane's own verdict.
- **A false block is how a gate gets disabled.** The predecessor was defused because it
  was expensive. A replacement that stops pushes over its own mapping gaps buys the
  same outcome by another route, and the escape hatch (`--no-verify`) is one flag away.
- **Focused coverage is not full coverage.** Anything that treats a subset measurement
  as if it spanned the repo will report covered lines as uncovered — or, if the
  measured tree differs from the analyzed tree, the reverse.
- **A performance guard on a correctness path.** The mapper's prefilter exists to keep
  the lane fast; a text it wrongly drops is a file silently unmapped.
- **Label reuse.** The lane kept its `check-changed-line-mutation-coverage` label while
  becoming a different program, so every surface keyed on that label now means
  something else without saying so.

## Counterweight Pass

- The safety direction was checked rather than asserted: focused coverage is a SUBSET
  of full coverage, so subsetting can over-report an uncovered line and never
  under-report one. That argument covers test-subsetting ONLY, and round 1 found the
  case it does not cover (a dirty tree, where line numbers skew between the measured
  and analyzed trees and a false PASS becomes possible). The argument was not stretched
  to cover it; the case was made `unestablished` instead.
- Policy (a) was NOT quietly widened into "unproven never blocks". Round 2's repair
  distinguishes `unproven` (the mapper resolved no standing test — the owner's
  deliberate non-blocking choice) from `unestablished` (the lane failed to judge what
  it was asked to judge). Only the second is refusable, and only at push time.
- The stem-as-call-argument regex over-matches (it will match
  `parser.add_argument("quality")`). Left as-is: the direction is safe — an extra test
  in the focused set can only ADD measured coverage — and an arbitrary "distinctive
  stem" heuristic would trade a costed miss for an uncosted one. Recorded as an
  accepted residual with a runtime tell rather than tightened on speculation.
- Measurement replaced estimation throughout: mapper 6.5s, focused producer ~24s for a
  realistic single-commit slice and ~5min for a whole nine-commit session, against
  11-15min broad. Before the mapper repair the lane false-blocked 3 of 26 analyzed
  files; after it, the same range returns `blocking: []`, matching full-suite ground
  truth.

## Structured Findings

- R1-F1 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_focused_changed_line_coverage.py:223 | action: fix | note: status was derived from the consumer's EXIT CODE alone, so "the limit intersected to nothing, this run proves nothing" and "dirty pool, judged a tree I could not see" both rendered as `clean`. Repaired with `_verdict_from_consumer`, which reads the payload; the consumer's honest reason was otherwise only in a stdout JSON blob carrying no `WARNING` head, which `print_phase_output` does not surface on a passing gate.
- R1-F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:582 | action: fix | note: `--allow-dirty` was inherited from the ADVISORY lane, whose rationale was that the verdict was advisory anyway. It now feeds a blocking verdict, and the focused coverage is produced by running pytest against the LIVE worktree while the mapping is computed against HEAD — line numbers skew, so an executed worktree line can be attributed to a different HEAD statement. That is a false PASS and outside the subset-of-full-coverage argument. A dirty pool is now `unestablished`, never `clean`.
- R1-F3 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/support.py:231 | action: fix | note: the seeded-harness stub list still named the old script, so three `test_quality_runner.py` tests failed. Reproduced (3 failed / 32 passed) before repair, green after.
- R1-F4 | bin: act-before-ship | evidence: strong | ref: scripts/mutation_coverage_producer.py:139 | action: fix | note: the lane wrote SUBSET coverage to the canonical `reports/mutation/test-coverage.json` and stamped a VALID freshness marker, so every `--require-fresh-coverage` consumer — the CI mirror included — would read freshness as breadth. Default moved to `reports/mutation/prepush-focused-coverage.json`.
- R1-F5 | bin: bundle-anyway | evidence: moderate | ref: docs/conventions/implementation-discipline.md:31 | action: document | note: two docs described the lane as reusing the closeout fingerprint. Updated, together with `.agents/quality-adapter.yaml`'s "active pre-push gate" note.
- R2-F1 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_focused_changed_line_coverage.py:224 | action: fix | note: round 1's repair only RELABELED the dirty case; it still exited 0, so a single uncommitted eligible pool file disarmed the whole lane — and `run-quality.sh` itself states a live dirty worktree is the normal condition, with verify running before commit. Exit 0 plus prose is precisely what the predecessor did. Repaired with `--refuse-unestablished`, passed by `run-quality.sh` only in read-only mode (the pre-push hook's mode): mid-work stays non-blocking, push time refuses.
- R2-F2 | bin: act-before-ship | evidence: moderate | ref: scripts/run-quality.sh:569 | action: fix | note: R1-F5 updated the external docs and MISSED the stale comment block in the lane's own file, which still described `--skip-if-no-coverage`, `--require-fresh-coverage` and the canonical coverage path — contradicting the invocation ten lines below it. Rewritten.
- R2-F3 | bin: bundle-anyway | evidence: moderate | ref: scripts/prepush_focused_changed_line_coverage.py:195 | action: fix | note: no post-produce existence check. With the coverage JSON absent, the consumer's `--reuse-coverage` falls through to the BROAD probe — an 11-15 minute silent stall inside a lane advertised at ~24s. Now refuses with `no-verdict`.
- R2-F4 | bin: bundle-anyway | evidence: strong | ref: scripts/prepush_focused_changed_line_coverage.py:299 | action: fix | note: a dead guard — the `"fell OUTSIDE" in reason` branch returned exactly what the following `if reason:` returned. Removed rather than kept: an allowlist-shaped guard that cannot change an outcome reads to the next maintainer as coverage.
- R2-F5 | bin: over-worry | evidence: weak | ref: scripts/suggest_mutation_coverage_command.py:80 | action: defer | note: the stem-as-call-argument regex matches any call with a matching string literal, so a short or common stem can inflate the focused set. Cost, not correctness, and the mitigation (a distinctive-stem heuristic) risks re-introducing silent unmapping. Accepted residual; the tell is lane runtime.
- R2-F6 | bin: over-worry | evidence: moderate | ref: scripts/prepush_focused_changed_line_coverage.py:152 | action: defer | note: five of seven outcomes exit 0. Three are owner-sanctioned or provably empty (`noop`, policy (a), `clean`); the two that established nothing now refuse at push time. The residual count is a property of a lane that must not false-block, not a defect.

## Executed Proof

- Mapper ground truth. The false block was not argued away, it was measured: coverage
  run over candidate test groups showed `tests/test_nose_inprocess_coverage.py` covers
  18/18 of the disputed changed lines in `nose_report_lib.py` and
  `nose_report_shape_lib.py`, while `test_quality_nose_advisory.py` — the file the
  mapper returned — covers 0. Post-repair the mapper returns the ground-truth test for
  both, unmapped files fall from 6 to 1, and the survivor is the brand-new script that
  genuinely had no test yet.
- End-to-end. Over `d0172d3b..HEAD` the armed lane returns `status: clean`, exit 0,
  33 analyzed files, `blocking: []` — matching the full-suite verdict for the same
  range. Before the mapper repair the same invocation returned `blocked` on 3 files.
- Performance. Mapper 6.5s (a prefilter regression had taken it past 5 minutes and was
  caught by measurement, not review). Focused producer ~24s single-commit, ~5min
  whole-session, against 11-15min broad.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent type `bounded-reviewer` (read-only Read/Grep/Glob), no host addressing name, session model inherited per the Claude Code host branch of the per-host subagent contract.
- Host exposure state: host-defaulted
- Application state: host resolved the typed read-only agent and inherited the session model; no per-subagent model/effort control was requested on this host.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — two bounded rounds, as this slice owes: it changes what a proof
surface DECIDES (a gate moved from advisory to blocking, a new blocking-set control on
the consumer, and a mapper whose output selects the evidence that gate judges on).
Round 1 read the armed lane and found five defects; round 2 read the REPAIRED surfaces
whole and found that round 1's headline repair had only relabeled the failure — the
lane still exited 0 where it mattered. All findings arrived in-band; none was recovered
from a transcript. Reviewer boundary snapshotted before each spawn and verified at each
return: `d40-round1` exit 0 `verdict: clean`, drift `[]`; `d40-round2` exit 3
`verdict: parent-attributed` with `parent_declared` covering
`scripts/prepush_focused_changed_line_coverage.py`, `scripts/run-quality.sh`,
`tests/quality_gates/test_prepush_focused_changed_line_coverage.py`,
`tests/quality_gates/support.py`, `docs/conventions/implementation-discipline.md` and
`.agents/quality-adapter.yaml` — the parent made every write in that window — and
undeclared drift `[]`.

Per the two-round cap, the round-2 repairs are recorded as accepted-unreviewed rather
than opening a third round. So is one refactor neither round saw: the round-2 repairs
pushed `check_changed_line_mutation_coverage.py` past the 480-line cap, and rather than
spill mechanically into an `_extra_lib` companion (D33) the run-trust cluster —
`_git_lines`, the uncommitted/contaminated-pool detectors, run-state pinning and drift,
and the two operator messages for the untrusted cases — moved to
`scripts/changed_line_run_trust.py` under one question it already answered:
is the tree this gate is about to judge the tree it measured? Behavior-preserving by
construction (names are re-exported so every existing caller and test keeps its
surface), and proven so by the suites that own those callers: 159 passing across the
changed-line, degradation-branch, producer, suggester, prepush and quality-runner
tests. The move DID break two things first, both caught by those tests rather than by
inspection: `_mark_untrusted` left behind a caller, and a monkeypatch aimed at the
gate's re-exported name no longer reached the real callee — the second repaired by
pointing the patch at the owning module, since patching a re-export would have left the
test green while exercising nothing.

Fresh-eye pass: scripts/prepush_focused_changed_line_coverage.py — round 2 read this
new proof surface whole against its own class (a verdict rendered over a scope never
established) and found the dirty-pool arm exiting 0, the missing post-produce existence
check, and a dead guard; all three repaired here.

Fresh-eye pass: scripts/suggest_mutation_coverage_command.py — round 2 verified that
every pattern `_reference_patterns` builds literally contains the prefilter substring,
so the performance guard cannot silently unmap a file, and judged the new stem
over-match as cost rather than correctness.

Fresh-eye pass: scripts/check_changed_line_mutation_coverage.py — round 1 walked
`_apply_file_limit` and confirmed an empty limit analyzes everything, an
intersect-to-nothing is distinguished from "nothing changed", and a limit naming an
unchanged path is intersected away rather than erroring.

## Public Skill Validation Decision

`skills/public/quality/references/attention-state-visibility.json` changed, but only to
DECLARE the new script's exit-zero attention state, which is what the gate that flagged
it requires. The `quality` skill's routing contract, prompt surface, references, and
adapter-facing behavior are unchanged, and no portable capability moved: the armed lane
is charness-host-local closeout wiring, and the portable
`changed_line_coverage_gate_lib` capability is untouched. `docs/public-skill-dogfood.json`
therefore stays frozen as-is and still validates. `quality` is `hitl-recommended`, so
this is recorded as an explicit decision rather than an evaluator scenario that must run.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-07-29-d40-round2-packet.json
- Packet path: charness-artifacts/critique/2026-07-29-d40-round2-packet.json
- Packet SHA256: 6a81b69cd5682591661bb4a7091a323733abe4cd6acd1dcbd2171becfc4a59aa
- Identity SHA256: bb1c4bb6f92e033fbfec916f5f35beab0c4ef62ac244693040ebfdbf77a84a9a

The binding above was re-rendered after the round-2 repairs landed, so it is current
against the tree; the round-2 reviewer read the surfaces as they stood at identity
`a7d32008bb91b120b9f529a5d2f8d7076644a65f1aa68f7bf750c102dd03aebf`, and its repairs are
the accepted-unreviewed remainder named above.

Round 1's packet was `charness-artifacts/critique/2026-07-29-d40-round1-packet.json`
(SHA256 `272e638a53fd9cab4076ec3e1c8894689577949ad5ec2a1f8e6cd68b8d1a9805`, identity
`f4770920b3ff8b3d9411476f0e6c0c6659102a9acf65b98d5941b2ef973a1274`). It is recorded
rather than declared current: its repairs landed after it, which is exactly what the
currency floor refuses.

## Boundary Ownership

- Producer: `suggest_mutation_coverage_command`, which decides WHICH standing tests are
  run as evidence, and the focused coverage producer that runs them.
- Consumer: `check_changed_line_mutation_coverage`, which renders the blocking verdict,
  and `run-quality.sh`, which turns that verdict into a push outcome.
- Owning surface: the orchestrator `prepush_focused_changed_line_coverage.py` owns the
  join — it is the one place that knows the coverage is a SUBSET and must therefore
  narrow the blocking set to match. Neither the mapper nor the consumer can hold that
  invariant alone: the mapper does not know a verdict is being rendered, and the
  consumer does not know its coverage was focused.
- Verdict: owned-correctly
