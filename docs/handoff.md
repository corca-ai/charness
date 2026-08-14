# Charness Handoff

## Workflow Trigger

- Run `python3 scripts/open_lesson_session.py --repo-root . --session-id <date-slug> --seed <same>`
  BEFORE any brief or reviewer spawn. Both flags are REQUIRED.
- Then commit the verified tree (item 1 below), and invoke `release`: the prepared
  publish is no longer blocked.

## Continuation Capability

- [Migration retro](../charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md)
  — what the `--json` removal cost, the four false-completeness claims and their one
  cause, and the two recurrences it scored.
- [Residual-flags debug](../charness-artifacts/debug/2026-07-18-residual-json-flags-after-yaml-migration.md)
  — why `--json` survived July as a deliberate hidden compatibility parser.
- [Release notes](../charness-artifacts/release/2026-08-14-v6.0.0-notes.md)
  — breaking changes, migration cost, and known-weak surfaces a consumer inherits.
- [Recent lessons](../charness-artifacts/retro/recent-lessons.md)
  — the digest a session reads before work.

## Current State

- Nothing is committed, pushed, tagged, released, or closed; the whole slice is a
  dirty worktree. Count it with `git status --porcelain | wc -l`.
- `--json` is gone repo-wide and command output is unconditionally YAML, held by a
  gate that also scans the mirror and the extension-less root CLI. Prove with
  `python3 -m pytest tests/quality_gates/test_public_skill_yaml_output_contract.py -q`.
- Full suite green. Prove with `python3 -m pytest tests/ -q --no-header`.
- Dup ratchet clean after classifying 89 families; six were real duplications and were
  fixed, not labelled. Prove with
  `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --summary`.
- The release is still PREPARED — no bump, tag, or publish, and every version surface
  reads the shipped one. Confirm with
  `python3 skills/public/release/scripts/current_release.py --repo-root .`.
- [#618](https://github.com/corca-ai/charness/issues/618)-[#632](https://github.com/corca-ai/charness/issues/632):
  fifteen verified this session. Eight are fixed in-repo but still reproduce for their
  reporter because nothing installable has changed; three are still broken
  ([#628](https://github.com/corca-ai/charness/issues/628),
  [#629](https://github.com/corca-ai/charness/issues/629),
  [#631](https://github.com/corca-ai/charness/issues/631)); four are partly valid.

Non-claims: no commit, push, tag, version bump, publish, hosted CI, installed-consumer
readback, or issue closure. Round-2 repairs are accepted-unreviewed under the two-round
cap, and the reviewer-boundary verify failed on mid-window parent edits.

## Next Session

1. Commit the verified tree, then publish via `release`; its ordering and the publish
   floor live in [the release skill](../skills/public/release/SKILL.md). Re-verify first
   with `python3 -m pytest tests/ -q --no-header`.
2. Close [#618](https://github.com/corca-ai/charness/issues/618)-[#627](https://github.com/corca-ai/charness/issues/627)
   with a `Closes #N` carrier plus the classification ledger, then
   `verify-closeout --expect-state CLOSED`. Closability now depends on the publish, not
   on more repair — eight fixes are unreleased.
   [#626](https://github.com/corca-ai/charness/issues/626)/[#627](https://github.com/corca-ai/charness/issues/627)
   still need the scope decision their titles outrun.
3. **Drive `link_only_lines` to 0 and make the gate hold it there.** Fix
   [#629](https://github.com/corca-ai/charness/issues/629) at the
   [scaffold](../skills/public/handoff/scripts/scaffold_handoff_artifact.py), then clear
   this repo's own count — now **255**, not the 196 recorded before. Assert the count the
   gate already parses; `scripts/check_docs_graph.py:12-18` still reads only
   `orphans`/`islands`.
4. **Repair the lesson score signal.** Measured this session, not predicted: two lessons
   demonstrably worked and could not be recorded, because scoring requires the cited retro
   to recurrence-tag the lesson — crediting success means declaring recurrence. Design is
   written: [score outcome vocabulary](../charness-artifacts/spec/2026-08-14-lesson-score-outcome-vocabulary.md).
5. Make four recorded probe `_provenance` commands runnable again; they exit 2 on
   `--json`. One is SHA256-pinned, so the repair is a three-place edit. Find them with
   `grep -rn -- '--json' charness-artifacts/probe/`.

## Discuss

- Enforce the no-mutating-git rule for WRITE-CAPABLE subagents, not only bounded
  reviewers. One `git stash` reverted every agent's in-flight work this session and only
  recovery luck saved it; the incident and its blast radius are recorded in the
  [migration retro](../charness-artifacts/retro/2026-08-15-json-to-yaml-migration-closeout.md).
- Whether to extract the ledger write transaction shared by four writers; see
  [dup-review](../charness-artifacts/quality/dup-review.json) family `d3fea2dbc2463d22`.

## References

- [Design north star](./design-north-star.md) — the P4 rule this session leaned on hardest:
  every correction came from a different observer, none from re-reading my own work.
- [Operating contract](./conventions/operating-contract.md) — the closeout, critique-round,
  and external-boundary floors every item above is measured by.
- [Parallel execution](./conventions/parallel-execution.md) — the disjoint-writer rule the
  `git stash` incident tested.
