# Lane A — the changed-line gate's analyzed/changed count pair
Date: 2026-08-02

## Decision Under Review

Make every verdict-emitting path of `scripts/check_changed_line_mutation_coverage.py`
carry an explicit analyzed/changed count pair, and put the scope split and its
disclosure in a new module rather than appending to a gate at 476/480 code lines.
Disclosure only: refusal behaviour unchanged, with the refusal question fenced out
to D45.

## Failure Angles

- The denominator itself is partial. `changed` is derived from
  `base..resolved_head_sha`, so an `--allow-dirty` run emits a pair that reads
  complete over a set that excluded uncommitted pool edits — this goal's own
  defect class, in the code written to close it.
- A payload-shape change that silently alters a verdict. Consumers prefix-match
  the empty-scope `reason`, and `_finalize` re-emits reports on the drift path.
- The move of `_apply_file_limit` across modules breaking an existing test that
  reaches it through the gate module.
- A new module that is a length-cap dodge rather than a cohesive unit (D33).

## Counterweight Pass

- The `--allow-dirty` gap is real but is NOT a reason to shrink the pair: the
  pair's population is the range's, which keeps it comparable across runs, and the
  same payload already carries `dirty_pool_unverified` plus the offending files.
  Documenting the limit and pinning it with a test is the proportionate answer;
  changing the arithmetic would trade one silent gap for another.
- The mirror blocker below looked like process overhead and was not: the export
  would have shipped a `ModuleNotFoundError`.
- The "should a partial denominator refuse" question is genuinely out of scope,
  not avoidance — it is D45's toll and the operator's call.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/packaging_lib.py:248-250 | action: fix | note: the slice packet claimed no `plugins/` mirror was involved; the whole `scripts/` tree is mirrored, so the export would have shipped the un-repaired gate plus a ModuleNotFoundError for the new module. Parent-verified (the mirrored twin of the previous split exists, the new module did not) and folded by running the sync.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/changed_line_scope_counts.py:56-71 | action: fix | note: the module's own docstring claimed an equal pair means "nothing was left out", false on an --allow-dirty run. Rewritten to state the population and its limit, and pinned by test_the_pair_is_the_ranges_population_and_says_so_beside_the_dirty_keys.
- F3 | bin: act-before-ship | evidence: moderate | ref: scripts/check_changed_line_mutation_coverage.py:476 | action: fix | note: the SCOPE_MISMATCH path's pair depends on the scope rebind landing before the check, and nothing tested it; an assertion was added to the existing mismatch test.
- F4 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_changed_line_mutation_coverage.py:108 | action: fix | note: `_apply_file_limit` became a cross-module re-export an external test depends on, without being in `__all__` — the exact shape a recorded `ruff --fix` incident once deleted. Added.
- F5 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/test_changed_line_scope_counts.py:56 | action: fix | note: the reviewer read the first fixture as fully subsumed by the control. Resolved by giving it a distinct claim (stderr and JSON channels agreeing) rather than deleting it.
- F6 | bin: valid-but-defer | evidence: weak | ref: scripts/changed_line_scope_counts.py | action: document | note: the computed pair does not restate its population inside the payload the way the not-computed variant states its reason. Folded into the docstring rather than the payload; adding a fourth key for it would be ceremony.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (this repo's typed read-only reviewer agent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, `run_in_background: false`, no host addressing/team `name` (an addressed spawn routes onto a teammate protocol whose retrieval tool is not exposed here). No model/effort override: on a Claude Code host the per-host contract uses session-model inheritance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: the spawn returned findings inline in this session, and the reviewer reported its own envelope as Read/Grep/Glob only.
- Delivery state: findings-received

One round. This slice changes a payload shape, not verdict logic — exit codes and
blocking behaviour are pinned unchanged by a control test — so the second-round
obligation does not fire. It is recorded here because the goal's
`## Discuss Before Activation` item (2) says otherwise and the plan critique's
later fold moved that obligation to Lane B.

Parent-side boundary integrity: `.charness/reviewer-boundary/lane-a-round1.json`,
verified `clean`, no drift.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer was given an inline slice packet naming intent, changed files, four expected invariants, the proof runs, non-claims, and six questions. The binding floor is therefore off by design, and this critique does not claim packet-bound identity. -->

## Boundary Ownership

- Producer: `scripts/changed_line_scope_counts.py` (the scope split and its count pair) and `scripts/check_changed_line_mutation_coverage.py` (the verdict payload that carries it).
- Consumer: an operator reading the JSON verdict, `scripts/prepush_focused_changed_line_coverage.py`, and this repo's own tests.
- Owning surface: the gate owns its verdict contract; the new module owns scope arithmetic; the tests own the proof.
- Verdict: single-surface
