# Release 8.0.2 Critique

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Target: `code-critique.md`.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-31-131926-packet.json
- Packet path: charness-artifacts/critique/2026-08-31-131926-packet.json
- Packet SHA256: 8c6e1f3bc4e81ebbcb1ffe5db3f42345cd7a3d857e15cfc8d0576cf35e4cd1f0
- Identity SHA256: c7e4c0bbe1db3c6c23fb9f6931947f78502016b2f107324a084d94aeddf2dffb

Two bounded read-only reviewers ran in parallel with materially different
angles — Gerald Weinberg (diagnostic + producer/consumer boundary ownership) and
Michael Jackson (problem framing). Both delivered `block`-weight findings. The
counterweight pass below is parent-owned.

Recorded non-claim: a FIRST pair of reviewers completed their work but their
reports never reached the parent context (no transcript, no completion result).
They were re-run rather than reported as delivered, and nothing from that first
pair is cited here.

## Reviewer Tier Evidence

- requested tier: `high-leverage`
- requested spawn fields: typed `bounded-reviewer`, session-model inheritance
  (per-host contract; the adapter's `model` / `reasoning_effort` /
  `service_tier` / `fork_turns` fields are the Codex-host request and are not
  applied on this Claude host)
- host exposure state: `host-defaulted`
- application state: unverified-by-packet
- Delivery state: `findings-received`

Both reviewers of the delivering pair returned their findings into the parent
context, and this artifact cites them. The earlier pair is recorded separately as
`spawn-accepted-no-delivery <named agents completed and went idle; no completion
result and no transcript reached the parent>`; nothing from that pair is cited,
and it is not counted toward the two-reviewer substrate.

## Boundary Ownership

- Producer: `scripts/env_bypass.py` — owns `TRUE_VALUES` and
  `env_bypass_enabled(name)`, the fact "is this gate's env bypass switched on".
- Consumer: the three `check_staged_*` gates, `scripts/helper_provenance_lib.py`,
  and the root `charness` CLI as a consumer that cannot import the producer.
- Owning surface: `scripts/env_bypass.py`.
- Verdict: moved-to-owner

The reviewed change is precisely a producer/consumer ownership move. The
env-bypass truthiness predicate was a consumer-side restatement in four modules
with no producer; it now has one (`scripts/env_bypass.py`), and the consumers
call it instead of re-deriving it.

- Producer: `scripts/env_bypass.py` owns `TRUE_VALUES` and
  `env_bypass_enabled(name)`. The spelling table is pinned once, in
  `tests/quality_gates/test_env_bypass.py`.
- Consumers: the three `check_staged_*` gates and `helper_provenance_lib`. Each
  keeps its own env-var NAME and its own CLI-flag disjunction, because those are
  genuinely per-consumer; only the truthiness rule moved.
- Boundary that cannot be crossed: the root `charness` CLI. It is a consumer that
  structurally cannot import the producer, so it is bound by a test that drives
  both implementations rather than by a duplicated constant plus a comment.

The same question applied to `tests/script_closure.py` gives `owned-correctly`:
it is new shared test infrastructure with one producer and three consumers, and
the review's finding against it was under-inclusion in the producer, repaired in
the producer rather than worked around in any consumer.

## Release Scope

Version: `8.0.2`.
Tag: `v8.0.2`.
Change: patch. 86 commits, no `feat:` among them — 16 `fix`, 21 `perf`,
30 `test`, 8 `refactor`, 4 `docs`, 1 `critique`, 2 `retro`, plus four
sentence-form commits. `git diff --name-status origin/main..HEAD -- skills/public
packaging .agents` adds no file, so no additive public surface moved and the
lightest honest bump is patch rather than minor.

## Surface-Lock Inventory

- Bypass contract owner: `scripts/env_bypass.py` and its four consumers
  (`scripts/check_staged_reversion.py`, `scripts/check_staged_router_change.py`,
  `scripts/check_staged_worktree_consistency.py`,
  `scripts/helper_provenance_lib.py`).
- The copy that cannot import the owner: `charness` (root CLI), bound by
  `tests/quality_gates/test_env_bypass.py`.
- Test infrastructure: `tests/script_closure.py`, `tests/seed_cache.py`,
  `tests/conftest.py`.
- Checked-in plugin export: `plugins/charness/scripts/` (gitignored, regenerated
  by `scripts/sync_root_plugin_manifests.py`).
- Audit evidence:
  `charness-artifacts/impl/2026-08-31-test-value-audit-staged-gate-family.md`.

## Findings

### Act Before Ship — all fixed before this artifact was written

- `check_staged_worktree_consistency.py` died at import through its own
  scheduled argv (`ModuleNotFoundError: No module named 'scripts'`). Measured
  against all three index-hygiene gates; the other two passed. Fixed in
  `1d0993a34` with a real-process test that fails on the pre-fix file.
- `tests/script_closure.py` could not see `import x` or `from scripts import x`,
  so `script_import_closure("task_run.py")` silently omitted
  `task_run_completion.py` — the exact failure the module exists to prevent,
  with the hand-written list it replaced already deleted. Fixed in `ba284321d`.
- The new seed-cache refusal escaped `conftest.pytest_configure`, turning a
  dubious-ownership checkout into pytest INTERNALERROR with zero tests
  collected — strictly worse than the fail-open collision it replaced. Fixed in
  `c75bfe7cd`.
- Two further unknown-is-not-empty collisions and a NUL-framing ambiguity in the
  seed digest. Fixed in `c75bfe7cd`.
- A fifth bypass copy in the root CLI, unmentioned, making "pinned ONCE" false
  repo-wide. Bound by test in `17bbcedf8`; drift verified by dropping `"on"`.
- `helper_provenance_lib` lost its stdlib-only import property with no analysis.
  Dual-path restored in `17bbcedf8`.

### Bundle Anyway — done in place

- Evidence corrections in the audit artifact: four copies → five; the vulture
  argument answered detection where the retro proposed enforcement; the scoped
  `+14/−9` headline given honest full accounting; "flaky" downgraded to an open
  question naming its own instrument's blind spot.

### Over-Worry — rejected with evidence, not deferred

- `source_env_present` (`charness:446`) is not the historical bare-truthiness
  bug. It answers PRESENCE, a different predicate, and its one caller wants that.
- `script_closure` dropping three-segment `scripts.a.b` paths is not reachable:
  no such subpackage or import exists in this repo.
- The eight deleted helpers are not reachable by a missed spelling. Checked
  independently against `getattr`, pytest hook/fixture names, toml/yaml strings,
  doctests and entry points.

### Valid but Defer

- `check_current_pointer_writes` cannot see a pointer name built from a variable
  stem. The reported defect was one layer off — the scanner, not the prefilter —
  and the attempted prefilter fix was measured to change nothing and reverted
  rather than shipped as cosmetic.
- `reviewed_input_verification` not recomputing component digests: downgraded on
  inspection, since `packet_sha256` already pins the bytes the identity lives in.
- Making the dead-code advisory blocking or non-opt-in.
- The four restatements of the "git failed ≠ empty answer" error contract across
  the gates; consolidating changes pinned message text.
- One standing-suite test is nondeterministic
  (`test_s2_the_checkers_own_scope_carries_no_odd_backtick_count`, 95 vs 96
  failures over byte-identical source). Not mutant-attributable; mechanism
  unexplained and explicitly not closed.

## Deliberately Not Doing

- Folding the root CLI's `bool_env` into `scripts/env_bypass.py`. The CLI is the
  installed standalone entry point and its source-root probe returns `None` when
  no charness tree is present, so the owner is not importable in the case that
  entry point exists to serve. Bound by test instead.
- Completing the closure of `test_prepush_close_keyword_guard`'s `guard-lonely`
  fixture. Its list is incomplete on purpose — the test asserts a PARTIAL install
  crashes with exit 2 — so deriving it would delete the subject of the test.

## Verification

- Standing suite: 8470 passed / 0 failed, working tree clean.
- `ruff check scripts/ tests/`: four findings, all pre-existing at
  `origin/main` and all in files this range does not touch.
- Plugin manifests synced via `scripts/sync_root_plugin_manifests.py`.
