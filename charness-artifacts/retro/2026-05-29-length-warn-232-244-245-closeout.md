# Retro — length-warn + #232 + #244/#245 achieve run (closeout)

Mode: session

## Context

Closeout of the `/goal` run for
`charness-artifacts/goals/2026-05-29-length-warn-232-244-245.md`: a four-slice
arc — (A) advisory file-length WARN tier in `check_python_lengths.py`; (B) #232
issue-body safety via `issue_tool.py create --body-file`; (C) #244 auto-install
the find-skills SessionStart hook; (D) #245 dedup SessionStart hooks by logical
identity. Six commits (4 slices + 2 After-phase fixes). What matters next: the
recorded follow-ups (host_hook_install_lib.py split, find-skills status
coverage) and that the warn-tier signal is now acted on, not ignored.

## Evidence Summary

- Commits `9cb81e5` (A), `2a4fb82` (B), `dff0101` (C), `7111da6` (D), `6f8c791`
  (contract-snippet fix), `3c7f42e` (attention-state declarations).
- Broad read-only gate (`./scripts/run-quality.sh --read-only`): final run
  **68 passed, 0 failed**.
- Two bounded fresh-eye critiques (general-purpose subagents): Slice B
  (no blockers) and combined C+D (1 real BLOCKER found + fixed).
- Host-log probe `charness-artifacts/probe/2026-05-29-length-warn-232-244-245.json`
  (token_count `available`). Session-log derived (source:
  `~/.claude/projects/.../d046245e-….jsonl`): ~198 tool_use calls, ~484k
  cumulative output tokens — approximate, the per-session jsonl may include
  adjacent activity; treat as order-of-magnitude, not exact.

## Waste

- **Two closeout reworks the per-slice checks could not see.** (1) The Slice B
  markdown-wrap fix shortened a *required* core-contract snippet
  (`Do not ask for approval unless the user explicitly asks to review first.`),
  failing `run-evals` + a cautilus scenario; (2) the new C/D helpers introduced
  `disabled`/`skipped` strings that `validate-attention-state-visibility`
  requires declared. Both gates are broad-gate / pre-push only, so they
  surfaced at After-phase closeout rather than at slice time — two extra
  commits. Not catastrophic (the gates exist and caught it), but the feedback
  arrived one phase late.
- **A real data-loss blocker my own tests missed.** Slice D's second TOML marker
  exposed that `find_charness_toml_block`'s block-boundary loop broke only on its
  *own* marker, so uninstalling one charness TOML block would swallow an
  adjacent one. My Slice C/D tests exercised each hook in isolation; none placed
  two charness blocks adjacent and uninstalled one. The fresh-eye critique
  caught it — the per-slice critique earned its cost here.

## Critical Decisions

- **Sibling module over full generalization (C).** Putting find-skills wiring in
  `host_hook_find_skills.py` reusing install_lib primitives (rather than a
  HookSpec refactor of the per-host functions) kept the usage-episodes path
  byte-for-byte unchanged — zero regression on the installer that runs every
  `charness init/update`. Cost: cross-module access to underscore primitives,
  accepted as cohesive-subsystem reuse and recorded.
- **Logic out of the CLI entrypoint to honor the limit (B).** `create` lives in
  `issue_create.py` so `issue_tool.py` stays ≤360 — Slice A's warn tier directly
  drove this, the arc paying off within itself.
- **One combined C+D critique, not per-slice.** The blocker only manifests once
  *both* a second marker (C) and the matcher change (D) exist; a C-only critique
  would likely have missed it. Sequencing the critique after the coupled pair
  was the decision that surfaced the bug.

## Expert Counterfactuals

- **Test-interaction lens (property/edge-case testing discipline).** When
  introducing a *second* instance into a dimension that was previously
  single-valued (a second TOML marker), write the coexistence + mutation test
  *first* (install both, uninstall one, assert the other survives). That test
  would have failed before the critique ran, catching the blocker at slice time.
  Changed action: "added a second value to a scanned dimension" ⇒ immediately add
  an adjacent-instances test.
- **Gate-placement lens (Deming, build quality in) — corrected after user
  feedback.** The right question is not "run it manually before commit" (a
  memory-dependent habit — the exact fragility that failed here). It is binary:
  a check that is **fast + agent-free + hard-fail belongs in pre-commit**
  (automatic, no memory burden); a check that is genuinely costly or agent-backed
  stays **pre-push-only by deliberate cost tradeoff** — and then late feedback is
  by design, not waste. Both checks that caught my reworks
  (`validate-attention-state-visibility` ≈0.8s, `run-evals` ≈2.3s) are cheap +
  agent-free + hard-fail, so they belonged in pre-commit all along.

## Next Improvements

- **capability (DONE this follow-up):** Wired `validate-attention-state-visibility`
  (staged `scripts|skills/*.py`) and `run-evals` (staged `skills/`) into
  `.githooks/pre-commit`, matching the existing staged-path-conditional pattern.
  Verified: a broken contract snippet now blocks the commit (HOOK EXIT=1 with the
  exact missing-snippet error); a clean tree passes. This structurally eliminates
  both closeout reworks — no manual habit, no custom "changed-surface→gate-subset"
  mechanism needed (pre-commit already does staged-conditional gating).
- **placement rule (memory):** cheap + agent-free + hard-fail ⇒ pre-commit;
  costly/agent-backed ⇒ pre-push only (accepted cost). "pre-push already runs it"
  is *not* a sufficient reason to keep a cheap check out of pre-commit. The
  advisory file-length WARN tier is the legitimate exception: it does not
  fail, so it does not fit pre-commit's pass/block model and stays pre-push.
- **workflow:** When introducing a *second* value into a previously single-valued
  scanned dimension (a second marker/identity), add the coexistence + mutation
  test in the same slice (see Sibling Search) rather than relying on the
  fresh-eye critique to catch the interaction.

## Sibling Search

Transferable pattern: **a scanner/matcher that is correct only because a single
value existed silently breaks when a second value is introduced** (here: the
Codex TOML block-boundary loop broke only on its own marker once a second
charness marker appeared). Four-axis scan across the host-hook subsystem:

- **JSON dedup (`_entries_match_command`)** — uses script *basename* identity;
  two distinct charness basenames coexist correctly (tested). No bug.
- **State keys** — usage-episodes uses `host`, find-skills uses
  `<host>:find_skills_routing`; no collision with `schema_version` or bare host
  keys (tested). No bug.
- **`detect_host_hook_actual` / `session_capture_status`** — read `state.get(host)`
  for usage-episodes only; they do not iterate markers, so a second marker does
  not break them — they simply do not *cover* find-skills (recorded follow-up,
  not a breakage).
- **`find_charness_toml_block`** — the one site with the single-value assumption;
  fixed to break on any `# charness:` marker + 2 regression tests
  (both uninstall directions).

Decision: **fix already complete; no additional sibling fixes required.** The
direct siblings (JSON matcher, state keys) were designed generically in Slice D
so they never had the bug; the detect/status non-coverage is a tracked
follow-up, not a defect.

## Persisted

yes — see path emitted by `persist_retro_artifact.py` below; recent-lessons
digest refreshed from this artifact.
