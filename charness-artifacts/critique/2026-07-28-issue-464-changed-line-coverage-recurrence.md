# Issue #464 resolution: covering the changed lines the eighth mutation regression named
Date: 2026-07-28

## Decision Under Review

Resolving corca-ai/charness#464 "Mutation test regression on main" with a TESTS-ONLY diff
that covers the 15 changed lines the blocking changed-line signal reports as uncovered over
`d0172d3b..HEAD`, and closing the issue on the strength of a post-push CI verdict rather
than on the commit's own auto-close.

#464's FAIL is not a score failure: the run's mutation score PASSES (88.8% vs an 80% break).
The FAIL is entirely the blocking signal "changed lines were left test-uncovered before
mutation". The class is recurrent — `.github/workflows/quality-core.yml` names
#219 -> #251 -> #260 -> #320 -> #321 -> #335 -> #453, and this is the eighth.

## Failure Angles

- **Fixing the symptom set, not the class.** The 15 lines are what one run reported. The
  causal locus of eight recurrences is one layer up: the only lane that runs BEFORE a
  landing is non-blocking by construction (`scripts/run-quality.sh:587` passes
  `--skip-if-no-coverage`), and the only blocking lane runs AFTER the push and cannot
  unland it.
- **Solving the adjacent problem.** #464's reported blocking set was computed over
  `4d9858d5..d0172d3b`. The scheduled run's base is the previous COMPLETED run's head
  (`.github/workflows/mutation-tests.yml`), so that range is never re-analyzed. A diff that
  covers a different range can be credited for a green it did not cause.
- **A green produced by emptiness.** With local main unpushed, the next scheduled run would
  compute base `d0172d3b` and head `d0172d3b` — an empty diff whose changed-line arm is
  vacuously clean. The repo has already recorded this trap
  (`scripts/mutation_sample_manifest_score_lib.py:20-23`).
- **Closing before the evidence exists.** `Closes #464` in a direct-commit carrier fires the
  auto-close the instant the push lands, which is BEFORE the CI job whose verdict the close
  is supposed to rest on.
- **Tests that pass for the wrong reason.** Two of the eleven new tests inject failure by
  monkeypatch; an injection that removes the thing under test would leave the guard pinned
  by nothing.

## Counterweight Pass

- The monkeypatch in `test_repo_root_targets_skips_a_target_whose_path_cannot_be_resolved`
  was PROBED rather than argued: on this platform a symlink loop raises `RuntimeError` (which
  `except OSError` would not catch), a 6000-character component resolves fine, and a NUL byte
  raises `ValueError`. No reachable `OSError` input exists here, so the name-scoped patch plus
  the discriminating control (the empty target is still caught) is the correct evidence shape,
  not a shortcut.
- The conjunctive-FAIL objection — that score, `scope_gap`, sample-manifest, pending/timeout
  and the StrykerJS arm can each redden a run independently — is granted and then set aside:
  #464's FAIL came solely from the changed-line arm, and the other arms only bite if the
  closeout claims "FAIL cannot recur". The claim is scoped instead.
- Three extra assertions in the new `tests/test_markdown_sections.py` beyond its one target
  line are the cheapest possible scope creep: tests-only, reversible, no production surface.
  Blocking on them would be aesthetics.
- The freshness-fingerprint gap (C6) is real but its failure direction for THIS slice is
  self-announcing: coverage produced before the new tests existed shows the 15 lines still
  UNCOVERED, so stale reuse yields a loud false FAIL, not a false pass. Deferred, not folded.

## Structured Findings

- C8 | bin: act-before-ship | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py:64 | action: fix | note: a direct-commit `Closes #464` auto-closes at push, before the push-mirror job returns the verdict the close rests on, and `verify-closeout --expect-state CLOSED` reads issue state only — so a RED mirror still leaves a fully green closeout over a closed issue nobody reopens. Close keywords dropped from the carrier; the close is a separate manual step taken after the mirror verdict, naming that run.
- C3 | bin: act-before-ship | evidence: strong | ref: .github/workflows/mutation-tests.yml:141 | action: document | note: #464's own reported 47 targets were resolved by the unpushed commit `0807b62f`, not by this diff, and their range is never re-analyzed. The closeout says exactly that instead of implying this diff cleared what the open comment listed.
- C1 | bin: bundle-anyway | evidence: strong | ref: scripts/run-quality.sh:587 | action: document | note: this resolution is instance-only. The class fix (a pre-landing lane that BLOCKS rather than warns) is a separate slice with its own cost decision, recorded as a sibling decision rather than implied by a tests-only diff.
- C7 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_changed_line_mutation_coverage.py:180 | action: fix | note: the verification re-run collects fresh coverage rather than reusing it, which is correct here because reuse would validate nothing about tests that did not exist when the JSON was written; `--write-fresh-marker` is passed so the JSON and its sibling `.fingerprint` come from the same invocation.
- C9 | bin: bundle-anyway | evidence: moderate | ref: .github/workflows/quality-core.yml:144 | action: document | note: the push-mirror job runs the SAME script as the local reproducer, sharing `classify_changed_line_scope_gap` and the coverage probe. It is a distinct OBSERVER (clean checkout, different base, different environment) but not a distinct PROBE; the closeout says "distinct observer, shared probe" rather than claiming an independent channel.
- C10 | bin: bundle-anyway | evidence: moderate | ref: .gitignore:7 | action: document | note: `reports/` is gitignored and overwritten by the next run, so the verification payload exists only on stdout. The `blocking: []` / `resolved_head_sha` payload is pasted into this artifact's Executed Proof section before the push.
- C6 | bin: valid-but-defer | evidence: strong | ref: scripts/mutation_changed_files_lib.py:245 | action: defer | follow-up: deferred docs/deferred-decisions.md | note: the coverage freshness fingerprint digests only mutation-POOL files, and `tests/` is not in the pool, so a tests-only slice moves the marker by zero bits and a coverage JSON predating the new tests is still accepted as FRESH. The dangerous direction (tests deleted, marker still matching) is a gate design defect; gate redesign is out of scope here.
- C2 | bin: over-worry | evidence: weak | ref: tests/quality_gates/test_check_test_completeness.py:130 | action: defer | note: demanding a reachable `OSError` input for the `Path.resolve` guard chases fidelity the platform cannot supply; the probe above found no such input.
- C4 | bin: over-worry | evidence: weak | ref: scripts/check_mutation_score.py:168 | action: defer | note: the FAIL verdict is conjunctive over several arms, but #464's FAIL came solely from the changed-line arm, and seed rotation / score margin is the mutation workflow, explicitly out of scope for this resolution.
- C5 | bin: over-worry | evidence: weak | ref: tests/test_markdown_sections.py:23 | action: defer | note: three assertions beyond the one target line in a new test file for a previously-untested shared parser; fully reversible, no production surface, no consumer.

## Executed Proof

`reports/` is gitignored and each run overwrites the last, so the verification payload is
copied here rather than left on a terminal nobody will read again (finding C10).

Before the repair, over `d0172d3b..HEAD` (full probe, no reuse): **exit 1**, `ok: false`,
9 blocking files, 15 `blocking_targets` —
`scripts/check_test_completeness.py:80,81`, `scripts/critique_enforcement_scope.py:223`,
`scripts/markdown_sections.py:175`, `scripts/refresh_current_pointer.py:212,213`,
`scripts/validate_critique_artifacts.py:239`,
`skills/public/gather/scripts/write_record.py:69`,
`skills/public/handoff/scripts/draft_goal_from_chunk.py:187`,
`skills/public/quality/scripts/draft_dup_ratchet_triage.py:286,287`,
`skills/public/quality/scripts/seed_dup_review.py:91,92,117,166`.

After the repair, same range, coverage produced by
`run_slice_closeout.py --verification-lock --produce-mutation-coverage` in the same run
that consumed it (`check_changed_line_mutation_coverage.py ... --reuse-coverage
--require-fresh-coverage`): **exit 0**, and the payload is a real verdict rather than a
skip — `ok: true`, `blocking: []`, no `reason`, no `coverage_not_verified` key,
31 `changed_pool_files` analyzed, `resolved_head_sha: 594f2bfde21938d86741bde7dc5695f220d4d5d4`.
The skip-vs-clean distinction is checked explicitly because a skip also exits 0.

Per-target coverage was additionally measured through the gate's own mechanism
(`mutation_sampling_lib.run_test_coverage` + `load_covered_lines`) across the nine touched
test files: all 15 target lines present in the covered set, 152 tests passing.

## Post-Push Outcome (the close did NOT happen)

Finding C8 changed the plan before the push: the carrier carries `Refs #464`, not
`Closes #464`, so nothing auto-closed. That decision paid for itself immediately.

**Push 1 (`c5886080`, run 30352089354): the mirror went RED** — and not on the changed-line
signal. The coverage probe's own pytest run died, taking the verdict with it
(`subprocess.CalledProcessError` out of `_ensure_coverage`). Four tests in
`tests/quality_gates/test_dup_review_seed.py` fail wherever `nose` is absent, and no CI
workflow installs it. They inject `--code-inventory` and leave the doc arm to the real
producer, which degrades to `status=missing`; commit `53e883a8` — the slice that taught
these readers to refuse a verdict over a scan that never ran — turns that degrade into a
refusal the tests read as a crash. The class reproduced inside its own fix, one surface
over, invisible to that author's green local run because this machine has `nose` on PATH.
Repaired in `5ad503d8` by injecting both inventories; verified in both arms (29 passed with
`nose`, 29 passed with it hidden, where 4 failed before). Sibling scope closed empirically
rather than by grep: the CI run at `c5886080` IS the `nose`-absent environment, and the 21
other nose-referencing test modules passed in it.

**Push 2 (`5ad503d8`, run 30354134484): the mirror went GREEN, and the green is VACUOUS.**
Its payload reads `"reason": "no eligible mutation-pool files changed in this range"` with
`base_sha: c5886080` — the push-arm base is `github.event.before`, so this run analyzed only
the test-file commit and rendered no changed-line verdict over `d0172d3b..5ad503d8` at all.
It proves the probe no longer crashes. It proves nothing about the 15 repaired lines.
Reading the colour instead of the `reason` here would have produced exactly the trap the
repo already recorded at `scripts/mutation_sample_manifest_score_lib.py:20-23` — an
empty-diff green closing an auto-filed issue without re-proof.

**#464 therefore stays OPEN.** The only channel that can render a non-vacuous verdict over
the repaired range is the SCHEDULED mutation run, whose base is the previous completed run's
head (`d0172d3b`) and whose head will be `5ad503d8`. `workflow_dispatch` cannot substitute:
it computes no `base_sha`, so its changed-line classifier is inert by construction
(`.github/workflows/mutation-tests.yml`). The next scheduled run either comments a fresh
failure or posts a recovery candidate; a distinct observer closes #464 on the latter.

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: agent type `bounded-reviewer` (read-only Read/Grep/Glob), no host addressing name, session model inherited per the Claude Code host branch of the per-host subagent contract.
- Host exposure state: host-defaulted
- Application state: host resolved the typed read-only agent and inherited the session model; no per-subagent model/effort control was requested on this host.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated — four bounded reviewers: one causal-review reviewer before design (root
cause / detection gap / sibling search with the workflow-boundary invariant overlay), then
three critique angles (Weinberg diagnostic, Jackson problem framing, Gawande operational)
and one separate counterweight pass. All findings arrived in-band; none was recovered from a
transcript. The reviewer boundary was snapshotted before each spawn and verified at each
return across four windows (`i464-causal-review`, `i464-critique-angles`,
`i464-critique-angles-2`, `i464-critique-angles-3`, `i464-critique-counterweight`); every
verify returned exit 0 with `verdict: clean` and an empty drift list, with nothing declared.

A SECOND round ran anyway, and it earned its cost. The trigger was not the verdict-logic
rule — this slice edits no proof surface — but the currency floor in
`validate_critique_artifacts`, which refused the artifact once the CI-driven repair landed
after round 1: declared reviewed inputs had gone stale, which is the floor saying the
repairs are unreviewed. Round 2 re-read the REPAIRED file whole (not the repair hunks) and
asked the one question: does this fix reproduce the class it fixes?

It partly did, and the instance was the parent's own round-1 test.
`test_main_refusal_still_emits_the_payload_under_json` injected `--code-inventory` and left
the DOC arm to the real `nose`-backed producer — the same shape that had just broken four
sibling tests. It did not go red only because a refusal is what that test wants: on a
`nose`-less runner the doc arm supplies its own unestablished reason, so three of its four
assertions passed whether or not the code-arm branch worked. A falsifier settled it rather
than argument: with the doc arm made to fail instead, the old `any("cannot read")`
assertion still PASSED, proving it could not tell the two arms apart. The repaired test now
injects both arms and asserts the refusal names the code path specifically; the same
falsifier now fails it. Round 2 also cleared the four CI-driven repairs themselves (Q1/Q2:
the declared-empty doc inventory is the right declaration, and the invalid-overlay test no
longer rides on its exit code alone).

Per the two-round cap, the round-2 repair is recorded as accepted-unreviewed rather than
triggering a third round.

The causal reviewer's own strongest claim was FALSIFIED by the parent rather than accepted:
it named "the CI mirror is PR-only, so it fires post-landing" as root cause #2, and the
parent found the push arm live since `69941efb`, 67 commits before `origin/main`, and then
found in the CI run records that it FIRED and went RED on all three relevant pushes
(runs 30269197950, 30314842348, 30317036462). The gate was never missing; it was unread.

## Public Skill Validation Decision

No public skill surface changes in this slice. The diff is tests only; the `quality`,
`gather`, `handoff`, and `critique` skills' routing/prompt contracts, references, and
dogfood acceptance evidence are all UNCHANGED. `docs/public-skill-dogfood.json` therefore
stays frozen as-is and still validates, and no evaluator scenario is implicated.

## Reviewed Input Identity

Round 1 read nine changed test files; round 2 re-read the one the CI failure repaired.
The binding below is round 2's, because it is the one current against the tree.

- Packet consumed: charness-artifacts/critique/2026-07-28-i464-round2-packet.json
- Packet path: charness-artifacts/critique/2026-07-28-i464-round2-packet.json
- Packet SHA256: 1fb2539b71b28e7a4bd174e1dddb70896a96c826c43569487a6b2f1544203e64
- Identity SHA256: 8a6b303bea06f0e1b205d06584d443882368c980686a8787770d6db42424ffc8

Round 1's packet was `charness-artifacts/critique/2026-07-28-102134-packet.json`
(SHA256 `94991572436b8c82d69a2f89b0ed691f1c3c2677c8e11c8bf61894508573a453`, identity
`984bbc0efad998f297c052af61b6b57adf78406faee9b14bd36a9a0181ea341b`) over the nine changed
test files. It is recorded rather than declared current: the repairs after it landed, which
is exactly what the currency floor refused when this artifact still claimed it.

## Boundary Ownership

- Producer: the scheduled mutation runner's changed-line classifier, which emits the
  blocking signal, and the CI bot that transports it onto this issue.
- Consumer: the human reading #464, who decides whether the signal is resolved.
- Owning surface: the changed-line gate (`scripts/check_changed_line_mutation_coverage.py`
  and its workflow wiring), not any of the nine test files this slice touches.
- Verdict: single-surface
