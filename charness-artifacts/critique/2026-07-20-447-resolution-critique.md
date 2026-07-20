# Critique Review
Date: 2026-07-20

## Decision Under Review

Issue #447 resolution (bug): the standing-test-economics inventory omitted
`.mjs` test files because it re-derived test-file discovery from a hardcoded
glob list in the portable skill body, divergent from each consumer repo's own
authoritative test runner — while the quality adapter's own Design Rule says
repo-specific patterns belong in the adapter, not the skill body. `.mjs` was one
symptom of that structural cause.

Fix (chosen depth: **adapter is the authoritative source, graded fallback**):
- immediate: `.test.mjs` / `.spec.mjs` added to the built-in default globs.
- structural: new adapter field `test_file_discovery {command, patterns,
  patterns_mode}`. The inventory now loads the quality adapter and resolves the
  test surface by precedence — authoritative `command` (consumed verbatim) →
  adapter `patterns` (extend|replace the defaults) → built-in defaults. A
  declared command that fails, times out, or returns an empty surface is marked
  `test_discovery.degraded` rather than silently substituting the default globs.

Fresh-eye causal review ran first (parent-delegated bounded reviewer); this
resolution critique ran three distinct-lens bounded reviewers plus an in-lens
counterweight. Both reviewer passes verified clean by the rail-1
reviewer-boundary fingerprint (no index/worktree drift).

## Failure Angles

- Recurrence & detection: does the adapter seam + degraded-surfacing actually
  stop the silent-undercount class, or does a hole remain?
- Boundary ownership & portability: is discovery now owned at the right layer
  (adapter/consumer vs portable body), and does it stay portable across
  no-adapter / non-git / plugin-mirror layouts?
- Correctness counterweight: real implementation bugs in the graded-fallback
  engine, then separate genuine blockers from over-worry.

## Counterweight Pass (four-bin triage)

- K1 | act-before-ship (fixed): a `command` that exits 0 but prints nothing
  returned `command_status: ok, degraded: false, count: 0` — the exact
  silent-undercount class the field exists to remove, re-entered from the
  exit-0 direction. Now an empty authoritative surface is
  `command_status: empty, degraded: true`, keeping the authoritative empty
  answer instead of substituting defaults. Regression test added.
- K2 | bundle-anyway (fixed): `_discover_by_command` used `subprocess.run(...,
  text=True)`; a lister emitting non-UTF-8 raises `UnicodeDecodeError` (a
  `ValueError`, outside the caught `(OSError, SubprocessError)`), crashing the
  inventory against its own "degrade, never crash" contract. Added
  `errors="replace"`. Regression test added.
- K3 | bundle-anyway (fixed): the shell trust boundary was implicit. Documented
  in `references/adapter-contract.md` that `command` runs via shell in
  `repo_root` as trusted repo-owned config (same boundary as `gate_commands` /
  mutation `commands.*`), bounded by timeout and the under-repo-root path drop.
- K4 | over-worry: `shell=True` as a security defect — repo-owned committed
  config with existing precedent (`gate_commands`, mutation commands,
  `announcement_verification_lib`); symlink/`..` escape — both sides `.resolve()`d
  and `relative_to`-filtered; a `command` supplied as a list — the validator
  normalizes it before the CLI reads it; replace-vs-extend and the pre-existing
  pytest-bucket-vs-file-count asymmetry for non-Python files — correct and
  already documented. No action.
- K5 | valid-but-defer: a stack-agnostic "zero / near-zero test surface"
  advisory (a Go/Rust/Ruby repo declaring neither command nor patterns still
  silently inherits the built-in default list) and per-glob parametrized
  coverage + a timeout-branch test. Real but beyond #447's JTBD; recorded as
  follow-up rather than bundled.

## Boundary Ownership

- Verdict: owned-correctly

The fix touches a shared, cross-surface generic (the quality adapter contract),
so the producer/consumer brief applies. The portable body owns the discovery
*mechanism* and the zero-config *default*; the consumer repo owns its
*authoritative surface* via the new adapter `test_file_discovery` field. The
inert default in `infer_quality_defaults` carries no repo-specific patterns, and
the command posture matches the repo-owned-command-string precedent
(`gate_commands`, mutation `commands.*`), not the structured `startup_probes`
argv form. No producer/consumer inversion; the seam is owned at the adapter
layer where repo-specific discovery belongs.

## Recurrence Verdict

The structural pattern-divergence class is closed for any repo that declares a
command or patterns, and the mjs default fixes the zero-config JS/TS/ESM case.
The two deferred items (zero-count backstop, extra failure-branch tests) are
detection hardening, not open instances of the resolved bug.

## Reviewer Tier Evidence

<!-- allowed Host exposure state enums only -->
- Requested tier: high-leverage
- Requested spawn fields: none — Claude Code host, typed `bounded-reviewer` (Read/Grep/Glob) with session-model inheritance per the repo per-host subagent contract; no Codex model requested on this host, so the omission is contract-conformant, not a degradation.
- Host exposure state: host-defaulted
- Application state: the host spawned the typed `bounded-reviewer` agent by name for the causal review and for all three critique-angle reviewers; the read-only envelope bound (a reviewer reported "Envelope: bound — only Read/Grep/Glob visible") and the rail-1 reviewer-boundary fingerprint verified clean (no index/worktree drift) after the causal review and after the three critique reviewers, so approvals are valid and reviewers ran on the parent's session-inherited model.

## Fresh-Eye Satisfaction

parent-delegated — one causal-review reviewer plus three distinct-lens
resolution-critique reviewers with an in-lens counterweight; rail-1
reviewer-boundary fingerprint verified clean around both passes.
