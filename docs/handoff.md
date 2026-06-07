# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.27.0 shipped** (tag `v0.27.0`, release verified; tree clean, `origin/main`
  even). Bundled #322, the #325 provenance policy + portable standing-doc check,
  and the handoff-3 changed-line gate — all additive/opt-in.
- **#322 CLOSED** (advisory-interpretation contract on six inference-layer
  surfaces; now enforced by #330's meta-validator).
- **#328 CLOSED** (preflight-gate-phase-coverage): prose-pin pre-check,
  one-shot authoring-preflight (`--run-checks` runs the full portable-package gate
  set), and a `python-scan-hygiene` slice-closeout surface.
  [Critique](../charness-artifacts/critique/2026-06-07-issue-328-preflight-gate-phase-coverage.md).
- **#331 CLOSED** (same family): reconciled the closeout matcher idiom
  manifest-wide to the `<dir>/*.md|py` form (fnmatch `*` crosses `/`); the bare
  `**/*.X` missed top-level files and let a packaging README slip the markdown gate.
  [Critique](../charness-artifacts/critique/2026-06-07-issue-331-closeout-fnmatch-idiom.md).
- **#330 CLOSED** (advisory-interpretation meta-validator, #322 sequel): a
  registry + `validate-inference-interpretation` gate assert each inference-layer
  surface (8: 7 python + 1 prose) emits the 4-field declaration + paired consumer
  line and fail closed on any unregistered declaration. Bundled the #331-deferred
  surface-idiom lint. Standing gate + slice-closeout surface. Closeout:
  [critique](../charness-artifacts/critique/2026-06-07-issue-330-metavalidator-gate-hardening.md),
  [retro](../charness-artifacts/retro/2026-06-07-issue-330-metavalidator-gate-hardening.md).
- **#327 triaged, not re-pointed:** mutation *score* passes (88.9%/91.9% vs 80%);
  CI FAILs are the intermittent changed-line selection-budget signal on
  *scheduled* main runs — low-severity, non-blocking.
- Open issues: **#329** (retro disposition floor), **#327** (scheduled mutation
  signal), **#184** (product metrics).

## Next Session

- **#330 complete** (goal
  [330-metavalidator-gate-hardening](../charness-artifacts/goals/2026-06-07-330-metavalidator-gate-hardening.md)
  is `Status: complete`). Remaining open-issue candidates: **#329** (retro
  disposition floor — small tooling hardening; hit again this session, the floor
  accepted the prose-only dispositions it should scrutinize), **#184** (product
  metrics — needs ideation/spec, not a quick slice). Either is a fresh `/goal` or
  `issue` pickup.
- **Human real-host smoke for v0.27.0 (release left it open).** `charness update`
  on a clean temp-home / second machine + the nose tool-doctor/install/sync
  checklist in [release latest](../charness-artifacts/release/latest.md). Cannot
  be done by the agent; confirm before treating the v0.27.0 operator surface as
  proven.

## Discuss

- **No push/tag CI.** The local `--release` gate is the bundle proof. Open: add
  light push/tag CI and/or mirror the changed-line gate into a CI-PR check (spec
  "Deferred Decisions").

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; Slice 2 delivered, freshness identity, portability follow-up),
  [release v0.25.0 critique](../charness-artifacts/critique/2026-06-07-release-v0-25-0.md)
- [nose-clone interpretation (#322)](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
