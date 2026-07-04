# Vulture Dead-Code Advisory Wiring Closeout
Date: 2026-07-04

## Decision Under Review

Wiring the pre-existing `run_dead_code_advisory.py` (vulture-backed) into
`run-quality.sh` as a DEFAULT-OFF, opt-in, never-blocking advisory gate — the one
concrete gap the 2026-07-04 gate-reclassification audit named (config + runner existed
but were never invoked). Operator chose wire-only; findings triage deferred. Shipped: the
opt-in inline guard (`CHARNESS_QUALITY_DEAD_CODE=1` or explicit `dead-code-advisory`
label, mirroring the agent-browser-runtime gate), an `ADVISORY:` surfacing line in the
runner's human output, a seed stub, and behavioral tests.

## Failure Angles

- Not actually default-off (leaks into the normal battery). Checked: the guard uses
  `label_is_explicitly_selected` (false on empty labels) + a bare `if`/`queue_timed`, not
  `queue_selected`, so the "empty labels selects all" path never applies; behaviorally
  verified (`test_dead_code_advisory_gate_is_default_off`) and on the real repo.
- Not actually advisory (can block the run). **This angle found a real blocker** — see F1.
- The `ADVISORY:` line broke the pinned `--json`/`--summary` contract. Checked: both paths
  return before the human block; existing JSON tests pass.
- Opt-in semantics wrong (silently does nothing, or leaks). Checked: env opt-in runs
  regardless of label scoping (queue_timed bypass), explicit label runs it; both proven.
- Tests non-falsifiable or the seed stub has side effects on other quality-runner tests.
  Checked: opt-in/ADVISORY tests fail on revert; exact-count tests use scoped labels that
  never opt in, so the added stub is inert until queued; full file 48 passed.

## Counterweight Pass

- Real blocker folded now (F1): with vulture ABSENT, `run_vulture` returns a "missing"
  dict lacking `classification_counts`; the human output keyed it directly and crashed
  (exit 1), so an opted-in advisory gate turned the run red — teeth exactly where the
  north-star says there should be none. The crash line predated this change, but the
  wiring is what newly routes an opted-in run through it, so it is this slice's to fix.
  Fixed with `.get(...)` + a falsifiable regression test; reproduced exit-0 after the fix.
- Not over-built: findings triage (33 review_candidates on the real run) is deferred per
  the operator's wire-only choice, not silently dropped — it is the top Next-Session item.
- Deliberately minimal: the fix is the one-line defensive `.get()`, not a broader
  status-specific human-output rewrite; the missing/error runs already print a clear
  "missing"/"error" status line and exit 0.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/run_dead_code_advisory.py:219 | action: fix | note: vulture-missing human path crashed (KeyError on classification_counts → exit 1), breaking the never-blocking advisory guarantee; fixed with .get() + a regression test that simulates vulture absent and asserts exit 0, reproduced before/after
- F2 | bin: over-worry | evidence: strong | ref: scripts/run-quality.sh:390 | action: document | note: default-off guard uses label_is_explicitly_selected + queue_timed (not queue_selected), so a normal run never queues it — confirmed behaviorally and on the real repo
- F3 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/run_dead_code_advisory.py:200 | action: document | note: the ADVISORY line lives only in the human path (after the --json/--summary returns), so the pinned machine-output contract is intact
- F4 | bin: over-worry | evidence: moderate | ref: tests/quality_gates/support.py:? | action: document | note: adding the seed stub has no side effects — exact-count quality-runner tests use scoped label sets that never opt into this gate

Fresh-eye satisfaction: parent-delegated — a bounded fresh-eye subagent (general-purpose,
id af9fe0bd5baf1215a) adversarially reviewed the staged diff across six angles and returned
SHIP-AFTER-FIXES, CONFIRMING the F1 missing-vulture crash by execution (it ran the human
path with vulture absent and observed the KeyError/exit 1) and refuting the other five
angles by running the tests, dup-ratchet, and mirror-drift. The single blocker it raised
was fixed in this slice (with a regression test reproducing exit-0), so the shipped change
resolves what it reviewed rather than merely matching it.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent in a different agent context, adversarial, read-only in the shared parent worktree
- Requested spawn fields: the full staged diff, the wire-only claim, and six adversarial angles (default-off, advisory/never-block, JSON-contract, opt-in semantics, test falsifiability, mirror/dup)
- Host exposure state: applied
- Application state: host-confirmed: subagent af9fe0bd5baf1215a ran to completion and returned SHIP-AFTER-FIXES with the F1 blocker reproduced; the fix + regression test were applied and verified this session
