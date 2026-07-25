# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- **v2.5.0 is PUBLISHED** (tag `v2.5.0 -> 666fc42f`; HTTPS observer 200, installed
  readback `charness version -> 2.5.0`). v2.4.3's baton obligation is discharged here.
  The `retro` weekly deletion below landed AFTER the tag and ships in the next cut.
- `retro`'s `weekly` mode is DELETED (one shape now). Its one real asset — the
  closeout-telemetry miner, 985 records and a recurring 475s gate — moved to
  `references/closeout-telemetry.md` and now runs on EVERY retro. Retired adapter keys
  (`default_mode`, `weekly_window_days`, `snapshot_path`) pass through ignored.
- **The mutation workflow no longer closes GitHub issues.** A scheduled green
  comments a recovery *candidate*, labels it, and stops; the close is a human's call.
  **Runtime-unproven until a failure files a marked issue AND a later green runs** —
  no local gate runs `actions/github-script`. Installed consumer workflows are never
  re-rendered; adoption is a manual copy.
- `check_runtime_budget` now emits a **budget slack advisory** naming budgets whose
  worst recent run is far under the bar, so they cannot silently re-inflate.
- No open issues as of this session (re-check `gh issue list --state open` fresh);
  sibling scan closed through Tier 2, Tier 3 (E-J) stays boy-scout only.

## Next Session

1. **Sweep for other built-with-intent-but-unused modes and options** (operator
   request). `retro`'s `weekly` was the first instance: a deliberately designed mode
   whose entire behavioral delta was two extra `required_reads`, invoked once in
   3.5 months, with a configured snapshot nothing ever read. Look for the same shape
   elsewhere — adapter enum fields, planner branches, `--mode`/`--part` style flags,
   preset variants. The tell is a branch whose two arms produce nearly the same plan.
   `inventory_skill_ergonomics.py`'s `mode_option_pressure` rule is a starting
   detector, not the answer; usage evidence (artifact counts, git history) decides.
2. Residuals, not closed: `issue_close_comment_floor.py` omits
   `evaluate_ai_provenance` and the ledger-field / close-keyword checks; every quality
   run rewrites the tracked specdown report because [specdown.json](../specdown.json)
   hardcodes `outFile` — restore by hand before staging; the plugin-copy fresh-install
   render path is untested, the ONLY delivery path for the workflow change.
3. Budgets were retuned for `local-linux-x86_64-36cpu` only; aarch64 and the
   unprofiled defaults were left alone. Act on `SLACK` lines from
   `check_runtime_budget.py --runtime-profile <profile>`.
4. Still deferred, unchanged: inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory, D18,
   stale `charness-run-*` basetemp reaping, and #451's two unacted siblings (~20
   `init_adapter.py` thin-assertion scaffolds; the identifier-literal blind spot at
   `announcement_adapter_lib.py:125` — read its critique first). #449 was declined
   over its CI write-permission surface; do not re-propose without new information.

## Discuss

- Do not re-litigate two refuted audit findings: removing the dup-ratchet hard arm
  or the boundary-bypass ratchet as "teeth on reversible work". The boy-scout arm
  runs at `floor_F: 0` and has never blocked in production; every cited
  boundary-bypass false block already has a landed fix.
- #448 scoped-accept deferred items (its critique): overlay-missing advisory in
  scoped mode, refused-early-return advisories, explicit `--accept-family` of an
  intentional id test — only with the next dup-ratchet slice.

## References

- [v2.5.0 release critique](../charness-artifacts/critique/2026-07-25-v2-5-0-release-critique.md) · [notes](../charness-artifacts/release/2026-07-25-v2.5.0-notes.md)
- [boundary-hardening critique](../charness-artifacts/critique/2026-07-25-irreversible-boundary-terminal-trust-critique.md) · [staleness critique](../charness-artifacts/critique/2026-07-25-stale-proof-and-duplicated-prose-critique.md)
- [v2.4.3 release critique](../charness-artifacts/critique/2026-07-23-v2-4-3-release-critique.md) · [#449 brief](../charness-artifacts/issue/2026-07-23-issue-449-brief.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md) · [retention RCA](../charness-artifacts/debug/2026-07-20-debug-review.md) · [basetemp deletion-race RCA](../charness-artifacts/debug/2026-07-20-standing-pytest-basetemp-deletion-race.md)
- [release state](../charness-artifacts/release/latest.md) · [quality review](../charness-artifacts/quality/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
