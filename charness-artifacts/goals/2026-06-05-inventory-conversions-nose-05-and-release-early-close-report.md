# Early Close Report: inventory-conversions-nose-05-and-release

Goal: `charness-artifacts/goals/2026-06-05-inventory-conversions-nose-05-and-release.md`

## Why early closeout

All four planned slices completed and verified well inside the 3h timebox:
nose 0.5 integration (commit `7bd7d1ee`), the five `inventory_*` in-process
conversions with a real boundary-bypass baseline drop 94→90 (commit `6b758e28`),
and the full 0.21.0 publish — `origin/main` + tag `v0.21.0` + a verified GitHub
release (commits `b9d2b342`, `17110205`, `ac3f7f8a`). The read-only quality gate
is green (71/0) at both code-slice boundaries, packaging validators pass, and all
three substantial slices passed bounded fresh-eye review (SHIP). The release was
the terminal deliverable, so no in-scope slice remains; continuing would mean
starting out-of-scope work rather than finishing this goal. Closing inside the
reserve window because the bundled scope is genuinely exhausted (done-early), not
to skip remaining work.

## User decisions needed

None blocking. One user decision was taken mid-run via `AskUserQuestion`: the
publish boundary — "Full publish (tag + GitHub release)" vs branch-push-only vs
stop-before-push; the user chose full publish, which was executed and verified.
No further decision is required to close this goal.

## Residual / non-claims

- Real-host proof (second-machine / clean temp-home install smoke) is **owed, not
  run** — work happened on the dev machine; the checklist is recorded in
  `charness-artifacts/release/latest.md`.
- The publish needed manual recovery after the #194 usage-episodes pre-push gate
  flake (the failing test passes in isolation; the authoritative `--release` gate
  had already passed). No quality gate was bypassed. The publish-flow resilience
  gaps are filed as follow-up #305.

## Waste and retro

The mid-publish flake left a partial state the non-resumable helper could not
continue, forcing hand completion; the installed-cache `publish_release.py`
bootstrap failure cost one dead-end attempt; two inventory scripts hid a
sibling-import testability gap until conversion exercised them. All captured in
the session retro
`charness-artifacts/retro/2026-06-05-inventory-conversions-nose-05-and-release.md`,
whose Next Improvements feed this goal's `## Auto-Retro` dispositions (applied
fixes + follow-up #305).
