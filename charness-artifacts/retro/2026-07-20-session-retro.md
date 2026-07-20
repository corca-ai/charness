# Retro: Session — Flaky-Suite Debug and v2.3.1 Release
Date: 2026-07-20
Mode: session

## Context

Handoff OPEN SMELL (flaky/nondeterministic suite under parallel/`--release` load)
was routed through `debug` → `impl` → follow-up resolution → `release`. Two
independent root causes were fixed and shipped in v2.3.1: (a) release-failure
retention evicted by coarse-granularity `st_mtime_ns`, and (b) a pytest temp-tree
deletion race (the standing runner's lock-less `pytest-*` basetemp deleted mid-run
by nested pytest cleanup). What matters next: the harness's own proof-infra now has
deterministic regression tests for both; the next session picks a fresh slice.

Addendum (same day, second unit): the sibling-scan Tier-1 fixes slice
(commit 092ab996) — three 1-2 line concurrency/tie-direction fixes (A/B
`unlink missing_ok`, C mtime tie `>=`→`>`), mirrors synced, two regression
tests, clean bounded critique, locked closeout with mutation coverage.
Auto-triggered by changed export surfaces.

Addendum (same day, third unit): the `verified` additive migration slice
(commit 18483dc9) — `verify-closeout` gains a `confirmation`
{observer, channel, scope, line} object with a scope-tracking verb; the
sibling Discuss clause (pre-commit rollback persistence) was closed by
evidence as already-shipped rather than rebuilt. Auto-triggered by changed
export surfaces.

## Waste

- False non-claim from a scope-mismatched disconfirmer. I ran symptom (b)'s two
  named files in isolation at `-n 16`, saw them pass, and wrote "did NOT reproduce
  / resource contention" into BOTH the durable debug artifact and the handoff. The
  full `--release` suite falsified it minutes later (11 failed, 1439 errors). Cost:
  a wrong durable claim that fresh-eye review (Angle C) flagged and that I then had
  to correct twice. The isolated subset never exercised the nested-pytest cleanup
  that only the full suite triggers — it was not a valid disconfirmer for a
  load-dependent flake.
- Rename without a consumer grep. I renamed the `default_basetemp` leaf
  (`pytest-<ns>` → `charness-run-<ns>`) without first grepping for its name-based
  consumers; two tests asserting the old leaf failed only when the full suite ran,
  and a fresh-eye reviewer caught a third consumer (the economics session regex)
  that would have silently under-reported.

- (Tier-1 fixes slice) Near-zero repo waste — the audit artifact's exact
  file:line + remediation + confirmed-safe set made the slice mechanical. One
  host-side friction: the spawned bounded reviewer's final report arrived only
  as an idle notification, so the parent had to extract it from the subagent
  transcript JSONL by hand before the boundary-fingerprint verify.
- (verified-migration slice) Two locked closeout runs blocked on a stale
  cached broad-proof fingerprint before the pattern registered: after any
  critique-driven edit the cache is expectedly stale, so the final run should
  go straight to `--refresh-broad-pytest-proof` instead of paying a blocked
  full-gate pass first.

## Critical Decisions

- Routing through `debug` (falsifiable hypothesis + reproduction before repair)
  is what revealed symptom (b) was a DIFFERENT root cause than the handoff's
  "shared state across workers" hypothesis — it was a pytest cleanup race.
- Reproducing the deletion race deterministically against pytest's OWN
  `make_numbered_dir_with_cleanup`/`cleanup_numbered_dir` before fixing — turning a
  ~1-in-3 flake into a deterministic probe, then a regression test with teeth.
- Deferring the third follow-up (reaping stale `charness-run-*` basetemps): an
  ad-hoc reaper would reintroduce the very deletion-race class just fixed.

- (Tier-1 fixes slice) Used the default single instrumented broad run for
  mutation coverage instead of the suggested "focused" producer, which spanned
  nearly the whole quality-gates directory anyway — avoided a double broad run.
- (Tier-1 fixes slice) The boundary-escalation probe fired on
  `scripts/*_lib.py`, so the self-assessed small slice was escalated to a
  standalone durable critique validated with `--changed-ref` — the objective
  probe overriding self-assessment, as designed.
- (verified-migration slice) Resolving a Discuss item by evidence of prior
  shipment (commit archaeology: the entry predated the implementation by an
  hour) instead of rebuilding the mechanism; and adopting both reviewer
  should-fixes (scope-tracking verb, distinct-observer disclaimer) before
  commit, which is what kept the new vocabulary from recreating the
  terminal-sounding trap it was built to remove.

## Expert Counterfactuals

- Engelbart (system-improving-itself: design T alongside LAM). The flake lived in
  the harness's own proof-infrastructure — the thing that certifies everything
  else. The method gap (LAM) was "an isolated subset run is a sufficient
  disconfirmer"; the missing tool (T) is a disconfirmer whose SCOPE matches the
  failure's trigger (full-suite load/concurrency). Co-designing them — the method
  "reproduce load-dependent flakes under the real load" plus the deterministic
  cleanup-driving regression harness I ended up building — is what converts the
  one-off fix into a repeatable capability, instead of a chat-only caution.
- "Make the implicit contract explicit" (sharpens the rename miss, not the same as
  Engelbart). The basetemp leaf name is a contract re-matched by string in distant
  files (`standing_test_economics_lib.PYTEST_SESSION_RE`, two tests). The fix works,
  but the coupling stays a convention; a shared named constant consumed by producer
  and matchers would make the next rename refactor-safe rather than grep-dependent.

- (Tier-1 fixes slice) Engelbart (system-improving-itself). The sibling-scan
  audit artifact IS the tool (T) this loop built: a durable fix backlog with
  exact locations, remediations, and a confirmed-safe set. The method (LAM)
  "record scan findings fix-ready so a later session fixes without
  re-deriving" demonstrably worked — the whole slice consumed zero re-scan
  effort. The counterfactual is restraint: a machine-readable fix manifest for
  three one-line items would have been tooling for its own sake; keep the
  markdown-artifact form at this scale.

## Next Improvements

- workflow: before writing "not reproduced" / "does not happen" for a flake,
  scope-match the disconfirmer to the failure's trigger conditions (load,
  concurrency, scale) and reproduce under the FULL environment; an isolated subset
  passing is not a valid absence proof.
- workflow: before renaming a widely-referenced constant, grep for its name-based
  consumers (`startswith`/`==`/regex) across scripts, skills, tests, and mirrors,
  and batch the assertion updates with the rename.
- memory: persist both lessons in the generated recent-lessons digest so the next
  session inherits the disconfirmer-scope and rename-consumer-grep guards.

- memory: (Tier-1 fixes slice) when a spawned named subagent goes idle without
  its report reaching the parent, read the last assistant text from its
  transcript under `~/.claude/projects/<session>/subagents/` instead of
  re-spawning or substituting a same-agent pass; verify the reviewer boundary
  fingerprint afterward as usual.
- workflow: (Tier-1 fixes slice) keep the fix-ready scan-artifact pattern
  (file:line + severity + remediation + confirmed-safe set) for any multi-
  finding audit that hands fixes to a later session.

## Sibling Search

- same layer: `standing_test_economics_lib.py` `PYTEST_WORKER_RE`/`PYTEST_SEED_PREFIXES` name-couplings | decision: intentional boundary | proof: read — these match pytest-xdist's own fixed `popen-gw*` / seed-fixture names, not a charness-owned renameable constant.
- abstraction up: the general "charness-owned constant re-matched by a distant regex/startswith without a shared symbol" (the basetemp-leaf class) | decision: valid follow-up outside the slice | proof: grep found producer `run_standing_pytest.py:69` vs consumer `standing_test_economics_lib.py:33` coupled only by the string. follow-up: deferred docs/handoff.md (extract a shared basetemp-name constant when that area is next touched).
- specialization down: the `charness-run-<ns>` / `pytest-*` cleanup-glob distinction | decision: same waste, fix now | proof: pinned by `test_default_basetemp_survives_nested_pytest_cleanup` + the economics regex test.
- mental-model siblings: any "X passes under condition A ⇒ X is fine" where A omits the failure trigger (the weak-disconfirmer class) | decision: same waste, fix now | proof: the retention flake (symptom a) was correctly reproduced 2/8 before its claim; only symptom (b) carried the scope-mismatched disconfirmer, now corrected and reproduced under full load.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-20-session-retro.md

## Packet Consumed

charness-artifacts/retro/2026-07-20-075910-packet.md
