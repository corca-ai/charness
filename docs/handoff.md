# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Current State

- Two north-star slices from an adversarially verified drift audit landed on
  `main` (`2116904c`, `106f6d2f`); the release cut follows, and the baton
  reconcile after it records the published version. Critiques in References.
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

1. **`retro` weekly-concept split** is the ready next slice, deliberately deferred
   rather than rushed: `weekly` is a second concept woven through six sections of a
   155/160 body, while `references/mode-guide.md` and `references/weekly-trends.md`
   already own it and `plan_retro_run.py` already routes weekly runs to the latter.
   Needs: emit BOTH `mode-guide.md` and `section-guide.md` as weekly
   `required_reads`; port SKILL.md:39-40's adapter prescription (stronger than
   mode-guide.md:41's) before deleting it; two `PACKAGE_CONTRACTS` pins currently
   satisfied by SKILL.md:79 and :177 must land verbatim in the receiving reference.
2. Two residuals recorded, not closed: `issue_close_comment_floor.py` still omits
   `evaluate_ai_provenance` and the ledger-field / close-keyword checks (same
   argument that justified wiring the HOTL floor, but its own slice); and every
   quality run rewrites the tracked specdown report because
   [specdown.json](../specdown.json)'s reporters hardcode `outFile`, so
   `-out <tmpdir>` does not redirect them — restore it by hand before staging.
3. Budgets were retuned for `local-linux-x86_64-36cpu` only; the aarch64 profile
   and unprofiled defaults were left alone (no measurements from this machine).
   Run `check_runtime_budget.py --runtime-profile <profile>` and act on `SLACK`.
4. Still deferred, unchanged: inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory, D18,
   stale `charness-run-*` basetemp reaping, and #451's two unacted siblings (~20
   `init_adapter.py` thin-assertion scaffolds; the identifier-literal blind spot at
   `announcement_adapter_lib.py:125` — read its critique first). #449 was declined
   over its CI write-permission surface; do not re-propose without new information.

## Discuss

- Do not re-litigate two refuted audit findings: removing the dup-ratchet hard arm
  and the boundary-bypass ratchet as "teeth on reversible work". Both were refuted
  with evidence — the boy-scout arm runs at `floor_F: 0` and has never blocked in
  production, and every cited boundary-bypass false block already has a fix.
- #448 scoped-accept deferred items (its critique): overlay-missing advisory in
  scoped mode, refused-early-return advisories, explicit `--accept-family` of an
  intentional id test — pick up only with the next dup-ratchet slice.

## References

- [boundary-hardening critique](../charness-artifacts/critique/2026-07-25-irreversible-boundary-terminal-trust-critique.md) · [staleness critique](../charness-artifacts/critique/2026-07-25-stale-proof-and-duplicated-prose-critique.md)
- [v2.4.3 release critique](../charness-artifacts/critique/2026-07-23-v2-4-3-release-critique.md) · [#449 brief](../charness-artifacts/issue/2026-07-23-issue-449-brief.md)
- [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [retention RCA](../charness-artifacts/debug/2026-07-20-debug-review.md) · [basetemp deletion-race RCA](../charness-artifacts/debug/2026-07-20-standing-pytest-basetemp-deletion-race.md)
- [release state](../charness-artifacts/release/latest.md) · [quality review](../charness-artifacts/quality/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
