# Resolution Critique #302 — gather agent-browser close + clean-runtime proof

Date: 2026-06-05
Issue: #302
Classification: bug
Reviewer: bounded fresh-eye subagent (general-purpose, read-only, shared parent
worktree) + operator self-critique.

## Slice under review

Four-gap bug-class fix: (1) guarantee `agent-browser close` on every in-process
path; (2) make a missing post-close runtime guard fail-visible
(`guard_unavailable`), not a silent clean; (3) make `gather_public_url.py` reach
the support web-fetch impl + cleanup proof from an exported/installed layout and
arbitrary repo_root; (4) stop the runtime guard from misclassifying
reparented/zombie agent-browser/Chromium residue as clean.

## Verdict: no blockers

The fresh-eye reviewer confirmed all four gaps correctly addressed (YES on each),
genuine regression guards (new tests reference symbols absent pre-fix), and
byte-identical mirrors.

- **Gap 1:** render+network wrapped in `try`, close + runtime proof in `finally`;
  no in-process post-open path skips close; an exception closes then propagates
  loudly (never silent clean). `attempts[-1]` cannot IndexError because the
  `direct-public-fetch` attempt is always appended before `_browser_stage`.
- **Gap 2:** missing guard returns `guard_unavailable` → degraded, vs the pre-fix
  `None` (= clean) silent skip.
- **Gap 3:** `resolve_runtime_guard` (repo_root/scripts first, then nearest
  ancestor) reaches the bundled guard in the exported layout; the reach test
  plants a *failing* bundled guard so a pass proves it ran, not skipped.
- **Gap 4:** reparented and zombie residue are mutually exclusive (no
  double-count); cleanup still targets only daemon trees (detect-not-reap),
  matching the Ceal-owned Non-Goal.

## Adversarial finding folded (was non-blocking, fixed in-slice)

The reviewer flagged that bare `chrome`/`chromium` substring markers would
false-positive a developer's desktop Chrome reparented to PID 1, and that
`run_slice_closeout.py` runs `--assert-no-orphans` unconditionally with the
waiver stripped — so the false positive could fail the closeout gate on other
machines with no remediation (cleanup cannot clear reparented residue). Folded:
`is_browser_residue_command` now counts bare Chrome/Chromium only with a
headless/automation indicator (`--headless` / `headless_shell`); the
agent-browser-specific names (`agent-browser`, `headless_shell`) still match
standalone. A regression test asserts a non-headless desktop Chrome at PID 1 is
NOT flagged while a headless Chromium is.

## Residual (accepted, not a defect)

If genuine reparented agent-browser residue exists, `--assert-no-orphans` stays
red and `cleanup_orphans` cannot reap it (PID-1 reaping is Ceal-owned). This is
the intended fail-visible behavior; the operator escape hatch is
`CHARNESS_AGENT_BROWSER_IGNORE_ORPHANS=1`. Live exported-host runtime proof is a
declared non-claim; coverage is test-level.

## Prevention

The `finally`-guaranteed close, the `guard_unavailable` degrade, the
exported-layout reach test (failing-guard-proves-ran), and the
reparented/zombie residue + desktop-Chrome-false-positive tests lock each gap so
a future edit that reintroduces a silent skip or misclassification fails a test.
