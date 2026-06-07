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
  surfaces; 4-field declaration + paired consumer line). Closeout:
  [critique](../charness-artifacts/critique/2026-06-07-issue-322-advisory-interpretation-rollout.md).
- **#328 CLOSED** (preflight-gate-phase-coverage goal): landed a prose-pin
  pre-check (advisory, wired into slice closeout), a one-shot authoring-preflight
  (`--run-checks` now runs the full portable-package gate set) with a closeout
  ADVISORY pointer, and a dedicated `python-scan-hygiene` surface that pulls the
  gitignore-scan-hygiene gate into slice closeout (retro-lesson-index was already
  reachable).
  [Critique](../charness-artifacts/critique/2026-06-07-issue-328-preflight-gate-phase-coverage.md).
  #328 had been accidentally auto-closed by a stray close keyword in `12e9d54b`;
  reopened and resolved for real.
- **#331 CLOSED** (same family): reconciled the closeout matcher idiom
  manifest-wide to `<dir>/*.md|py` (fnmatch `*` crosses `/`); the bare
  `<dir>/**/*.X` matched zero top-level scripts and let a top-level packaging
  README slip the markdown gate.
  [Critique](../charness-artifacts/critique/2026-06-07-issue-331-closeout-fnmatch-idiom.md).
- **#327 triaged, not re-pointed:** mutation *score* passes (88.9%/91.9% vs 80%);
  CI FAILs are the intermittent changed-line selection-budget signal on
  *scheduled* main runs — low-severity, non-blocking.
- Open issues: **#330** (meta-validator, #322 follow-up), **#329** (retro
  disposition floor), **#327** (scheduled mutation signal), **#184** (product
  metrics).

## Next Session

- **Shaped achieve goal ready (pursue-ready):**
  [330-metavalidator-gate-hardening](../charness-artifacts/goals/2026-06-07-330-metavalidator-gate-hardening.md)
  — `/goal @charness-artifacts/goals/2026-06-07-330-metavalidator-gate-hardening.md`.
  Primary #330 (advisory-interpretation meta-validator); bundles the #331
  surface-idiom lint; re-points to #329 / #184 in its Discuss section.
- **Human real-host smoke for v0.27.0 (release left it open).** `charness update`
  on a clean temp-home / second machine + the nose tool-doctor/install/sync
  checklist in [release latest](../charness-artifacts/release/latest.md). Cannot
  be done by the agent; confirm before treating the v0.27.0 operator surface as
  proven.

## Discuss

- **No push/tag CI.** The local `--release` gate is the bundle proof (just
  exercised for v0.25.0). Worth deciding whether to add light push/tag CI, and
  whether to mirror the changed-line gate into a CI-PR check (spec
  "Deferred Decisions").

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; Slice 2 delivered, freshness identity, portability follow-up),
  [release v0.25.0 critique](../charness-artifacts/critique/2026-06-07-release-v0-25-0.md)
- [nose-clone interpretation (#322)](../charness-artifacts/quality/2026-06-06-nose-clone-interpretation.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md)
