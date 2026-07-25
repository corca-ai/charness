# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- **v2.5.0 is PUBLISHED** (tag `v2.5.0 -> 666fc42f`; unauthenticated HTTPS observer
  200 on the public release page, installed readback `charness version -> 2.5.0`).
  Scope: two north-star slices from an adversarially verified drift audit, plus the
  pre-publish corrections the release review forced. Critiques in References.
  v2.4.3's standing baton-reconcile obligation is discharged by this line.
- **The mutation workflow no longer closes GitHub issues.** A scheduled green now
  comments a recovery *candidate* (run URL, sha, mode, sample manifest), labels it
  `mutation-recovered-candidate`, and stops; the close is a human's call. Both paths
  select on the workflow's own marker. **Runtime-unproven until a failure files a
  marked issue AND a later scheduled green runs** — the next cycle alone proves
  nothing (empty issue set) and no local gate runs `actions/github-script`.
  Installed consumer workflows are never re-rendered; adoption is a manual copy.
- `check_runtime_budget` now emits a **budget slack advisory** naming budgets whose
  worst recent run is far under the bar, so they cannot silently re-inflate.
- No open issues as of this session (re-check `gh issue list --state open` fresh);
  sibling scan closed through Tier 2, Tier 3 (E-J) stays boy-scout only.

## Next Session

1. **`retro` weekly-concept split** is the ready next slice, deferred not rejected:
   `weekly` is a second concept woven through six sections of a 155/160 body that
   `references/mode-guide.md` and `references/weekly-trends.md` already own. Needs:
   emit BOTH `mode-guide.md` and `section-guide.md` as weekly `required_reads`; port
   SKILL.md:39-40's adapter prescription (stronger than mode-guide.md:41's) before
   deleting it; two `PACKAGE_CONTRACTS` pins satisfied by SKILL.md:79 and :177 must
   land verbatim in the receiving reference.
2. Residuals recorded, not closed: `issue_close_comment_floor.py` still omits
   `evaluate_ai_provenance` and the ledger-field / close-keyword checks (its own
   slice); every quality run rewrites the tracked specdown report because
   [specdown.json](../specdown.json)'s reporters hardcode `outFile` — restore it by
   hand before staging; and the plugin-copy fresh-install render path is untested,
   which now matters because it is the ONLY delivery path for the workflow change.
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
