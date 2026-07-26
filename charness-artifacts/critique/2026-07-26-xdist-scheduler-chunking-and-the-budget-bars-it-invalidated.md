# xdist scheduler chunking and the budget bars it invalidated
Date: 2026-07-26

## Decision Under Review

Add `--maxschedchunk 1` to the standing pytest command (`choose_sched_chunk` in
`scripts/run_standing_pytest.py`) so `--dist load` stops pre-assigning each worker a
contiguous block of tests before any timing feedback, and re-derive the four
`local-linux-x86_64-36cpu` runtime bars the resulting speedup invalidated.

## Failure Angles

- **Semantics, not just speed.** Finer scattering breaks same-worker locality. If any
  session/module fixture carried state across tests that previously landed together,
  the win would be bought with flakes that surface later, on someone else's push.
- **The version floor is a claim about the world.** A floor guessed rather than checked
  is worse than no floor: it converts "slower suite" into "pytest exits 4 before
  collecting", which is the one outcome this repo's own `usable_cpu_count` docstring
  forbids for a tuning knob.
- **A speedup silently loosens every bar sized against the old regime.** The handoff
  records this exact trap twice (`check-coverage` drifted to 6-10x; an aarch64 bar
  shipped at 2.07x median while citing a rule forbidding it). Making the gate 41%
  faster and leaving `pytest: 73000` would have re-created it in one commit.
- **Sizing basis vs enforcement basis.** A retune is naturally sized from the
  post-change slice, but `runtime_budget_lib._checked_entry` enforces against the
  full-window median. During a regime change those disagree, so a bar can read correct
  in every comment and still be a few percent from a blocking red.
- **Comment arithmetic drifting from the samples it cites.** Each gate run mutates the
  window the comments quote, so numbers written mid-session go stale in place.

## Counterweight Pass

- The flakiness angle was probed and came back empty, and that is a real answer, not an
  absence of effort: the seed cache is a source-hash-keyed *filesystem* cache shared
  across workers with a wait-forever `filelock`, the one direct `os.environ` mutation
  runs in a `multiprocessing` spawn child, and the historical shared-index race already
  has a live AST guard. Five repeat runs plus two release-inclusive runs plus two
  4-core runs produced zero failures. Not a blocker.
- Reworking `seeded_quality_runner_repo` (module-scoped, `tmp_path_factory`-backed, now
  rebuilt per worker instead of once or twice) is a genuine follow-up but not a
  blocker: the measured 45.5s -> 26.9s is already net of that duplicated setup.
- The `run-quality-read-only-release` bar is under the 1.4x-worst no-flake arm, but its
  window max is a pre-barrier-removal run from six days earlier. Inventing a number
  from a regime that no longer exists would be worse than stating the gap. Documented,
  not "fixed".
- Raising `pytest-release` against this block's usual tightening direction is not a
  regression in discipline: 87000 was 1.16x its own worst observed run, which is the
  flake failure mode rather than the loose-bar one.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/run_standing_pytest.py:24 | action: fix | note: version floor was guessed at 2.3; `--maxschedchunk` first shipped in xdist 3.2.0 (changelog #855), and `packaging/mutation-requirements.txt` pins `>=3,<4`, so 3.0/3.1 are reachable and would have exited 4. Corrected to (3, 2) and verified against the upstream changelog.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_standing_pytest_runner.py:216 | action: fix | note: the PYTEST_ADDOPTS deference test asserted only the suppressing case, so widening the guard to `if env.get("PYTEST_ADDOPTS")` still passed — a mutant that silently reverts the whole optimization on any host with addopts set. Discrimination assertion added.
- F3 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml:210 | action: fix | note: first-pass bars were sized from the post-change slice while enforcement reads the full-window median, leaving `run-quality-read-only` at 1.02x and `run-quality-full` at 1.03x of the blocking basis. Windows were turned over to convergence before the numbers were set.
- F4 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_standing_pytest_runner.py:174 | action: fix | note: the serial fallback path had no assertion that `--maxschedchunk` is absent, so the exit-4 outcome the whole guard exists to prevent was untested. Added.
- F5 | bin: act-before-ship | evidence: strong | ref: .agents/quality-adapter.yaml:226 | action: fix | note: pre-existing false arithmetic on an untouched neighbour — "110000 stays above 1.4x the worst sample (86353)" when 1.4*86353 = 120894. Claim corrected in place; number deliberately left alone and the missing re-derive stated.
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/run_standing_pytest.py:180 | action: fix | note: the docstring described the initial batch as round-robin `len(collection)//4`; upstream sends CONSECUTIVE chunks of `len(collection)//nworkers//4`, which is the actual reason one worker got every slow test (they are adjacent in collection order). Verified against installed xdist source and corrected.
- F7 | bin: act-before-ship | evidence: moderate | ref: scripts/run_standing_pytest.py:216 | action: fix | note: the fixture-locality paragraph claimed nothing was given up; `seeded_quality_runner_repo` (~80 consumers, module-scoped, not seed-cache-backed) is now rebuilt per worker. Claim narrowed to what is true and the follow-up named.
- F8 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/support.py:472 | action: defer | note: seed-cache-backing `seeded_quality_runner_repo` is the next speed win on this path; the current change is already net positive without it.
- F9 | bin: valid-but-defer | evidence: moderate | ref: scripts/run_standing_pytest.py:235 | action: document | note: the deference covers `PYTEST_ADDOPTS` only; an ini `addopts` tuning is still silently overridden. No effect on this repo (`pyproject.toml` sets no `addopts`); scoped in the comment for downstream consumers.
- F10 | bin: over-worry | evidence: moderate | ref: charness-artifacts/critique/2026-07-26-xdist-scheduler-chunking-and-the-budget-bars-it-invalidated.md | action: defer | note: `CHARNESS_PYTEST_SCHED_CHUNK=off` restores the slow regime and would trip the retuned `pytest` bar. Real coupling, but "off" is a debugging escape hatch, not a supported steady state, and the 58500 bar now has enough headroom that a single off-run is the operator's own signal.
- F11 | bin: over-worry | evidence: weak | ref: scripts/run_standing_pytest.py:237 | action: defer | note: substring false positives on `"--maxschedchunk" in PYTEST_ADDOPTS` (e.g. inside a `-k` expression) — no non-contrived case constructible.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (repo-typed read-only fresh-eye reviewer, Read/Grep/Glob only), two independent scopes — scheduler correctness and budget-bar honesty.
- Requested spawn fields: `subagent_type: bounded-reviewer`, per-scope prompt, session-model inheritance per the Claude Code host branch of the per-host subagent contract.
- Host exposure state: applied
- Application state: host-confirmed: both spawns accepted and returned findings; `reviewer_boundary_fingerprint.py verify` reported `{"ok": true, "drift": []}` against the pre-review snapshot, so neither reviewer mutated worktree or index.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

`parent-delegated`

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

- Producer: `scripts/run_standing_pytest.py` — sole owner of the standing pytest argv, including worker width and now scheduling granularity.
- Consumer: `scripts/run-quality.sh` (labels the run and records timings) and `check_runtime_budget.py` (enforces bars against those timings).
- Owning surface: the standing-pytest runner for the flag; `.agents/quality-adapter.yaml` for the bars the flag's speedup invalidated.
- Verdict: owned-correctly
